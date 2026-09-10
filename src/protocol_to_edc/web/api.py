"""Web API.

A thin layer over `core.orchestrator.execute` -- the same function the CLI calls.
The browser gets live progress because the orchestrator reports through an event
callback, which this module forwards over Server-Sent Events.

Nothing here knows the names of the eight domains. `/api/domains` reports
whatever the registry finds, and the UI renders the toggles from that, so a ninth
domain appears in the browser without a line changing in this file or in the
JavaScript.
"""

from __future__ import annotations

import asyncio
import json
import shutil
from pathlib import Path
from typing import Any

from fastapi import FastAPI, HTTPException, UploadFile
from fastapi.responses import FileResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

from ..core import config, orchestrator, paths, registry
from ..usdm import schema

UI_DIR = Path(__file__).resolve().parents[3] / "web" / "ui"

app = FastAPI(title="Protocol to USDM", version="0.1.0")

# Runs are kept in memory: this is a local single-operator tool, and a run's
# durable output is the files it writes into the study folder.
_RUNS: dict[str, dict[str, Any]] = {}
_RUN_SEQ = 0


class RunRequest(BaseModel):
    study_id: str
    usdm_version: str | None = None
    output_mode: str | None = None
    model: str | None = None
    effort: str | None = None
    domains: list[str] | None = Field(
        default=None, description="Domains to enable; all others are disabled."
    )
    use_cache: bool = True


def _overrides(request: RunRequest) -> dict[str, Any]:
    overrides: dict[str, Any] = {}
    if request.usdm_version:
        overrides.setdefault("usdm", {})["version"] = request.usdm_version
    if request.output_mode:
        overrides.setdefault("usdm", {})["output_mode"] = request.output_mode
    if request.model:
        overrides.setdefault("llm", {})["model"] = request.model
    if request.effort:
        overrides.setdefault("llm", {})["effort"] = request.effort
    if not request.use_cache:
        overrides.setdefault("llm", {})["reuse_cached_runs"] = False
    if request.domains is not None:
        known = {s.id for s in registry.load_all()}
        overrides["domains"] = {
            d: {"enabled": d in set(request.domains)} for d in known
        }
    return overrides


# -- configuration endpoints ----------------------------------------------


@app.get("/api/domains")
def list_domains() -> dict[str, Any]:
    specs = registry.load_all()
    return {
        "domains": [
            {
                "id": s.id,
                "order": s.order,
                "label": s.label,
                "description": s.description,
                "produces": list(s.produces),
                "attachesTo": s.attaches_to,
                "dependsOn": list(s.depends_on),
                "codelists": list(s.ct_codelists),
            }
            for s in specs
        ],
        "levels": registry.execution_levels(),
    }


@app.get("/api/usdm-versions")
def list_versions() -> dict[str, Any]:
    versions = paths.available_usdm_versions()
    return {
        "versions": [
            {"version": v, "entities": len(schema.load(v).entity_names())} for v in versions
        ],
        "default": versions[0] if versions else None,
    }


@app.get("/api/studies")
def list_studies() -> dict[str, Any]:
    studies = []
    for study_id in paths.list_studies():
        entry: dict[str, Any] = {"id": study_id}
        try:
            settings = config.load(study_id)
            entry.update(
                {
                    "title": settings.study.title,
                    "sponsor": settings.study.sponsor,
                    "phase": settings.study.phase,
                    "protocolPdf": settings.input.protocol_pdf,
                    "usdmVersion": settings.usdm.version,
                    "outputMode": settings.usdm.output_mode,
                    "enabledDomains": settings.enabled_domains(),
                    "ready": settings.paths.resolve_input(
                        settings.input.protocol_pdf
                    ).is_file()
                    if settings.input.protocol_pdf
                    else False,
                    "hasOutput": settings.paths.usdm_document.is_file(),
                }
            )
        except config.ConfigError as exc:
            entry["error"] = str(exc).splitlines()[0]
            entry["ready"] = False
        studies.append(entry)
    return {"studies": studies}


@app.post("/api/studies")
def create_study(study_id: str) -> dict[str, Any]:
    try:
        paths.validate_study_id(study_id)
    except paths.StudyIdError as exc:
        raise HTTPException(400, str(exc)) from exc
    target = paths.for_study(study_id)
    if target.root.exists():
        raise HTTPException(409, f"Study {study_id} already exists")
    shutil.copytree(paths.STUDY_TEMPLATE, target.root)
    target.ensure_dirs()
    cfg = target.config_file
    cfg.write_text(
        cfg.read_text(encoding="utf-8").replace(
            'id: "STUDY-ID-HERE"', f'id: "{study_id}"'
        ),
        encoding="utf-8",
    )
    return {"id": study_id, "path": str(target.root)}


