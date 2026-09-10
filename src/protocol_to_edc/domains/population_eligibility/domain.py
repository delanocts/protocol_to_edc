"""Domain 7 -- Population and Eligibility Criteria.

Who the study plans to enrol, and the inclusion and exclusion criteria that
decide it.

USDM v4 splits eligibility across two levels, which is easy to get wrong:

* `EligibilityCriterionItem` holds the criterion *text*, and lives on
  `StudyVersion`.
* `EligibilityCriterion` holds the criterion's *role* in a design -- its
  category, its number, its position in the list -- and lives on the design,
  pointing back at the item by `criterionItemId`.

The split exists so two designs in one study can share a criterion's wording
while numbering it differently. This module produces both halves and links them.
"""

from __future__ import annotations

from typing import Any

from pydantic import Field

from ...llm.schemas import DomainOutput, Grounded
from ..base import DomainContext, compose_prompt


class CriterionItem(Grounded):
    """One inclusion or exclusion criterion."""

    identifier: str = Field(
        description="The criterion's number as printed, e.g. '1' or 'E3'."
    )
    category: str = Field(
        default="",
        description="Inclusion Criteria or Exclusion Criteria, in the permitted wording.",
    )
    text: str = Field(
        description=(
            "The criterion's full text, verbatim. Keep sub-clauses and "
            "parenthetical values -- thresholds are the point of a criterion."
        )
    )


class PopulationItem(Grounded):
    """The planned study population."""

    name: str = Field(default="Study Population", description="A name for the population.")
    description: str = Field(
        default="", description="The population in the protocol's own words."
    )
    includes_healthy_subjects: bool = Field(
        default=False,
        description=(
            "Whether healthy volunteers may enrol. False for a patient population. "
            "This is required by USDM, so decide it rather than leaving it."
        ),
    )
    planned_enrolment: int | None = Field(
        default=None, description="Total number of subjects planned to enrol."
    )
    planned_completion: int | None = Field(
        default=None, description="Number planned to complete, if stated separately."
    )
    planned_sex: str = Field(
        default="", description="Sex of participants, in the permitted wording."
    )
    minimum_age: str = Field(
        default="", description="Minimum age with its unit, e.g. '20 years'."
    )
    maximum_age: str = Field(default="", description="Maximum age with its unit, if any.")
    criteria: list[CriterionItem] = Field(
        default_factory=list,
        description="Every inclusion and exclusion criterion, in the protocol's order.",
    )


PAYLOAD_MODEL = PopulationItem
OutputModel = DomainOutput[PopulationItem]


def build_prompt(ctx: DomainContext) -> str:
    return compose_prompt(
        ctx,
        task=(
            "Extract the planned population and every eligibility criterion.\n\n"
            "Return a single item for the population, with all criteria in its "
            "`criteria` list, in the order the protocol prints them."
        ),
        guidance="""\
Extract every criterion, not a summary. A protocol with 28 criteria produces 28 \
items. This is the single most volume-sensitive domain in the pipeline and a \
truncated list is worse than an obviously empty one, because it looks complete.

Copy criterion text verbatim, thresholds included. 'HbA1c less than or equal to \
10%' is the criterion; 'adequate glycaemic control' is not. Keep sub-clauses, \
units and parenthetical qualifications exactly as printed.

Keep the protocol's own numbering in `identifier`. Where inclusion and exclusion \
lists each restart at 1, that is fine -- the category distinguishes them.

`includes_healthy_subjects` is required by USDM and has no 'unknown'. A study \
enrolling patients with a diagnosed condition is false; a phase 1 study in \
healthy volunteers is true. Where a study enrols both, choose true and explain \
in the description.

Age: give the value with its unit as the protocol states it ('20 years', \
'6 months'). Do not convert. If only a minimum is set, leave the maximum empty \
rather than inventing an upper bound.

If enrolment is expressed as a range or a target with a cap ('approximately 60, \
up to 72'), put the primary planned number in `planned_enrolment` and the full \
phrasing in the description.""",
    )


def to_usdm(output: OutputModel, ctx: DomainContext) -> dict[str, Any]:
    if not output.items:
        return {}
    item = output.items[0]

    criterion_items: list[dict[str, Any]] = []
    criteria: list[dict[str, Any]] = []
    for position, criterion in enumerate(item.criteria, start=1):
        if not criterion.text:
            continue
        category_code = ctx.resolve_code(
            "EligibilityCriterion", "category", criterion.category
        ) or ctx.terminology.sponsor_code(criterion.category or "Not stated")
        prefix = "inclusion" if "inclu" in criterion.category.lower() else "exclusion"
        key = f"{prefix}-{criterion.identifier or position}"

        criterion_items.append(
            {
                "id": ctx.placeholder("EligibilityCriterionItem", key),
                "name": f"{criterion.category or 'Criterion'} {criterion.identifier or position}",
                "text": criterion.text,
                "instanceType": "EligibilityCriterionItem",
            }
        )
        criteria.append(
            {
                "id": ctx.placeholder("EligibilityCriterion", key),
                "name": f"{criterion.category or 'Criterion'} {criterion.identifier or position}",
                "label": criterion.identifier or str(position),
                "identifier": criterion.identifier or str(position),
                "category": category_code,
                # The text lives on the study version; the design points at it.
                "criterionItemId": ctx.placeholder("EligibilityCriterionItem", key),
                "instanceType": "EligibilityCriterion",
            }
        )

    # USDM chains criteria in order, as it does epochs.
    for index, criterion in enumerate(criteria):
        if index > 0:
            criterion["previousId"] = criteria[index - 1]["id"]
        if index < len(criteria) - 1:
            criterion["nextId"] = criteria[index + 1]["id"]

    population: dict[str, Any] = {
        "id": ctx.placeholder("StudyDesignPopulation", "main"),
        "name": item.name or "Study Population",
        "label": item.name or "Study Population",
        "description": item.description or item.name or "Study population",
        "includesHealthySubjects": item.includes_healthy_subjects,
        "instanceType": "StudyDesignPopulation",
    }
    if item.planned_enrolment is not None:
        population["plannedEnrollmentNumber"] = _range(ctx, "enrolment", item.planned_enrolment)
    if item.planned_completion is not None:
        population["plannedCompletionNumber"] = _range(
            ctx, "completion", item.planned_completion
        )
    if item.planned_sex:
        sex = ctx.resolve_code("StudyDesignPopulation", "plannedSex", item.planned_sex)
        if sex:
            population["plannedSex"] = [sex]
    if criteria:
        population["criterionIds"] = [c["id"] for c in criteria]

    fragment: dict[str, Any] = {"studyDesign.population": population}
    if criteria:
        fragment["studyDesign.eligibilityCriteria"] = criteria
        fragment["studyVersion.eligibilityCriterionItems"] = criterion_items
    return fragment


def _range(ctx: DomainContext, key: str, value: int) -> dict[str, Any]:
    """USDM expresses a planned number as a Range, not a bare integer."""
    quantity = {
        "id": ctx.placeholder("Quantity", f"{key}-value"),
        "value": float(value),
        "instanceType": "Quantity",
    }
    return {
        "id": ctx.placeholder("Range", key),
        "minValue": quantity,
        "maxValue": {**quantity, "id": ctx.placeholder("Quantity", f"{key}-max")},
        "isApproximate": True,
        "instanceType": "Range",
    }
