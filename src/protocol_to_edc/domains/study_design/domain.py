"""Domain 2 -- StudyDesign.

How the study is built: interventional or observational, its intervention model,
whether and how it is blinded, its phase, and what it intends to establish.

USDM v4 has no class called `StudyDesign`. There are two concrete classes,
`InterventionalStudyDesign` and `ObservationalStudyDesign`, and they differ in
their required properties -- an observational design requires `timePerspective`,
which an interventional one has no concept of. This domain therefore does not
create the design object; the assembler does, from configuration. What this
domain produces are the design's classifying properties.

Phase and blinding are `AliasCode`, not plain `Code`: a wrapper that carries one
standard code plus any sponsor aliases for it. That is why 'Phase 3' from the
protocol becomes `studyPhase.standardCode` rather than `studyPhase` directly.
"""

from __future__ import annotations

from typing import Any

from pydantic import Field

from ...llm.schemas import DomainOutput, Grounded
from ..base import DomainContext, compose_prompt


class DesignClassification(Grounded):
    """The design's classifying properties."""

    study_type: str = Field(
        default="",
        description="Interventional or observational, using the permitted wording.",
    )
    intervention_model: str = Field(
        default="",
        description=(
            "How subjects are allocated across treatments: parallel, crossover, "
            "single group, factorial. Use the permitted wording."
        ),
    )
    study_phase: str = Field(
        default="", description="Trial phase, using the permitted wording."
    )
    blinding_schema: str = Field(
        default="",
        description=(
            "Masking arrangement, using the permitted wording. Open label is a "
            "valid answer and should be stated rather than left empty."
        ),
    )
    blinding_description: str = Field(
        default="",
        description="What the protocol says about who is blinded and how, in its own words.",
    )
    is_masked: bool = Field(
        default=False, description="False for an open-label study, true otherwise."
    )
    intent_types: list[str] = Field(
        default_factory=list,
        description="What the study is for: treatment, prevention, diagnosis. Permitted wording.",
    )
    sub_types: list[str] = Field(
        default_factory=list,
        description="Trial type(s): efficacy, safety, pharmacokinetic, bioequivalence.",
    )
    characteristics: list[str] = Field(
        default_factory=list,
        description="Design characteristics such as adaptive, extension, randomised.",
    )
    is_randomised: bool = Field(
        default=False, description="Whether subjects are randomly allocated."
    )
    design_rationale: str = Field(
        default="",
        description="The protocol's stated rationale for the design, if it gives one.",
    )


PAYLOAD_MODEL = DesignClassification
OutputModel = DomainOutput[DesignClassification]


def build_prompt(ctx: DomainContext) -> str:
    return compose_prompt(
        ctx,
        task=(
            "Classify this study's design: its type, intervention model, phase, "
            "blinding, intent and sub-types.\n\n"
            "Return a single item. Every coded field must use the exact wording "
            "of one of the permitted values; if none fits, leave it empty and "
            "record a gap explaining what the protocol says instead."
        ),
        guidance="""\
Intervention model is about allocation structure, and a protocol rarely names it \
directly -- infer it from how subjects move through treatments. Each subject \
receiving one treatment for the whole study is parallel; each receiving several \
in sequence, with a washout between, is crossover; a single group with no \
comparator is single group.

A crossover is easy to miss. Signals: 'sequence', 'period 1 / period 2', \
'washout', a randomisation to an order rather than to a treatment, or a schedule \
of activities whose columns repeat per period. If you see those, say crossover \
and quote the wording that shows it.

Blinding: 'open label' is a real answer, not a missing one. Where a protocol \
says the participant knows but the assessor does not, that is single blind with \
the description spelling out which parties are masked. Put the protocol's own \
sentence in `blinding_description`.

Phase is often only on the title page or in the synopsis header. Match to the \
permitted wording -- a protocol saying 'Phase 3' maps to the codelist's phase \
three term.

`is_randomised` is true whenever subjects are allocated by a random process, \
including randomisation to a treatment sequence in a crossover study.

Do not confuse intent type with sub-type. Intent is the purpose for the patient \
(treatment, prevention, supportive care); sub-type is the kind of investigation \
(efficacy, safety, pharmacokinetic). A study is usually one intent and several \
sub-types.""",
    )


def to_usdm(output: OutputModel, ctx: DomainContext) -> dict[str, Any]:
    if not output.items:
        return {}
    item = output.items[0]
    design = "InterventionalStudyDesign"
    fragment: dict[str, Any] = {}

    if item.study_type:
        code = ctx.resolve_code(design, "studyType", item.study_type)
        if code:
            fragment["studyDesign.studyType"] = code

    if item.intervention_model:
        code = ctx.resolve_code(design, "model", item.intervention_model)
        if code:
            fragment["studyDesign.model"] = code

    if item.study_phase:
        code = ctx.resolve_code(design, "studyPhase", item.study_phase)
        if code:
            fragment["studyDesign.studyPhase"] = {
                "id": ctx.placeholder("AliasCode", "study-phase"),
                "standardCode": code,
                "instanceType": "AliasCode",
            }

    if item.blinding_schema:
        code = ctx.resolve_code(design, "blindingSchema", item.blinding_schema)
        if code:
            fragment["studyDesign.blindingSchema"] = {
                "id": ctx.placeholder("AliasCode", "blinding"),
                "standardCode": code,
                "instanceType": "AliasCode",
            }

    for field_name, target, attribute in (
        ("intent_types", "studyDesign.intentTypes", "intentTypes"),
        ("sub_types", "studyDesign.subTypes", "subTypes"),
        ("characteristics", "studyDesign.characteristics", "characteristics"),
    ):
        values = getattr(item, field_name)
        codes = [c for c in (ctx.resolve_code(design, attribute, v) for v in values) if c]
        if codes:
            fragment[target] = codes

    if item.design_rationale:
        fragment["studyDesign.rationale"] = item.design_rationale

    return fragment
