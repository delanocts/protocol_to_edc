"""Access to the USDM OpenAPI schema.

`USDM_API.json` is the authority on entity shape: property names, types, required
fields and the `instanceType` constant. It carries no prose descriptions -- the
titles are generated -- so what a field *means* comes from the Implementation
Guide excerpts and the controlled terminology, not from here.

Two consumers:

* `validator_for()` -- jsonschema validation of an assembled document.
* `describe()` -- a compact, token-cheap rendering of an entity for an agent
  prompt. The raw schema is unusable for that: it is deeply `$ref`-linked and
  a single entity expands to tens of thousands of tokens.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from functools import cache
from typing import Any, Literal

from jsonschema import Draft202012Validator

from ..core import paths

Variant = Literal["Input", "Output"]

# Housekeeping properties present on nearly every entity. They are handled by the
# assembler (ids) or are rarely used (extensions, notes), so they are hidden from
# agent-facing renderings to keep prompts focused on the clinical content.
_HOUSEKEEPING = frozenset({"id", "extensionAttributes", "instanceType", "notes"})


class SchemaError(KeyError):
    """An entity or property that is not in the USDM schema."""


@dataclass(frozen=True)
class PropertySpec:
    """One property of a USDM entity, flattened for prompting and assembly."""

    name: str
    type_name: str
    required: bool
    is_array: bool
    nullable: bool
    ref_entity: str | None
    const: str | None

    @property
    def is_reference(self) -> bool:
        """True when the value is an id (or list of ids) pointing at another entity."""
        return self.ref_entity is None and (
            self.name.endswith("Id") or self.name.endswith("Ids")
        )

    def render(self) -> str:
        bits = [f"{self.name}: {self.type_name}"]
        if self.required:
            bits.append("REQUIRED")
        if self.const:
            bits.append(f'const="{self.const}"')
        return "  ".join(bits)


@dataclass(frozen=True)
class EntitySchema:
    name: str
    variant: Variant
    properties: tuple[PropertySpec, ...]
    required: frozenset[str]

    def property(self, name: str) -> PropertySpec:
        for p in self.properties:
            if p.name == name:
                return p
        raise SchemaError(f"{self.name} has no property {name!r}")

    def content_properties(self) -> tuple[PropertySpec, ...]:
        return tuple(p for p in self.properties if p.name not in _HOUSEKEEPING)

    def child_entities(self) -> tuple[str, ...]:
        seen: dict[str, None] = {}
        for p in self.properties:
            if p.ref_entity and p.name not in _HOUSEKEEPING:
                seen.setdefault(p.ref_entity, None)
        return tuple(seen)


def _strip_variant(ref: str) -> str:
    """'#/components/schemas/Code-Input' -> 'Code'."""
    name = ref.rsplit("/", 1)[-1]
    for suffix in ("-Input", "-Output"):
        if name.endswith(suffix):
            return name[: -len(suffix)]
    return name


def _flatten(name: str, node: dict[str, Any], required: frozenset[str]) -> PropertySpec:
    """Reduce one JSON-schema property node to a flat spec.

    Handles the three shapes USDM uses: a direct `$ref`, an array of `$ref`, and
    an `anyOf` of [type, null] for optional scalars.
    """
    is_array = False
    nullable = False
    ref_entity: str | None = None
    const = node.get("const")
    type_name = node.get("type", "")

    if "anyOf" in node:
        options = [o for o in node["anyOf"] if o.get("type") != "null"]
        nullable = len(options) != len(node["anyOf"])
        node = options[0] if options else {}
        type_name = node.get("type", "")
        const = node.get("const", const)

    if "$ref" in node:
        ref_entity = _strip_variant(node["$ref"])
        type_name = ref_entity
    elif node.get("type") == "array":
        is_array = True
        items = node.get("items", {})
        if "$ref" in items:
            ref_entity = _strip_variant(items["$ref"])
            type_name = f"list[{ref_entity}]"
        else:
            type_name = f"list[{items.get('type', 'any')}]"
    elif node.get("enum"):
        type_name = " | ".join(json.dumps(v) for v in node["enum"])

    return PropertySpec(
        name=name,
        type_name=type_name or "any",
        required=name in required,
        is_array=is_array,
        nullable=nullable,
        ref_entity=ref_entity,
        const=const if isinstance(const, str) else None,
    )


class UsdmSchema:
    """One loaded USDM API schema document."""

    def __init__(self, version: str, document: dict[str, Any]) -> None:
        self.version = version
        self.document = document
        self._schemas: dict[str, Any] = document["components"]["schemas"]

    # -- lookup ------------------------------------------------------------

    @property
    def api_version(self) -> str:
        return str(self.document.get("info", {}).get("version", self.version))

    def entity_names(self) -> tuple[str, ...]:
        names = {
            _strip_variant(k) for k in self._schemas if k.endswith(("-Input", "-Output"))
        }
        return tuple(sorted(names))

    def has_entity(self, name: str) -> bool:
        return f"{name}-Input" in self._schemas

    def raw(self, name: str, variant: Variant = "Input") -> dict[str, Any]:
        key = f"{name}-{variant}"
        try:
            return self._schemas[key]
        except KeyError:
            near = [n for n in self.entity_names() if name.lower() in n.lower()][:5]
            hint = f" Did you mean: {', '.join(near)}?" if near else ""
            raise SchemaError(
                f"{key} is not in USDM {self.api_version}.{hint}"
            ) from None

    @cache  # noqa: B019 -- instances are themselves cached and long-lived
    def entity(self, name: str, variant: Variant = "Input") -> EntitySchema:
        node = self.raw(name, variant)
        required = frozenset(node.get("required", ()))
        props = tuple(
            _flatten(prop_name, prop_node, required)
            for prop_name, prop_node in node.get("properties", {}).items()
        )
        return EntitySchema(name=name, variant=variant, properties=props, required=required)

    # -- validation --------------------------------------------------------

    @cache  # noqa: B019
    def validator_for(self, name: str, variant: Variant = "Input") -> Draft202012Validator:
        """A validator for one entity, with `$ref`s resolvable against components."""
        self.raw(name, variant)  # existence check with a good error message
        schema = {
            "$ref": f"#/components/schemas/{name}-{variant}",
            "components": self.document["components"],
        }
        return Draft202012Validator(schema)

    # -- prompt rendering --------------------------------------------------

    def describe(
        self,
        name: str,
        *,
        variant: Variant = "Input",
        expand: int = 1,
        _seen: frozenset[str] | None = None,
    ) -> str:
        """Compact text rendering of an entity for an agent prompt.

        `expand` controls how many levels of referenced entities are inlined.
        Depth 1 is usually right: it shows the entity plus the shape of the
        `Code` objects and children it must produce, without dragging in the
        whole graph.
        """
        seen = (_seen or frozenset()) | {name}
        ent = self.entity(name, variant)
        lines = [f"{ent.name}:"]
        for prop in ent.content_properties():
            lines.append(f"  - {prop.render()}")
        if ent.required:
            visible_required = sorted(ent.required - _HOUSEKEEPING)
            if visible_required:
                lines.append(f"  required: {', '.join(visible_required)}")

        if expand > 0:
            for child in ent.child_entities():
                if child in seen:
                    continue
                nested = self.describe(
                    child, variant=variant, expand=expand - 1, _seen=seen
                )
                lines.append("")
                lines.extend("  " + line for line in nested.splitlines())
        return "\n".join(lines)

    def describe_many(self, names: list[str] | tuple[str, ...], *, expand: int = 1) -> str:
        return "\n\n".join(self.describe(n, expand=expand) for n in names)


@cache
def load(version: str = "4.0.0") -> UsdmSchema:
    """Load and cache the USDM schema for a version."""
    path = paths.usdm_resource_dir(version) / "USDM_API.json"
    if not path.is_file():
        raise FileNotFoundError(
            f"USDM schema not found at {path}. "
            "Run `python -m protocol_to_edc.usdm.refresh` to download it."
        )
    return UsdmSchema(version, json.loads(path.read_text(encoding="utf-8")))
