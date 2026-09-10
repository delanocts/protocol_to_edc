"""Validate an assembled USDM document.

Three layers, in increasing specificity:

1. **JSON schema** -- does it match `USDM_API.json`? Catches wrong types, missing
   required properties, bad `instanceType` values.
2. **Referential integrity** -- does every `*Id` / `*Ids` property point at an
   object that exists in the document? JSON schema cannot check this: every id is
   just a string, so a reference to a deleted arm validates perfectly.
3. **Unresolved terminology** -- which `Code` objects fell back to `SPONSOR`
   because no published codelist matched. Not an error, but every one is a
   decision a reviewer should see.

Layer 2 is the one that catches the failure mode this pipeline is most prone to:
a disabled domain leaves references pointing at nothing.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Iterator

from jsonschema import ValidationError

from .schema import UsdmSchema

_MAX_REPORTED = 200


@dataclass
class Finding:
    severity: str  # "error" | "warning" | "info"
    kind: str
    path: str
    message: str

    def as_dict(self) -> dict[str, str]:
        return {
            "severity": self.severity,
            "kind": self.kind,
            "path": self.path,
            "message": self.message,
        }


@dataclass
class ValidationReport:
    findings: list[Finding] = field(default_factory=list)
    entity_counts: dict[str, int] = field(default_factory=dict)
    truncated: bool = False

    @property
    def errors(self) -> list[Finding]:
        return [f for f in self.findings if f.severity == "error"]

    @property
    def warnings(self) -> list[Finding]:
        return [f for f in self.findings if f.severity == "warning"]

    @property
    def valid(self) -> bool:
        return not self.errors

    def add(self, severity: str, kind: str, path: str, message: str) -> None:
        if len(self.findings) >= _MAX_REPORTED:
            self.truncated = True
            return
        self.findings.append(Finding(severity, kind, path, message))

    def summary(self) -> str:
        total = sum(self.entity_counts.values())
        head = "valid" if self.valid else f"{len(self.errors)} error(s)"
        return (
            f"{head}, {len(self.warnings)} warning(s); "
            f"{total} objects across {len(self.entity_counts)} entity types"
        )

    def as_dict(self) -> dict[str, Any]:
        return {
            "valid": self.valid,
            "errors": len(self.errors),
            "warnings": len(self.warnings),
            "truncated": self.truncated,
            "entityCounts": dict(sorted(self.entity_counts.items())),
            "findings": [f.as_dict() for f in self.findings],
        }


def _path_of(error: ValidationError) -> str:
    parts = ["$"]
    for item in error.absolute_path:
        parts.append(f"[{item}]" if isinstance(item, int) else f".{item}")
    return "".join(parts)


def _walk(node: Any, path: str) -> Iterator[tuple[str, dict[str, Any]]]:
    """Yield every USDM object (anything carrying an `instanceType`) with its path."""
    if isinstance(node, dict):
        if "instanceType" in node:
            yield path, node
        for key, value in node.items():
            yield from _walk(value, f"{path}.{key}")
    elif isinstance(node, list):
        for index, item in enumerate(node):
            yield from _walk(item, f"{path}[{index}]")


def _best_context(error: ValidationError, instance: Any) -> ValidationError:
    """Pick the meaningful sub-error from an `anyOf` cascade.

    USDM unions the two study design classes with `anyOf`, so a single bad
    property in an interventional design also reports every way it fails to be an
    observational one. Reporting the wrong branch sends a reader hunting for a
    property their design does not even have, so the branch matching the object's
    own `instanceType` is preferred, and the shallowest failure otherwise.
    """
    if not error.context:
        return error

    candidates = list(error.context)
    wanted = instance.get("instanceType") if isinstance(instance, dict) else None
    if wanted and isinstance(error.schema, dict) and "anyOf" in error.schema:
        branches = error.schema["anyOf"]
        keep = []
        for sub in candidates:
            index = next((p for p in sub.schema_path if isinstance(p, int)), None)
            if index is None or index >= len(branches):
                continue
            if str(branches[index].get("$ref", "")).rsplit("/", 1)[-1].startswith(f"{wanted}-"):
                keep.append(sub)
        candidates = keep or candidates

    best = min(candidates, key=lambda e: len(list(e.absolute_path)))
    return _best_context(best, best.instance)


def _check_schema(document: dict[str, Any], schema: UsdmSchema, report: ValidationReport) -> None:
    study = document.get("study")
    if not isinstance(study, dict):
        report.add("error", "schema", "$.study", "Document has no `study` object")
        return
    validator = schema.validator_for("Study")
    for error in sorted(validator.iter_errors(study), key=lambda e: list(e.absolute_path)):
        detail = _best_context(error, error.instance)
        report.add("error", "schema", _path_of(detail), detail.message[:300])


def _check_references(document: dict[str, Any], report: ValidationReport) -> None:
    known: set[str] = set()
    for _, obj in _walk(document, "$"):
        identifier = obj.get("id")
        if isinstance(identifier, str):
            known.add(identifier)

    for path, obj in _walk(document, "$"):
        for key, value in obj.items():
            if key == "id" or not (key.endswith("Id") or key.endswith("Ids")):
                continue
            for ref in value if isinstance(value, list) else [value]:
                if not isinstance(ref, str) or not ref:
                    continue
                if ref.startswith("@"):
                    report.add(
                        "error",
                        "unresolved-placeholder",
                        f"{path}.{key}",
                        f"{ref} was never declared by any object -- the domain that "
                        "produces it is disabled or did not emit it",
                    )
                elif ref not in known:
                    report.add(
                        "error",
                        "dangling-reference",
                        f"{path}.{key}",
                        f"points at {ref!r}, which is not in the document",
                    )


def _check_terminology(document: dict[str, Any], report: ValidationReport) -> None:
    for path, obj in _walk(document, "$"):
        if obj.get("instanceType") != "Code":
            continue
        if obj.get("codeSystem") == "SPONSOR":
            report.add(
                "warning",
                "sponsor-terminology",
                path,
                f"{obj.get('decode')!r} is sponsor-defined rather than published "
                "CDISC terminology -- legitimate for sponsor-specific values, but "
                "confirm it is not a term that should have been coded",
            )


def validate(document: dict[str, Any], schema: UsdmSchema) -> ValidationReport:
    """Run all three validation layers over an assembled document."""
    report = ValidationReport()

    for _, obj in _walk(document, "$"):
        kind = str(obj.get("instanceType", "?"))
        report.entity_counts[kind] = report.entity_counts.get(kind, 0) + 1

    _check_schema(document, schema, report)
    _check_references(document, report)
    _check_terminology(document, report)
    return report
