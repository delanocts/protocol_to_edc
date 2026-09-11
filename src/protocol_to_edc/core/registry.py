"""Domain discovery.

A domain is a manifest in `config/domains/` plus a package in
`src/protocol_to_edc/domains/` with the same id. Nothing else in the codebase
names a domain: the orchestrator asks the registry what exists, the web UI
renders whatever it is told, and the assembler places output wherever the
manifest says.

That is what makes the ninth domain a drop-in. Adding one means writing a
manifest and a package; no orchestrator, UI or config change.

A package must expose:

    PAYLOAD_MODEL   a pydantic model for one extracted entity
    build_prompt    (context) -> str, the domain-specific instruction
    to_usdm         (output, context) -> the USDM fragment for its anchor

The registry checks all three at load time, so a broken domain is reported by
name at start-up rather than failing mid-run.
"""

from __future__ import annotations

import importlib
from dataclasses import dataclass, field
from functools import cache
from pathlib import Path
from types import ModuleType
from typing import Any

import yaml

from . import paths

REQUIRED_ATTRIBUTES = ("PAYLOAD_MODEL", "build_prompt", "to_usdm")


class RegistryError(RuntimeError):
    """A domain that cannot be loaded as declared."""


@dataclass(frozen=True)
class DomainSpec:
    """Everything the pipeline knows about one domain."""

    id: str
    order: int
    label: str
    description: str
    produces: tuple[str, ...]
    attaches_to: str
    depends_on: tuple[str, ...]
    skill_file: str
    ig_sections: tuple[str, ...]
    ct_codelists: tuple[str, ...]
    protocol_hints: tuple[str, ...]
    version_range: str
    manifest_path: Path
    model_override: str | None = None
    effort_override: str | None = None
    extra: dict[str, Any] = field(default_factory=dict)

    @property
    def package(self) -> str:
        return f"protocol_to_edc.domains.{self.id}"

    @property
    def package_dir(self) -> Path:
        return paths.DOMAINS_PACKAGE_DIR / self.id

    @property
    def anchor(self) -> str:
        return self.attaches_to.partition(".")[0]

    def skill_path(self) -> Path:
        if self.skill_file:
            candidate = paths.PROJECT_ROOT / self.skill_file
            if candidate.is_file():
                return candidate
        return self.package_dir / "skill.md"

    def load_skill(self) -> str:
        path = self.skill_path()
        return path.read_text(encoding="utf-8") if path.is_file() else ""

    def module(self) -> ModuleType:
        try:
            module = importlib.import_module(f"{self.package}.domain")
        except ModuleNotFoundError as exc:
            raise RegistryError(
                f"Domain {self.id!r} has a manifest at {self.manifest_path.name} but no "
                f"module at {self.package_dir / 'domain.py'}"
            ) from exc
        missing = [a for a in REQUIRED_ATTRIBUTES if not hasattr(module, a)]
        if missing:
            raise RegistryError(
                f"Domain {self.id!r} module is missing {', '.join(missing)}. "
                f"Every domain must define {', '.join(REQUIRED_ATTRIBUTES)}."
            )
        return module


def _as_tuple(value: Any) -> tuple[str, ...]:
    if value is None:
        return ()
    if isinstance(value, str):
        return (value,)
    return tuple(str(v) for v in value)


def _parse_manifest(path: Path) -> DomainSpec:
    try:
        data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    except yaml.YAMLError as exc:
        raise RegistryError(f"{path.name} is not valid YAML: {exc}") from exc

    domain_id = str(data.get("id", "")).strip()
    if not domain_id:
        raise RegistryError(f"{path.name} does not declare an `id`")

    usdm = data.get("usdm") or {}
    attaches_to = str(usdm.get("attaches_to", "")).strip()
    if not attaches_to:
        raise RegistryError(f"{path.name} does not declare `usdm.attaches_to`")

    skill = data.get("skill") or {}
    llm = data.get("llm") or {}

    return DomainSpec(
        id=domain_id,
        order=int(data.get("order", 99)),
        label=str(data.get("label", domain_id)),
        description=str(data.get("description", "")),
        produces=_as_tuple(usdm.get("produces")),
        attaches_to=attaches_to,
        depends_on=_as_tuple(data.get("depends_on")),
        skill_file=str(skill.get("file", "")),
        ig_sections=_as_tuple(skill.get("ig_sections")),
        ct_codelists=_as_tuple(skill.get("ct_codelists")),
        protocol_hints=_as_tuple(data.get("protocol_hints")),
        version_range=str(usdm.get("version_range", "")),
        manifest_path=path,
        model_override=llm.get("model") or None,
        effort_override=llm.get("effort") or None,
        extra={
            k: v
            for k, v in data.items()
            if k
            not in {
                "id",
                "order",
                "label",
                "description",
                "usdm",
                "depends_on",
                "skill",
                "protocol_hints",
                "llm",
            }
        },
    )


@cache
def load_all() -> tuple[DomainSpec, ...]:
    """Every domain manifest on disk, in declared order.

    Cached for the life of the process, unlike `paths.list_studies()`. That is a
    deliberate difference: a study folder appears while the server is running, so
    caching it hides new studies, whereas a domain is code as well as a manifest
    and cannot take effect until its package is imported. Adding a ninth domain
    therefore needs a server restart, which adding a study does not.
    """
    directory = paths.DOMAIN_MANIFEST_DIR
    if not directory.is_dir():
        raise RegistryError(f"No domain manifest directory at {directory}")

    specs = [_parse_manifest(p) for p in sorted(directory.glob("*.yaml"))]
    seen: dict[str, Path] = {}
    for spec in specs:
        if spec.id in seen:
            raise RegistryError(
                f"Two manifests declare domain {spec.id!r}: "
                f"{seen[spec.id].name} and {spec.manifest_path.name}"
            )
        seen[spec.id] = spec.manifest_path

    known = {s.id for s in specs}
    for spec in specs:
        unknown = [d for d in spec.depends_on if d not in known]
        if unknown:
            raise RegistryError(
                f"Domain {spec.id!r} depends on unknown domain(s): {', '.join(unknown)}"
            )

    return tuple(sorted(specs, key=lambda s: (s.order, s.id)))


def get(domain_id: str) -> DomainSpec:
    for spec in load_all():
        if spec.id == domain_id:
            return spec
    known = ", ".join(s.id for s in load_all())
    raise RegistryError(f"Unknown domain {domain_id!r}. Known domains: {known}")


def execution_levels(domain_ids: list[str] | tuple[str, ...] | None = None) -> list[list[str]]:
    """Group domains into dependency levels; everything in a level can run at once.

    Dependencies on domains that are not in the selection are dropped rather than
    treated as blocking -- a disabled domain should not stop the rest of the run,
    it should show up later as a gap in the report.
    """
    specs = {s.id: s for s in load_all()}
    selected = list(domain_ids) if domain_ids is not None else list(specs)
    selected = [d for d in selected if d in specs]

    pending = {d: {p for p in specs[d].depends_on if p in selected} for d in selected}
    levels: list[list[str]] = []
    while pending:
        ready = sorted(d for d, deps in pending.items() if not deps)
        if not ready:
            cycle = ", ".join(sorted(pending))
            raise RegistryError(f"Circular dependency between domains: {cycle}")
        levels.append(ready)
        for domain in ready:
            pending.pop(domain)
        for deps in pending.values():
            deps.difference_update(ready)
    return levels
