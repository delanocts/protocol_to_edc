"""Assemble domain fragments into one USDM document.

Each domain agent produces a fragment aimed at an anchor:

    study         -- the Study wrapper
    studyVersion  -- the StudyVersion (titles, identifiers, interventions, ...)
    studyDesign   -- the study design (arms, epochs, objectives, activities, ...)

A manifest says where its domain's output goes, e.g. `studyDesign.epochs`. This
module owns the skeleton those anchors hang from, merges fragments into it,
derives the join entities, and mints ids.

Output modes decide what happens when an enabled-and-required part is missing --
which is routine here, because turning off a domain agent removes properties that
`InterventionalStudyDesign` marks required:

    partial  emit what exists; report what is missing (the default)
    strict   refuse to assemble; the caller is asking for a conformant document
    stub     insert a minimal placeholder object so the document validates, and
             list every stub in the gap report
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Literal

from . import ids, joins
from .schema import UsdmSchema

Anchor = Literal["study", "studyVersion", "studyDesign"]
ANCHORS: tuple[Anchor, ...] = ("study", "studyVersion", "studyDesign")

INTERVENTIONAL = "InterventionalStudyDesign"
OBSERVATIONAL = "ObservationalStudyDesign"


class AssemblyError(ValueError):
    """The document cannot be assembled as configured."""


@dataclass
class MissingRequirement:
    entity: str
    property: str
    anchor: str
    reason: str
    stubbed: bool = False


@dataclass
class AssemblyReport:
    """What assembly did and could not do. Feeds the gap report."""

    missing: list[MissingRequirement] = field(default_factory=list)
    notes: list[str] = field(default_factory=list)
    resolution: ids.Resolution | None = None
    fragments: dict[str, str] = field(default_factory=dict)

    @property
    def dangling(self) -> dict[str, list[str]]:
        return self.resolution.dangling if self.resolution else {}

    def summary(self) -> str:
        parts = [f"{len(self.fragments)} fragments"]
        if self.resolution:
            parts.append(self.resolution.summary())
        if self.missing:
            stubbed = sum(1 for m in self.missing if m.stubbed)
            parts.append(f"{len(self.missing)} required properties missing ({stubbed} stubbed)")
        return "; ".join(parts)


STUB_TEXT = "Not stated in the protocol"


def _stub_entity(schema: UsdmSchema, entity: str, key: str, depth: int = 2) -> dict[str, Any]:
    """A minimal object of `entity` that satisfies its own required properties.

    Recursive, because a shallow stub is not enough: stubbing a study design's
    `population` with `{id, name, instanceType}` still fails validation, since
    `StudyDesignPopulation` itself requires `includesHealthySubjects`.
    """
    if entity == "Code":
        return {
            "code": "UNKNOWN",
            "codeSystem": "SPONSOR",
            "codeSystemVersion": "1",
            "decode": STUB_TEXT,
            "instanceType": "Code",
        }

    node: dict[str, Any] = {
        "id": ids.placeholder(entity, f"stub-{key}"),
        "instanceType": entity,
    }
    entity_schema = schema.entity(entity)
    for prop in sorted(entity_schema.required):
        if prop in node:
            continue
        node[prop] = _stub_value(schema, entity, prop, f"{key}-{prop}", depth - 1)
    return node


def _stub_value(schema: UsdmSchema, entity: str, prop: str, key: str, depth: int = 2) -> Any:
    """The smallest value that satisfies a required property's declared type."""
    spec = schema.entity(entity).property(prop)
    if spec.is_array:
        return []
    if spec.ref_entity:
        if depth <= 0:
            return {
                "id": ids.placeholder(spec.ref_entity, f"stub-{key}"),
                "instanceType": spec.ref_entity,
            }
        return _stub_entity(schema, spec.ref_entity, key, depth)
    if spec.type_name == "boolean":
        return False
    if spec.type_name in {"integer", "number"}:
        return 0
    return STUB_TEXT


