"""Command line interface.

    pte studies                          list studies
    pte domains                          list domain agents
    pte new <STUDY_ID>                   scaffold a study folder
    pte check <STUDY_ID>                 validate setup without calling the API
    pte build <STUDY_ID> [options]       run the pipeline
    pte web                              start the web UI

`build` is the same code path the web UI uses; neither is a reimplementation of
the other.
"""

from __future__ import annotations

import argparse
import asyncio
import json
import shutil
import sys
from typing import Any

from .core import config, orchestrator, paths, registry
from .core.console import setup_console


def _fmt_bool(value: bool) -> str:
    return "yes" if value else "no"


def cmd_studies(_: argparse.Namespace) -> int:
    studies = paths.list_studies()
    if not studies:
        print(f"No studies yet. Create one with:  pte new <STUDY_ID>")
        print(f"Studies live in {paths.STUDIES}")
        return 0
    print(f"{'STUDY':28} {'PROTOCOL PDF':44} CONFIG")
    for study_id in studies:
        try:
            settings = config.load(study_id)
            pdf = settings.input.protocol_pdf.rsplit("/", 1)[-1] or "-"
            state = "ok"
        except config.ConfigError as exc:
            pdf, state = "-", f"error: {str(exc).splitlines()[0][:40]}"
        print(f"{study_id:28} {pdf:44} {state}")
    return 0


def cmd_domains(args: argparse.Namespace) -> int:
    specs = registry.load_all()
    levels = registry.execution_levels()
    print(f"{len(specs)} domain agents, running over {len(levels)} level(s)\n")
    print(f"{'#':<3} {'ID':24} {'LABEL':34} ATTACHES TO")
    for spec in specs:
        print(f"{spec.order:<3} {spec.id:24} {spec.label:34} {spec.attaches_to}")
    print()
    for index, level in enumerate(levels, start=1):
        print(f"  level {index} (concurrent): {', '.join(level)}")
    if args.verbose:
        for spec in specs:
            print(f"\n--- {spec.id} ---")
            print(f"  produces      : {', '.join(spec.produces)}")
            print(f"  depends on    : {', '.join(spec.depends_on) or '-'}")
            print(f"  IG sections   : {', '.join(spec.ig_sections)}")
            print(f"  codelists     : {', '.join(spec.ct_codelists) or '-'}")
            print(f"  skill         : {spec.skill_path().name} "
                  f"({len(spec.load_skill()):,} chars)")
    return 0


def cmd_new(args: argparse.Namespace) -> int:
    try:
        paths.validate_study_id(args.study_id)
    except paths.StudyIdError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2

    target = paths.for_study(args.study_id)
    if target.root.exists():
        print(f"error: {target.root} already exists", file=sys.stderr)
        return 2

    shutil.copytree(paths.STUDY_TEMPLATE, target.root)
    target.ensure_dirs()
    config_file = target.config_file
    text = config_file.read_text(encoding="utf-8").replace(
        'id: "STUDY-ID-HERE"', f'id: "{args.study_id}"'
    )
    config_file.write_text(text, encoding="utf-8")

    print(f"created {target.root}")
    print(f"  1. put the protocol PDF in {target.protocol_dir}")
    print(f"  2. point `input.protocol_pdf` at it in {config_file.name}")
    print(f"  3. pte check {args.study_id}")
    return 0


def cmd_check(args: argparse.Namespace) -> int:
    """Everything that can be verified without spending a token."""
    from .pdf.extract import ProtocolText
    from .usdm import ct, schema

    problems: list[str] = []

    try:
        settings = config.load(args.study_id)
    except config.ConfigError as exc:
        print(f"config          FAIL  {exc}")
        return 1
    print(f"config          ok    {len(settings.enabled_domains())}/8 domains enabled, "
          f"output mode {settings.usdm.output_mode}")

    try:
        config.load_api_key()
        print("api key         ok    ANTHROPIC_API_KEY is set")
    except config.ConfigError as exc:
        problems.append(str(exc))
        print("api key         FAIL  not set")

    try:
        usdm = schema.load(settings.usdm.version)
        print(f"usdm schema     ok    v{usdm.api_version}, {len(usdm.entity_names())} entities")
    except Exception as exc:
        problems.append(str(exc))
        print(f"usdm schema     FAIL  {exc}")

    try:
        terminology = ct.load(settings.usdm.version)
        print(f"terminology     ok    {len(terminology.keys())} codelists")
    except Exception as exc:
        problems.append(str(exc))
        print(f"terminology     FAIL  {exc}")

    sections = list(paths.USDM_IG_SECTIONS.glob("*.md"))
    if sections:
        print(f"ig excerpts     ok    {len(sections)} entity excerpts")
    else:
        print("ig excerpts     WARN  none; run python -m protocol_to_edc.usdm.slice_ig")

    try:
        protocol_path = settings.protocol_path()
        protocol = ProtocolText.load(protocol_path)
        state = "ok  " if protocol.has_text_layer else "FAIL"
        print(
            f"protocol        {state}  {protocol_path.name}: {len(protocol)} pages, "
            f"{protocol.character_count:,} chars, text layer "
            f"{_fmt_bool(protocol.has_text_layer)}"
        )
        if not protocol.has_text_layer:
            problems.append("protocol PDF has no usable text layer (OCR is out of scope)")
    except Exception as exc:
        problems.append(str(exc))
        print(f"protocol        FAIL  {exc}")

    try:
        specs = registry.load_all()
        for spec in specs:
            spec.module()
        print(f"domains         ok    {len(specs)} manifests, all modules importable")
    except Exception as exc:
        problems.append(str(exc))
        print(f"domains         FAIL  {exc}")

    if problems:
        print(f"\n{len(problems)} problem(s) to fix before building.")
        return 1
    print(f"\nReady. Run:  pte build {args.study_id}")
    return 0


