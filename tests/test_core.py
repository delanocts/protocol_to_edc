"""Tests for the deterministic core: paths, config, terminology, assembly."""

from __future__ import annotations

import json

import pytest

from protocol_to_edc.core import config, paths
from protocol_to_edc.usdm import assembler, ct, ids, joins, schema, validator

USDM_VERSION = "4.0.0"


@pytest.fixture(scope="session")
def usdm_schema():
    return schema.load(USDM_VERSION)


@pytest.fixture(scope="session")
def terminology():
    return ct.load(USDM_VERSION)


@pytest.fixture(scope="session")
def reference_document():
    path = paths.REFERENCE_STUDIES / "lzzt" / "CDISC_Pilot_Study.json"
    if not path.is_file():
        pytest.skip("LZZT reference document not present")
    return json.loads(path.read_text(encoding="utf-8"))


# -- paths -----------------------------------------------------------------


def test_study_id_rejects_non_ascii_hyphen():
    """U+2011 is invisible next to U+002D and breaks Windows path handling."""
    with pytest.raises(paths.StudyIdError) as excinfo:
        paths.validate_study_id("I8R‑JE‑IGBJ")
    assert "U+2011" in str(excinfo.value)


def test_study_paths_refuse_to_escape_the_study_directory():
    sp = paths.for_study("EXAMPLE-1")
    with pytest.raises(ValueError):
        sp.resolve_input("../../.env")


def test_usdm_resource_dir_accepts_both_version_spellings():
    assert paths.usdm_resource_dir("4.0.0") == paths.usdm_resource_dir("4.x")


# -- config ----------------------------------------------------------------


def test_default_config_declares_eight_domains():
    data = config._read_yaml(paths.DEFAULT_CONFIG)
    assert len(data["domains"]) == 8


def test_null_override_means_inherit():
    merged = config._deep_merge({"llm": {"model": "claude-opus-5"}}, {"llm": {"model": None}})
    assert merged["llm"]["model"] == "claude-opus-5"


def test_unknown_usdm_version_is_rejected():
    with pytest.raises(Exception):
        config.UsdmConfig(version="99.0.0")


# -- terminology -----------------------------------------------------------


def test_resolve_matches_loosely_but_never_invents(terminology):
    assert terminology.resolve("StudyEpoch", "type", "screening")["code"] == "C202487"
    assert terminology.resolve("StudyEpoch", "type", "Not A Real Epoch") is None


def test_supplement_carries_full_published_codelists(terminology):
    """The reference document uses three epoch types; the codelist has many more."""
    assert len(terminology.codelist("StudyEpoch", "type").terms) > 10


def test_definitions_come_from_terminology_not_schema(terminology, usdm_schema):
    assert terminology.definition("StudyArm", "type")
    # The OpenAPI schema carries no prose at all, which is why the above matters.
    assert "description" not in usdm_schema.raw("StudyArm").get("properties", {}).get(
        "type", {}
    )


# -- identifiers -----------------------------------------------------------


def test_placeholders_resolve_and_reference_the_same_object():
    document = {
        "a": {"id": ids.placeholder("StudyArm", "active"), "instanceType": "StudyArm"},
        "b": {"armId": ids.placeholder("StudyArm", "active")},
    }
    resolved, resolution = ids.resolve(document)
    assert resolved["a"]["id"] == resolved["b"]["armId"] == "StudyArm_1"
    assert resolution.ok


def test_reference_to_undeclared_placeholder_is_reported_not_invented():
    document = {"b": {"armId": ids.placeholder("StudyArm", "ghost")}}
    resolved, resolution = ids.resolve(document)
    assert not resolution.ok
    assert resolved["b"]["armId"].startswith("@")


def test_ids_are_minted_in_document_order():
    document = {
        "items": [
            {"id": ids.placeholder("StudyArm", "zulu"), "instanceType": "StudyArm"},
            {"id": ids.placeholder("StudyArm", "alpha"), "instanceType": "StudyArm"},
        ]
    }
    resolved, _ = ids.resolve(document)
    assert [i["id"] for i in resolved["items"]] == ["StudyArm_1", "StudyArm_2"]


# -- joins -----------------------------------------------------------------


def test_study_cells_are_the_arm_by_epoch_grid():
    arms = [
        {"id": ids.placeholder("StudyArm", f"a{i}"), "name": f"Arm {i}"} for i in range(3)
    ]
    epochs = [{"id": ids.placeholder("StudyEpoch", f"e{i}")} for i in range(5)]
    result = joins.build_study_cells(arms, epochs)
    assert result.count == 15  # matches the reference document's 3 arms x 5 epochs
    assert len(result.study_elements) == 3


def test_no_cells_are_invented_when_a_side_is_missing():
    result = joins.build_study_cells([], [{"id": "@StudyEpoch:x"}])
    assert result.study_cells == []
    assert "arms" in result.note


# -- assembly and validation ----------------------------------------------


def _minimal_assembly(usdm_schema, terminology, output_mode):
    a = assembler.Assembly(
        usdm_schema, study_name="TEST-1", output_mode=output_mode, rationale="Test."
    )
    a.add(
        "epoch",
        "studyDesign.epochs",
        [
            {
                "id": ids.placeholder("StudyEpoch", "screening"),
                "name": "Screening",
                "type": terminology.resolve("StudyEpoch", "type", "Screening Epoch"),
                "instanceType": "StudyEpoch",
            }
        ],
    )
    return a


def test_stub_mode_produces_a_schema_valid_document(usdm_schema, terminology):
    a = _minimal_assembly(usdm_schema, terminology, "stub")
    report = validator.validate(a.build(), usdm_schema)
    assert report.valid, [f.message for f in report.errors]
    assert a.report.missing  # it is valid *because* gaps were stubbed, and says so


def test_partial_mode_reports_gaps_instead_of_filling_them(usdm_schema, terminology):
    a = _minimal_assembly(usdm_schema, terminology, "partial")
    a.build()
    assert a.report.missing
    assert not any(m.stubbed for m in a.report.missing)


def test_strict_mode_refuses_an_incomplete_document(usdm_schema, terminology):
    a = _minimal_assembly(usdm_schema, terminology, "strict")
    with pytest.raises(assembler.AssemblyError, match="strict mode"):
        a.build()


def test_value_objects_get_ids_automatically(usdm_schema, terminology):
    """Terminology lookups return Code objects with no id; the schema demands one."""
    document = _minimal_assembly(usdm_schema, terminology, "stub").build()
    epoch = document["study"]["versions"][0]["studyDesigns"][0]["epochs"][0]
    assert epoch["type"]["id"]


# -- regression against the published reference document -------------------


def test_reference_document_passes_our_validator(reference_document, usdm_schema):
    """A known-good USDM v4 document must produce no errors.

    This is the guard against the validator drifting into false positives: any
    error raised against the CDISC pilot study is wrong about USDM, not about us.

    Warnings are a different matter. The reference document does carry
    sponsor-coded values -- the sponsor's own therapeutic area, an intervention
    code -- which are legitimate USDM but are exactly what a reviewer should see
    listed, so they stay warnings.
    """
    report = validator.validate(reference_document, usdm_schema)
    assert report.valid, [f"{f.path}: {f.message}" for f in report.errors[:5]]
    assert {f.kind for f in report.warnings} <= {"sponsor-terminology"}


def test_reference_document_has_no_dangling_references(reference_document, usdm_schema):
    report = validator.validate(reference_document, usdm_schema)
    assert not [f for f in report.findings if f.kind == "dangling-reference"]
