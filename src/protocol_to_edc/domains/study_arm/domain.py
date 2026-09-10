"""Domain 3 -- StudyArm.

The groups subjects are assigned to. In a parallel study these are the treatment
groups; in a crossover study they are the treatment *sequences*, which is the
distinction this domain most often has to get right.

`StudyArm` feeds the `StudyCell` grid that the assembler derives, so the arms
this domain returns determine how many cells the design ends up with. An arm
invented here multiplies through the whole schedule.
"""

from __future__ import annotations

from typing import Any

from pydantic import Field

from ...llm.schemas import DomainOutput, Grounded
from ...usdm import ids
from ..base import DomainContext, compose_prompt


class StudyArmItem(Grounded):
    """One arm or treatment sequence."""

    name: str = Field(
        description=(
            "The arm's name in the protocol's own wording, e.g. 'Nasal Glucagon' "
            "or 'Sequence AB'. Keep it short; it names the arm, it does not "
            "describe it."
        )
    )
    label: str = Field(default="", description="A display label, if different from the name.")
    description: str = Field(
        default="",
        description="What subjects in this arm receive, as the protocol describes it.",
    )
    arm_type: str = Field(
        default="",
        description=(
            "The arm's classification, using the permitted wording: investigational, "
            "active comparator, placebo control, and so on."
        ),
    )
    intervention_names: list[str] = Field(
        default_factory=list,
        description=(
            "Names of the interventions given in this arm, matching how the "
            "intervention section names them. Used to link arms to interventions."
        ),
    )
    planned_subjects: int | None = Field(
        default=None, description="Number of subjects planned for this arm, if stated."
    )


PAYLOAD_MODEL = StudyArmItem
OutputModel = DomainOutput[StudyArmItem]


def build_prompt(ctx: DomainContext) -> str:
    return compose_prompt(
        ctx,
        task=(
            "List the study's arms: the groups subjects are assigned to.\n\n"
            "Return one item per arm, in the order the protocol presents them."
        ),
        guidance="""\
The commonest error here is confusing arms with periods. An arm is *who a subject \
is*, for the whole study; a period is *when*. If every subject eventually receives \
both treatments, those treatments are not two arms.

In a crossover study the arms are the sequences, not the treatments. A two-period \
crossover of drug A and drug B has two arms -- the sequence A-then-B and the \
sequence B-then-A -- and every subject is in exactly one of them. Name them the \
way the protocol does; if it labels them 'Sequence 1' and 'Sequence 2', use that, \
and put the composition in the description.

A single-group study has one arm. Say so explicitly rather than returning none.

Arm type classifies the arm's role in the comparison. The arm receiving the \
investigational product is the investigational arm; an arm receiving an approved \
active drug for comparison is an active comparator; an arm receiving placebo is \
a placebo control. In a crossover, a sequence arm contains both, so classify it \
by the protocol's own framing and record a gap if that is genuinely ambiguous.

`planned_subjects` is per arm. If the protocol gives only a total, leave this \
empty rather than dividing the total yourself -- an allocation ratio is not \
always even, and the population domain records the total.""",
    )


def to_usdm(output: OutputModel, ctx: DomainContext) -> dict[str, Any]:
    arms = []
    for item in output.items:
        if not item.name:
            continue
        key = ids.slug(item.name)
        arms.append(
            {
                "id": ctx.placeholder("StudyArm", key),
                "name": item.name,
                "label": item.label or item.name,
                "description": item.description or item.name,
                "type": ctx.resolve_code("StudyArm", "type", item.arm_type)
                or ctx.terminology.sponsor_code(item.arm_type or "Not stated"),
                "dataOriginType": ctx.resolve_code(
                    "StudyArm", "dataOriginType", "Data Generated Within Study"
                ),
                "dataOriginDescription": "Data generated within this study.",
                "instanceType": "StudyArm",
            }
        )
    return {"studyDesign.arms": arms} if arms else {}
