"""Run the pipeline.

One function, `execute`, drives everything: it resolves configuration, uploads
the protocol, runs the enabled domain agents in dependency order, assembles their
fragments into a USDM document, validates it and writes the reports.

Both entry points call it -- the CLI directly, the web API through the same
function -- so there is exactly one implementation of what a run is. Progress is
reported through an event callback rather than printed, which is what lets the
same code back a terminal progress display and a browser's event stream.

Agents at the same dependency level run concurrently. That is not just for speed:
the first agent to reach the API writes the protocol into the prompt cache, and
the rest read it back at a fraction of the input cost.
"""

from __future__ import annotations

import asyncio
import json
import time
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Callable

import anthropic

from ..llm.cache import ResponseCache
from ..llm.call import Agent, LlmError, Usage
from ..llm.documents import DocumentStore, UploadedDocument
from ..llm.schemas import Gap
from ..pdf.extract import ProtocolText
from ..qc import gap_report, provenance
from ..usdm import assembler, ct, schema, validator
from ..usdm.assembler import Assembly
from . import config, paths, registry
from ..domains.base import DomainContext

EventCallback = Callable[["RunEvent"], None]


@dataclass
class RunEvent:
    """Something worth telling the caller about."""

    type: str  # run.start | domain.start | domain.done | domain.error | run.done ...
    message: str
    domain: str = ""
    data: dict[str, Any] = field(default_factory=dict)
    at: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat(timespec="seconds")
    )

    def as_dict(self) -> dict[str, Any]:
        return {
            "type": self.type,
            "message": self.message,
            "domain": self.domain,
            "data": self.data,
            "at": self.at,
        }


@dataclass
class DomainResult:
    domain_id: str
    label: str
    ok: bool
    usage: Usage
    from_cache: bool = False
    item_count: int = 0
    gaps: list[Gap] = field(default_factory=list)
    min_confidence: float = 1.0
    error: str = ""
    seconds: float = 0.0
    targets: list[str] = field(default_factory=list)

    def as_dict(self) -> dict[str, Any]:
        return {
            "domain": self.domain_id,
            "label": self.label,
            "ok": self.ok,
            "fromCache": self.from_cache,
            "items": self.item_count,
            "gaps": len(self.gaps),
            "minConfidence": round(self.min_confidence, 2),
            "seconds": round(self.seconds, 1),
            "targets": self.targets,
            "usage": self.usage.as_dict(),
            "error": self.error,
        }


@dataclass
class RunResult:
    study_id: str
    document: dict[str, Any] | None
    domains: list[DomainResult]
    usage: Usage
    validation: validator.ValidationReport | None
    assembly: assembler.AssemblyReport | None
    provenance_rows: list[provenance.ProvenanceRow]
    seconds: float
    output_paths: dict[str, str] = field(default_factory=dict)

    @property
    def ok(self) -> bool:
        return self.document is not None and all(d.ok for d in self.domains)

    def as_dict(self) -> dict[str, Any]:
        return {
            "study": self.study_id,
            "ok": self.ok,
            "seconds": round(self.seconds, 1),
            "usage": self.usage.as_dict(),
            "domains": [d.as_dict() for d in self.domains],
            "validation": self.validation.as_dict() if self.validation else None,
            "outputs": self.output_paths,
        }


def _noop(_: RunEvent) -> None:
    return None


async def _run_domain(
    spec: registry.DomainSpec,
    agent: Agent,
    ctx: DomainContext,
    settings: config.Settings,
    document: UploadedDocument | None,
    emit: EventCallback,
) -> tuple[DomainResult, Any]:
    """Run one domain agent and return its result plus the raw output object."""
    started = time.monotonic()
    emit(RunEvent("domain.start", f"{spec.label}: reading the protocol", spec.id))

    module = spec.module()
    output_model = module.OutputModel
    try:
        instruction = module.build_prompt(ctx)
        result = await agent.extract(
            domain_id=spec.id,
            model=settings.model_for(spec.id),
            effort=settings.effort_for(spec.id),
            system=ctx.system_prompt,
            instruction=instruction,
            output_model=output_model,
            document=document,
        )
    except LlmError as exc:
        elapsed = time.monotonic() - started
        emit(RunEvent("domain.error", str(exc), spec.id))
        return (
            DomainResult(spec.id, spec.label, False, Usage(), error=str(exc), seconds=elapsed),
            None,
        )

    elapsed = time.monotonic() - started
    output = result.data
    domain_result = DomainResult(
        domain_id=spec.id,
        label=spec.label,
        ok=True,
        usage=result.usage,
        from_cache=result.from_cache,
        item_count=len(output.items),
        gaps=list(output.gaps),
        min_confidence=output.confidence_floor(),
        seconds=elapsed,
    )
    emit(
        RunEvent(
            "domain.done",
            f"{spec.label}: {len(output.items)} item(s), {len(output.gaps)} gap(s)"
            + (" (cached)" if result.from_cache else ""),
            spec.id,
            domain_result.as_dict(),
        )
    )
    return domain_result, output