def _overrides_from(args: argparse.Namespace) -> dict[str, Any]:
    overrides: dict[str, Any] = {}
    if args.usdm_version:
        overrides.setdefault("usdm", {})["version"] = args.usdm_version
    if args.output_mode:
        overrides.setdefault("usdm", {})["output_mode"] = args.output_mode
    if args.model:
        overrides.setdefault("llm", {})["model"] = args.model
    if args.effort:
        overrides.setdefault("llm", {})["effort"] = args.effort
    if args.no_cache:
        overrides.setdefault("llm", {})["reuse_cached_runs"] = False

    if args.domains:
        wanted = {d.strip() for d in args.domains.split(",") if d.strip()}
        known = {s.id for s in registry.load_all()}
        unknown = wanted - known
        if unknown:
            raise SystemExit(
                f"error: unknown domain(s): {', '.join(sorted(unknown))}\n"
                f"known: {', '.join(sorted(known))}"
            )
        overrides["domains"] = {d: {"enabled": d in wanted} for d in known}
    return overrides


def cmd_build(args: argparse.Namespace) -> int:
    overrides = _overrides_from(args)

    def on_event(event: orchestrator.RunEvent) -> None:
        if args.json:
            print(json.dumps(event.as_dict(), ensure_ascii=False), flush=True)
            return
        prefix = {
            "run.start": "==>",
            "run.done": "==>",
            "level.start": "  -",
            "domain.start": "    .",
            "domain.done": "    +",
            "domain.error": "    !",
        }.get(event.type, "    .")
        print(f"{prefix} {event.message}", flush=True)

    try:
        result = asyncio.run(
            orchestrator.execute(
                args.study_id,
                overrides=overrides,
                on_event=on_event,
                refresh=[d.strip() for d in (args.refresh or "").split(",") if d.strip()],
            )
        )
    except config.ConfigError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2

    if not args.json:
        print()
        print(f"USDM document : {result.output_paths['usdm']}")
        print(f"Gap report    : {result.output_paths['gapReport']}")
        print(f"Provenance    : {result.output_paths['provenance']}")
        if result.validation and result.validation.errors:
            print(f"\n{len(result.validation.errors)} validation error(s) -- see the gap report.")
    return 0 if result.ok else 1


def cmd_web(args: argparse.Namespace) -> int:
    import uvicorn

    print(f"Web UI on http://{args.host}:{args.port}")
    uvicorn.run("protocol_to_edc.web.api:app", host=args.host, port=args.port, reload=args.reload)
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="pte", description="Protocol PDF -> USDM v4 study definition"
    )
    sub = parser.add_subparsers(dest="command", required=True)

    sub.add_parser("studies", help="list studies").set_defaults(func=cmd_studies)

    domains = sub.add_parser("domains", help="list domain agents")
    domains.add_argument("-v", "--verbose", action="store_true")
    domains.set_defaults(func=cmd_domains)

    new = sub.add_parser("new", help="scaffold a study folder")
    new.add_argument("study_id")
    new.set_defaults(func=cmd_new)

    check = sub.add_parser("check", help="verify setup without calling the API")
    check.add_argument("study_id")
    check.set_defaults(func=cmd_check)

    build = sub.add_parser("build", help="run the pipeline")
    build.add_argument("study_id")
    build.add_argument("--domains", help="comma-separated domains to run (others disabled)")
    build.add_argument("--usdm-version", help="override the USDM version")
    build.add_argument("--output-mode", choices=["partial", "strict", "stub"])
    build.add_argument("--model", help="override the model")
    build.add_argument("--effort", choices=["low", "medium", "high", "xhigh", "max"])
    build.add_argument("--refresh", help="comma-separated domains to re-run ignoring the cache")
    build.add_argument("--no-cache", action="store_true", help="ignore all cached responses")
    build.add_argument("--json", action="store_true", help="emit events as JSON lines")
    build.set_defaults(func=cmd_build)

    web = sub.add_parser("web", help="start the web UI")
    web.add_argument("--host", default="127.0.0.1")
    web.add_argument("--port", type=int, default=8000)
    web.add_argument("--reload", action="store_true")
    web.set_defaults(func=cmd_web)

    return parser


def main(argv: list[str] | None = None) -> int:
    setup_console()
    args = build_parser().parse_args(argv)
    return int(args.func(args))


if __name__ == "__main__":
    raise SystemExit(main())
