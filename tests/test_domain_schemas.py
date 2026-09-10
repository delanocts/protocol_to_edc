"""Guards on the schemas sent to the structured-outputs API.

The API rejects several JSON-schema keywords, and it rejects them at request
time -- after the protocol has been uploaded and the run has started. Pydantic
emits some of them from perfectly ordinary field declarations: `Field(ge=0, le=1)`
becomes `minimum`/`maximum`, which returns

    output_config.format.schema: For 'number' type, properties maximum, minimum
    are not supported

These tests catch that at development time instead, for every domain at once,
so adding a ninth domain with a constrained field fails here rather than in a
billed run.
"""

from __future__ import annotations

import json
from typing import Any

import pytest

from protocol_to_edc.core import registry

# Keywords the structured-outputs API does not accept. Validation that these
# would have expressed belongs in a pydantic validator, which runs after parsing.
UNSUPPORTED_KEYWORDS = {
    "minimum",
    "maximum",
    "exclusiveMinimum",
    "exclusiveMaximum",
    "multipleOf",
    "minLength",
    "maxLength",
    "pattern",
    "minItems",
    "maxItems",
    "uniqueItems",
    "format",
}

DOMAIN_IDS = [spec.id for spec in registry.load_all()]


def _walk(node: Any, path: str = "$"):
    if isinstance(node, dict):
        yield path, node
        for key, value in node.items():
            yield from _walk(value, f"{path}.{key}")
    elif isinstance(node, list):
        for index, item in enumerate(node):
            yield from _walk(item, f"{path}[{index}]")


@pytest.mark.parametrize("domain_id", DOMAIN_IDS)
def test_schema_uses_no_unsupported_keywords(domain_id):
    module = registry.get(domain_id).module()
    schema = module.OutputModel.model_json_schema()

    offenders = []
    for path, node in _walk(schema):
        for keyword in UNSUPPORTED_KEYWORDS & set(node):
            # `properties` may legitimately contain a field *named* e.g. "format".
            if path.endswith(".properties"):
                continue
            offenders.append(f"{path}.{keyword} = {node[keyword]!r}")

    assert not offenders, (
        f"{domain_id}: schema contains keywords the structured-outputs API rejects:\n  "
        + "\n  ".join(offenders)
        + "\nMove the constraint into a pydantic field_validator instead."
    )


@pytest.mark.parametrize("domain_id", DOMAIN_IDS)
def test_schema_forbids_extra_properties(domain_id):
    """Every object must be closed, or the model may invent fields."""
    module = registry.get(domain_id).module()
    schema = module.OutputModel.model_json_schema()
    for path, node in _walk(schema):
        if node.get("type") == "object" and "properties" in node:
            assert node.get("additionalProperties") is False, (
                f"{domain_id}: object at {path} allows extra properties"
            )


@pytest.mark.parametrize("domain_id", DOMAIN_IDS)
def test_every_field_is_described(domain_id):
    """An undescribed field is a field the model has to guess the meaning of."""
    module = registry.get(domain_id).module()
    schema = module.OutputModel.model_json_schema()
    missing = []
    for path, node in _walk(schema):
        if not path.endswith(".properties"):
            continue
        for name, field in node.items():
            if isinstance(field, dict) and not field.get("description") and "$ref" not in field:
                missing.append(f"{path}.{name}")
    assert not missing, f"{domain_id}: fields with no description: {missing}"


@pytest.mark.parametrize("domain_id", DOMAIN_IDS)
def test_schema_is_json_serialisable(domain_id):
    module = registry.get(domain_id).module()
    json.dumps(module.OutputModel.model_json_schema())


@pytest.mark.parametrize("domain_id", DOMAIN_IDS)
def test_domain_exposes_the_required_interface(domain_id):
    spec = registry.get(domain_id)
    module = spec.module()
    assert callable(module.build_prompt)
    assert callable(module.to_usdm)
    assert hasattr(module, "PAYLOAD_MODEL")


@pytest.mark.parametrize("domain_id", DOMAIN_IDS)
def test_manifest_targets_a_known_anchor(domain_id):
    from protocol_to_edc.usdm.assembler import ANCHORS

    spec = registry.get(domain_id)
    assert spec.anchor in ANCHORS, (
        f"{domain_id}: attaches_to {spec.attaches_to!r} does not start with a known anchor"
    )


@pytest.mark.parametrize("domain_id", DOMAIN_IDS)
def test_declared_entities_exist_in_usdm(domain_id):
    from protocol_to_edc.usdm import schema

    usdm = schema.load("4.0.0")
    spec = registry.get(domain_id)
    unknown = [e for e in spec.produces if not usdm.has_entity(e)]
    assert not unknown, f"{domain_id}: manifest names entities not in USDM v4: {unknown}"
