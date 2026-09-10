"""Domain 4 -- Epoch.

The periods a study passes through: screening, treatment, follow-up, and any
run-in, washout or extension between them.

Epochs are ordered, and USDM expresses that order with `previousId` / `nextId`
links rather than by array position. This module builds that chain from the
order the agent returns them in, which is why the prompt insists on chronological
order rather than treating it as presentation detail.

Epochs also multiply into the `StudyCell` grid alongside arms, so an epoch that
is really a visit -- a common mistake -- inflates the whole design.
"""

from __future__ import annotations

from typing import Any

from pydantic import Field

from ...llm.schemas import DomainOutput, Grounded
from ...usdm import ids
from ..base import DomainContext, compose_prompt


class EpochItem(Grounded):
    """One study epoch."""

    name: str = Field(
        description="The epoch's name in the protocol's wording, e.g. 'Screening'."
    )
    label: str = Field(default="", description="Display label, if different from the name.")
    description: str = Field(
        default="", description="What happens during this epoch, briefly."
    )
    epoch_type: str = Field(
        default="",
        description="The epoch's type, using the exact wording of a permitted value.",
    )
    duration_text: str = Field(
        default="",
        description=(
            "The epoch's duration as the protocol states it, e.g. 'up to 28 days' "
            "or 'Day 1 to Day 28'. Free text; do not convert units."
        ),
    )


PAYLOAD_MODEL = EpochItem
OutputModel = DomainOutput[EpochItem]


def build_prompt(ctx: DomainContext) -> str:
    return compose_prompt(
        ctx,
        task=(
            "List the study's epochs -- the consecutive periods the study passes "
            "through.\n\n"
            "Return them in chronological order. Order matters: it becomes the "
            "epoch sequence in the output, so do not sort them any other way."
        ),
        guidance="""\
An epoch is a phase of the study, not a visit. Screening is an epoch; the \
screening visit is not. If a candidate epoch has a single time point rather than \
a span, it is almost certainly a visit and belongs to the schedule domain.

Typical epochs are screening, run-in, treatment, washout, follow-up and \
extension. A crossover study usually has one treatment epoch per period, often \
separated by a washout -- take the naming from the protocol ('Period 1', \
'Period 2') and give each its own item.

The study schematic is usually the most reliable source: its horizontal bands \
are the epochs. Where the schematic and the section headings disagree, prefer \
the schematic and record a gap noting the disagreement.

Match `epoch_type` to the permitted values by meaning, not by string similarity. \
A 'Run-in' period is typically a run-in epoch; a 'Post-treatment observation' \
period is a follow-up epoch. If the protocol's period genuinely has no counterpart \
in the list, leave the type empty and record a gap -- it will be recorded as \
sponsor-defined and flagged for review rather than being coded wrongly.

`duration_text` is for the protocol's own phrasing. Do not normalise 'up to 4 \
weeks' into days.""",
    )


def to_usdm(output: OutputModel, ctx: DomainContext) -> dict[str, Any]:
    epochs: list[dict[str, Any]] = []
    for item in output.items:
        if not item.name:
            continue
        key = ids.slug(item.name)
        epochs.append(
            {
                "id": ctx.placeholder("StudyEpoch", key),
                "name": item.name,
                "label": item.label or item.name,
                "description": item.description or item.duration_text or item.name,
                "type": ctx.resolve_code("StudyEpoch", "type", item.epoch_type)
                or ctx.terminology.sponsor_code(item.epoch_type or item.name),
                "instanceType": "StudyEpoch",
            }
        )

    # USDM orders epochs by an explicit doubly-linked chain, not by list position.
    for index, epoch in enumerate(epochs):
        if index > 0:
            epoch["previousId"] = epochs[index - 1]["id"]
        if index < len(epochs) - 1:
            epoch["nextId"] = epochs[index + 1]["id"]

    return {"studyDesign.epochs": epochs} if epochs else {}
