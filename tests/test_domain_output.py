"""Every domain's `to_usdm` must produce schema-valid USDM.

A domain module hand-builds USDM objects, and it is easy to get one subtly
wrong: `Administration.route` is an `AliasCode` wrapping a `Code`, not a `Code`;
`Administration.duration` is required even when the protocol states none. Both
of those shipped as bugs and were only caught by a billed run against a real
protocol.

These tests catch that class of error with no API call: each domain is handed a
filled-in payload built from its own schema, and the fragment it returns is
assembled and validated. They are not about extraction quality -- the values are
synthetic -- purely about whether the USDM a domain emits is well-formed.
"""

from __future__ import annotations

from typing import Any

import pytest
from pydantic import BaseModel

from protocol_to_edc.core import registry
from protocol_to_edc.core.config import Settings
from protocol_to_edc.domains.base import DomainContext
from protocol_to_edc.pdf.extract import ProtocolText
from protocol_to_edc.usdm import assembler, ct, schema, validator

DOMAIN_IDS = [spec.id for spec in registry.load_all()]
USDM_VERSION = "4.0.0"

# Values chosen to resolve against real codelists where a field is coded, so the
# fragment exercises the terminology path rather than only the sponsor fallback.
SAMPLE_STRINGS = {
    "study_type": "Interventional Study",
    "intervention_model": "Crossover Study",
    "study_phase": "Phase III Trial",
    "blinding_schema": "Open Label",
    "epoch_type": "Screening Epoch",
    "arm_type": "Investigational Arm",
    "role": "Experimental Intervention",
    "intervention_type": "Drug",
    "level": "Primary Objective",
    "category": "Inclusion Criteria",
    "planned_sex": "Both",
    "encounter_type": "Visit",
    "route": "Nasal Route of Administration",
    "frequency": "Once",
    "dose_unit": "mg",
    "timing_value_iso": "P7D",
    "window_lower_iso": "-P2D",
    "window_upper_iso": "P2D",
    "identifier": "1",
}


def _fill(model: type[BaseModel], depth: int = 0) -> BaseModel:
    """Build an instance of `model` with plausible values for every field."""
    values: dict[str, Any] = {}
    for name, info in model.model_fields.items():
        annotation = info.annotation
        origin = getattr(annotation, "__origin__", None)

        if name in SAMPLE_STRINGS:
            values[name] = SAMPLE_STRINGS[name]
        elif name == "confidence":
            values[name] = 0.9
        elif name == "page" or name == "source_page":
            values[name] = 1
        elif name == "quote":
            values[name] = "a verbatim span from the protocol"
        elif annotation is bool:
            values[name] = True
        elif annotation is int:
            values[name] = 12
        elif annotation is float:
            values[name] = 1.5
        elif annotation is str:
            values[name] = f"sample {name}"
        elif origin is list:
            (item_type,) = annotation.__args__
            if isinstance(item_type, type) and issubclass(item_type, BaseModel):
                values[name] = [_fill(item_type, depth + 1)] if depth < 2 else []
            else:
                values[name] = [SAMPLE_STRINGS.get(name, f"sample {name}")]
        elif isinstance(annotation, type) and issubclass(annotation, BaseModel):
            values[name] = _fill(annotation, depth + 1)
        elif info.is_required():
            values[name] = f"sample {name}"
    return model.model_validate(values)


@pytest.fixture(scope="module")
def context_parts():
    usdm = schema.load(USDM_VERSION)
    terminology = ct.load(USDM_VERSION)
    protocol = ProtocolText(path=None, pages=["placeholder page"])  # type: ignore[arg-type]
    return usdm, terminology, protocol


def _build_fragment(domain_id: str, context_parts):
    usdm, terminology, protocol = context_parts
    spec = registry.get(domain_id)
    module = spec.module()
    settings = Settings(study_id="TEST-1")
    ctx = DomainContext(
        settings=settings,
        spec=spec,
        schema=usdm,
        terminology=terminology,
        protocol=protocol,
    )
    output = module.OutputModel(items=[_fill(module.PAYLOAD_MODEL)], gaps=[], notes="")
    return module.to_usdm(output, ctx), ctx


@pytest.mark.parametrize("domain_id", DOMAIN_IDS)
def test_to_usdm_returns_a_target_map(domain_id, context_parts):
    """The contract is dict[target, payload]; a bare list would go to the wrong place."""
    fragment, _ = _build_fragment(domain_id, context_parts)
    assert isinstance(fragment, dict), f"{domain_id}: to_usdm must return a dict"
    for target in fragment:
        anchor, _, prop = target.partition(".")
        assert anchor in assembler.ANCHORS, f"{domain_id}: bad anchor in {target!r}"
        assert prop, f"{domain_id}: target {target!r} names no property"


@pytest.mark.parametrize("domain_id", DOMAIN_IDS)
def test_domain_output_assembles_into_valid_usdm(domain_id, context_parts):
    usdm, _, _ = context_parts
    fragment, _ = _build_fragment(domain_id, context_parts)

    a = assembler.Assembly(
        usdm, study_name="TEST-1", output_mode="stub", rationale="Test."
    )
    for target, payload in fragment.items():
        a.add(domain_id, target, payload)

    report = validator.validate(a.build(), usdm)
    schema_errors = [f for f in report.errors if f.kind == "schema"]
    assert not schema_errors, (
        f"{domain_id} emits schema-invalid USDM:\n  "
        + "\n  ".join(f"{f.path}: {f.message}" for f in schema_errors[:6])
    )


@pytest.mark.parametrize("domain_id", DOMAIN_IDS)
def test_domain_output_has_no_dangling_references(domain_id, context_parts):
    """Within one domain, anything it references it must also declare.

    A reference across domains is legitimate and is checked at run time; a
    reference to something the same domain never created is a bug.
    """
    usdm, _, _ = context_parts
    fragment, _ = _build_fragment(domain_id, context_parts)

    a = assembler.Assembly(
        usdm, study_name="TEST-1", output_mode="stub", rationale="Test."
    )
    for target, payload in fragment.items():
        a.add(domain_id, target, payload)
    document = a.build()

    # The study domain deliberately references organisations it also emits;
    # the schedule domain references epochs owned by the epoch domain.
    cross_domain_ok = {"activity_schedule"}
    if domain_id in cross_domain_ok:
        pytest.skip("references another domain's entities by design")

    dangling = [f for f in validator.validate(document, usdm).findings
                if f.kind in {"dangling-reference", "unresolved-placeholder"}]
    assert not dangling, (
        f"{domain_id}: references entities it does not create:\n  "
        + "\n  ".join(f"{f.path}: {f.message}" for f in dangling[:5])
    )