async def execute(
    study_id: str,
    *,
    overrides: dict[str, Any] | None = None,
    on_event: EventCallback | None = None,
    refresh: list[str] | None = None,
) -> RunResult:
    """Run the pipeline for one study."""
    emit = on_event or _noop
    started = time.monotonic()

    settings = config.load(study_id, overrides)
    study_paths = settings.paths
    study_paths.ensure_dirs()

    usdm_schema = schema.load(settings.usdm.version)
    terminology = ct.load(settings.usdm.version)
    protocol_path = settings.protocol_path()
    protocol = ProtocolText.load(protocol_path)

    if not protocol.has_text_layer:
        raise config.ConfigError(
            f"{protocol_path.name} has no usable text layer "
            f"({protocol.character_count:,} characters across {len(protocol)} pages). "
            "Scanned PDFs need OCR, which this pipeline does not do."
        )

    enabled = [s for s in registry.load_all() if settings.is_enabled(s.id)]
    levels = registry.execution_levels([s.id for s in enabled])
    emit(
        RunEvent(
            "run.start",
            f"{study_id}: {len(enabled)} domain(s) over {len(levels)} level(s), "
            f"protocol {protocol_path.name} ({len(protocol)} pages)",
            data={
                "study": study_id,
                "domains": [s.id for s in enabled],
                "levels": levels,
                "usdmVersion": usdm_schema.api_version,
                "outputMode": settings.usdm.output_mode,
                "model": settings.llm.model,
                "pages": len(protocol),
            },
        )
    )

    cache = ResponseCache(enabled=settings.llm.reuse_cached_runs)
    for domain_id in refresh or []:
        dropped = cache.clear(domain_id)
        if dropped:
            emit(RunEvent("cache.clear", f"dropped {dropped} cached response(s)", domain_id))

    client = anthropic.AsyncAnthropic(api_key=config.load_api_key())
    agent = Agent(client, cache=cache)

    store = DocumentStore(study_paths.work_dir)
    sync_client = anthropic.Anthropic(api_key=config.load_api_key())
    existing = store.lookup(protocol_path)
    document = store.ensure(sync_client, protocol_path)
    emit(
        RunEvent(
            "document.ready",
            f"protocol {'reused' if existing else 'uploaded'} as {document.file_id}",
            data={"fileId": document.file_id, "reused": bool(existing)},
        )
    )

    specs = {s.id: s for s in enabled}
    outputs: dict[str, Any] = {}
    results: list[DomainResult] = []
    total_usage = Usage()

    ig_cache: dict[str, str] = {}

    def ig_excerpt(spec: registry.DomainSpec) -> str:
        parts = []
        for name in spec.ig_sections:
            if name not in ig_cache:
                path = paths.USDM_IG_SECTIONS / f"{name}.md"
                ig_cache[name] = path.read_text(encoding="utf-8") if path.is_file() else ""
            if ig_cache[name]:
                parts.append(ig_cache[name])
        return "\n\n".join(parts)

    semaphore = asyncio.Semaphore(settings.llm.max_concurrency)

    async def guarded(spec: registry.DomainSpec):
        ctx = DomainContext(
            settings=settings,
            spec=spec,
            schema=usdm_schema,
            terminology=terminology,
            protocol=protocol,
            upstream=dict(outputs),
            ig_excerpt=ig_excerpt(spec),
        )
        async with semaphore:
            return await _run_domain(spec, agent, ctx, settings, document, emit)

    async def collect(pairs) -> None:
        for domain_result, output in pairs:
            results.append(domain_result)
            total_usage.add(domain_result.usage)
            if output is not None:
                outputs[domain_result.domain_id] = output

    cache_warmed = False
    for level_index, level in enumerate(levels, start=1):
        emit(
            RunEvent(
                "level.start",
                f"level {level_index}: {', '.join(level)}",
                data={"level": level_index, "domains": level},
            )
        )

        remaining = list(level)
        if not cache_warmed and settings.llm.cache_protocol and len(remaining) > 1:
            # The protocol is ~168,000 tokens and every agent sends it. Launched
            # together, all of them miss the prompt cache and each pays to write
            # it -- on this protocol that was 1.18M cache-write tokens for a 0%
            # hit rate. Running one agent first lets it populate the cache, so
            # the rest read the document back at a fraction of the price.
            first = remaining.pop(0)
            emit(
                RunEvent(
                    "cache.warm",
                    f"{specs[first].label} runs first to prime the protocol cache; "
                    f"the remaining {len(remaining)} then run concurrently",
                    first,
                )
            )
            await collect([await guarded(specs[first])])
            cache_warmed = True

        if remaining:
            await collect(await asyncio.gather(*(guarded(specs[d]) for d in remaining)))
        cache_warmed = True

    await client.close()

    # -- assemble ----------------------------------------------------------

    emit(RunEvent("assemble.start", "assembling the USDM document"))
    study_meta = settings.study
    assembly = Assembly(
        usdm_schema,
        study_name=study_meta.protocol_number or study_id,
        output_mode=settings.usdm.output_mode,
        version_identifier=study_meta.protocol_version or "1",
        rationale="",
    )

    for spec in enabled:
        output = outputs.get(spec.id)
        if output is None:
            continue
        module = spec.module()
        fragment = module.to_usdm(output, DomainContext(
            settings=settings,
            spec=spec,
            schema=usdm_schema,
            terminology=terminology,
            protocol=protocol,
            upstream=outputs,
        ))
        targets = sorted(fragment) if isinstance(fragment, dict) else []
        for target, payload in (fragment or {}).items():
            assembly.add(spec.id, target, payload)
        for result in results:
            if result.domain_id == spec.id:
                result.targets = targets
        study_paths.fragment(spec.id).write_text(
            json.dumps(
                {"domain": spec.id, "targets": targets, "fragment": fragment},
                indent=2,
                ensure_ascii=False,
            ),
            encoding="utf-8",
        )

    document_json = assembly.build()
    report = validator.validate(document_json, usdm_schema) if settings.usdm.validate_schema else None

    # -- reports -----------------------------------------------------------

    rows = provenance.verify_all(outputs, protocol)
    study_paths.usdm_document.write_text(
        json.dumps(document_json, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    provenance.write_csv(rows, study_paths.report("provenance.csv"))
    gap_report.write(
        study_paths.report("gap_report.md"),
        study_id=study_id,
        settings=settings,
        results=results,
        assembly=assembly.report,
        validation=report,
        provenance_rows=rows,
    )
    if report is not None:
        study_paths.report("validation_report.json").write_text(
            json.dumps(report.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8"
        )

    elapsed = time.monotonic() - started
    run_result = RunResult(
        study_id=study_id,
        document=document_json,
        domains=results,
        usage=total_usage,
        validation=report,
        assembly=assembly.report,
        provenance_rows=rows,
        seconds=elapsed,
        output_paths={
            "usdm": str(study_paths.usdm_document),
            "gapReport": str(study_paths.report("gap_report.md")),
            "provenance": str(study_paths.report("provenance.csv")),
            "validation": str(study_paths.report("validation_report.json")),
            "fragments": str(study_paths.fragments_dir),
        },
    )
    study_paths.report("run_summary.json").write_text(
        json.dumps(run_result.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8"
    )

    emit(
        RunEvent(
            "run.done",
            (
                f"{study_id}: "
                + (report.summary() if report else "validation skipped")
                + f"; {total_usage.summary()}"
            ),
            data=run_result.as_dict(),
        )
    )
    return run_result