class Assembly:
    """Collects fragments, then builds the document."""

    def __init__(
        self,
        schema: UsdmSchema,
        *,
        study_name: str,
        design_type: str = INTERVENTIONAL,
        output_mode: str = "partial",
        version_identifier: str = "1",
        rationale: str = "",
    ) -> None:
        if design_type not in {INTERVENTIONAL, OBSERVATIONAL}:
            raise AssemblyError(f"Unknown study design type {design_type!r}")
        self.schema = schema
        self.study_name = study_name
        self.design_type = design_type
        self.output_mode = output_mode
        self.version_identifier = version_identifier
        self.rationale = rationale or "Not stated in the protocol."
        self._fragments: list[tuple[str, str, str, Any]] = []
        self.report = AssemblyReport()

    # -- collecting --------------------------------------------------------

    def add(self, domain_id: str, target: str, payload: Any) -> None:
        """Add one domain's output at `anchor.property` (e.g. `studyDesign.epochs`)."""
        anchor, _, prop = target.partition(".")
        if anchor not in ANCHORS:
            raise AssemblyError(
                f"{domain_id}: target {target!r} must start with one of {', '.join(ANCHORS)}"
            )
        if not prop:
            raise AssemblyError(f"{domain_id}: target {target!r} names no property")
        if payload is None:
            return
        self._fragments.append((domain_id, anchor, prop, payload))
        self.report.fragments[domain_id] = target

    # -- building ----------------------------------------------------------

    def _skeleton(self) -> tuple[dict[str, Any], dict[str, Any], dict[str, Any]]:
        design: dict[str, Any] = {
            "id": ids.placeholder(self.design_type, "main"),
            "name": "Study Design",
            "instanceType": self.design_type,
        }
        version: dict[str, Any] = {
            "id": ids.placeholder("StudyVersion", self.version_identifier),
            "versionIdentifier": self.version_identifier,
            "rationale": self.rationale,
            "studyDesigns": [design],
            "instanceType": "StudyVersion",
        }
        study: dict[str, Any] = {
            "id": ids.placeholder("Study", self.study_name),
            "name": self.study_name,
            "versions": [version],
            "instanceType": "Study",
        }
        return study, version, design

    def _merge(self, target: dict[str, Any], prop: str, payload: Any, domain_id: str) -> None:
        existing = target.get(prop)
        if isinstance(payload, list):
            if existing is None:
                target[prop] = list(payload)
            elif isinstance(existing, list):
                existing.extend(payload)
            else:
                raise AssemblyError(
                    f"{domain_id}: cannot append a list to scalar property {prop!r}"
                )
        elif isinstance(payload, dict) and isinstance(existing, dict):
            existing.update(payload)
        else:
            target[prop] = payload

    def _check_required(
        self, node: dict[str, Any], entity: str, anchor: str
    ) -> None:
        """Record -- and in stub mode fill -- required properties that are absent."""
        entity_schema = self.schema.entity(entity)
        for prop in sorted(entity_schema.required):
            if prop in node and node[prop] not in (None, [], ""):
                continue
            if prop in {"id", "instanceType"}:
                continue
            missing = MissingRequirement(
                entity=entity,
                property=prop,
                anchor=anchor,
                reason=(
                    "no enabled domain produced it"
                    if prop not in node
                    else "produced empty by its domain"
                ),
            )
            if self.output_mode == "stub":
                node[prop] = _stub_value(self.schema, entity, prop, prop)
                missing.stubbed = True
            self.report.missing.append(missing)

    def build(self) -> dict[str, Any]:
        study, version, design = self._skeleton()
        anchors: dict[str, dict[str, Any]] = {
            "study": study,
            "studyVersion": version,
            "studyDesign": design,
        }

        for domain_id, anchor, prop, payload in self._fragments:
            self._merge(anchors[anchor], prop, payload, domain_id)

        # Join entities, once every domain fragment is in place.
        join = joins.build_study_cells(
            design.get("arms", []), design.get("epochs", []), elements=design.get("elements")
        )
        if join.study_cells:
            design["studyCells"] = join.study_cells
            design["elements"] = join.study_elements
        self.report.notes.append(join.note)

        self._check_required(study, "Study", "study")
        self._check_required(version, "StudyVersion", "studyVersion")
        self._check_required(design, self.design_type, "studyDesign")

        if self.output_mode == "strict" and self.report.missing:
            listing = ", ".join(f"{m.entity}.{m.property}" for m in self.report.missing[:8])
            raise AssemblyError(
                f"strict mode: {len(self.report.missing)} required properties are missing "
                f"({listing}). Enable the domains that produce them, or use "
                "output_mode 'partial' or 'stub'."
            )

        document = {
            "study": study,
            "usdmVersion": self.schema.api_version,
            "systemName": "protocol-to-edc",
            "systemVersion": "0.1.0",
        }
        # Terminology lookups and agent-supplied value objects (Code, AliasCode,
        # Quantity) arrive without ids; the schema requires them on every object.
        added = ids.ensure_ids(document)
        if added:
            self.report.notes.append(f"{added} ids added to value objects")
        document, resolution = ids.resolve(document)
        self.report.resolution = resolution
        return document