@app.post("/api/studies/{study_id}/protocol")
async def upload_protocol(study_id: str, file: UploadFile) -> dict[str, Any]:
    study_paths = paths.for_study(study_id)
    if not study_paths.root.is_dir():
        raise HTTPException(404, f"No study {study_id}")
    if not (file.filename or "").lower().endswith(".pdf"):
        raise HTTPException(400, "The protocol must be a PDF")

    study_paths.ensure_dirs()
    target = study_paths.protocol_dir / Path(file.filename).name
    target.write_bytes(await file.read())

    # Point the study config at what was just uploaded.
    cfg = study_paths.config_file
    if cfg.is_file():
        lines = []
        for line in cfg.read_text(encoding="utf-8").splitlines():
            if line.strip().startswith("protocol_pdf:"):
                indent = line[: len(line) - len(line.lstrip())]
                line = f'{indent}protocol_pdf: "input/protocol/{target.name}"'
            lines.append(line)
        cfg.write_text("\n".join(lines) + "\n", encoding="utf-8")

    from ..pdf.extract import ProtocolText

    protocol = ProtocolText.load(target)
    return {
        "filename": target.name,
        "pages": len(protocol),
        "characters": protocol.character_count,
        "hasTextLayer": protocol.has_text_layer,
    }


@app.get("/api/studies/{study_id}/config")
def get_study_config(study_id: str) -> dict[str, Any]:
    try:
        settings = config.load(study_id)
    except config.ConfigError as exc:
        raise HTTPException(400, str(exc)) from exc
    return {
        "id": study_id,
        "study": settings.study.model_dump(),
        "usdm": settings.usdm.model_dump(by_alias=True),
        "llm": settings.llm.model_dump(),
        "qc": settings.qc.model_dump(),
        "domains": {d: t.model_dump() for d, t in settings.domains.items()},
    }


# -- running ---------------------------------------------------------------


@app.post("/api/runs")
async def start_run(request: RunRequest) -> dict[str, Any]:
    global _RUN_SEQ
    _RUN_SEQ += 1
    run_id = f"run-{_RUN_SEQ:04d}"
    queue: asyncio.Queue[dict[str, Any] | None] = asyncio.Queue()
    loop = asyncio.get_running_loop()

    state: dict[str, Any] = {
        "id": run_id,
        "study": request.study_id,
        "status": "running",
        "queue": queue,
        "events": [],
        "result": None,
        "error": None,
    }
    _RUNS[run_id] = state

    def on_event(event: orchestrator.RunEvent) -> None:
        payload = event.as_dict()
        state["events"].append(payload)
        loop.call_soon_threadsafe(queue.put_nowait, payload)

    async def runner() -> None:
        try:
            result = await orchestrator.execute(
                request.study_id, overrides=_overrides(request), on_event=on_event
            )
            state["result"] = result.as_dict()
            state["status"] = "done" if result.ok else "failed"
        except Exception as exc:  # surfaced to the browser rather than swallowed
            state["error"] = str(exc)
            state["status"] = "error"
            await queue.put(
                {"type": "run.error", "message": str(exc), "domain": "", "data": {}}
            )
        finally:
            await queue.put(None)

    state["task"] = asyncio.create_task(runner())
    return {"runId": run_id, "study": request.study_id}


@app.get("/api/runs/{run_id}/events")
async def run_events(run_id: str) -> StreamingResponse:
    state = _RUNS.get(run_id)
    if state is None:
        raise HTTPException(404, f"No run {run_id}")

    async def stream():
        for event in list(state["events"]):
            yield f"data: {json.dumps(event, ensure_ascii=False)}\n\n"
        while True:
            event = await state["queue"].get()
            if event is None:
                final = {
                    "type": "stream.end",
                    "message": state["status"],
                    "domain": "",
                    "data": state.get("result") or {},
                }
                yield f"data: {json.dumps(final, ensure_ascii=False)}\n\n"
                return
            yield f"data: {json.dumps(event, ensure_ascii=False)}\n\n"

    return StreamingResponse(
        stream(),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )


@app.get("/api/runs/{run_id}")
def run_status(run_id: str) -> dict[str, Any]:
    state = _RUNS.get(run_id)
    if state is None:
        raise HTTPException(404, f"No run {run_id}")
    return {
        "id": run_id,
        "study": state["study"],
        "status": state["status"],
        "error": state["error"],
        "result": state["result"],
        "events": state["events"],
    }


# -- outputs ---------------------------------------------------------------


@app.get("/api/studies/{study_id}/output/{name}")
def get_output(study_id: str, name: str) -> Any:
    study_paths = paths.for_study(study_id)
    targets = {
        "usdm": study_paths.usdm_document,
        "gap": study_paths.report("gap_report.md"),
        "validation": study_paths.report("validation_report.json"),
        "provenance": study_paths.report("provenance.csv"),
        "summary": study_paths.report("run_summary.json"),
    }
    path = targets.get(name)
    if path is None:
        raise HTTPException(404, f"Unknown output {name!r}")
    if not path.is_file():
        raise HTTPException(404, f"{path.name} has not been produced yet")
    if name in {"usdm", "validation", "summary"}:
        return json.loads(path.read_text(encoding="utf-8"))
    return FileResponse(path, media_type="text/plain; charset=utf-8")


@app.get("/api/studies/{study_id}/fragments")
def get_fragments(study_id: str) -> dict[str, Any]:
    directory = paths.for_study(study_id).fragments_dir
    if not directory.is_dir():
        return {"fragments": []}
    fragments = []
    for path in sorted(directory.glob("*.json")):
        try:
            fragments.append(json.loads(path.read_text(encoding="utf-8")))
        except ValueError:
            continue
    return {"fragments": fragments}


if UI_DIR.is_dir():
    app.mount("/", StaticFiles(directory=str(UI_DIR), html=True), name="ui")
