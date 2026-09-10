"""Domain 5 -- StudyIntervention.

The investigational product and its comparators: what is given, in what role,
at what dose, by what route and how often.

`StudyIntervention` lives on `StudyVersion`, not on the design -- a design points
at interventions by id through `studyInterventionIds`. That is because an
amendment can change a dose without the design changing, and because two designs
in one study version can share an intervention.

Dose is the part most likely to be extracted wrongly, because protocols express
it in prose ('3 mg administered as a single actuation into one nostril') rather
than as fields. The model splits that sentence; the numeric value and its unit
are then checked against the unit codelist rather than accepted as written.
"""

from __future__ import annotations

from typing import Any

from pydantic import Field

from ...llm.schemas import DomainOutput, Grounded
from ...usdm import ids
from ..base import DomainContext, compose_prompt


class InterventionItem(Grounded):
    """One study intervention."""

    name: str = Field(
        description="The intervention's name as the protocol gives it, e.g. 'Nasal Glucagon'."
    )
    label: str = Field(default="", description="Display label, if different.")
    description: str = Field(
        default="", description="What this intervention is, in the protocol's words."
    )
    role: str = Field(
        default="",
        description=(
            "The intervention's role in the study, using the permitted wording: "
            "experimental, comparator, placebo, and so on."
        ),
    )
    intervention_type: str = Field(
        default="",
        description="What kind of thing it is -- drug, device, procedure -- permitted wording.",
    )
    product_codes: list[str] = Field(
        default_factory=list,
        description="Sponsor compound codes or abbreviations, e.g. 'LY900018'.",
    )
    dose_value: float | None = Field(
        default=None, description="The numeric dose, if the protocol states one."
    )
    dose_unit: str = Field(
        default="", description="Unit of the dose, e.g. 'mg'. Use the permitted wording."
    )
    dose_text: str = Field(
        default="",
        description="The full dosing sentence verbatim, including anything the fields lose.",
    )
    route: str = Field(
        default="", description="Route of administration, using the permitted wording."
    )
    frequency: str = Field(
        default="", description="Dosing frequency, using the permitted wording."
    )
    duration_text: str = Field(
        default="", description="How long it is given for, as the protocol states it."
    )


PAYLOAD_MODEL = InterventionItem
OutputModel = DomainOutput[InterventionItem]


def build_prompt(ctx: DomainContext) -> str:
    return compose_prompt(
        ctx,
        task=(
            "List the interventions this study administers: the investigational "
            "product, any active comparator, and any placebo.\n\n"
            "Return one item per distinct intervention. Two doses of the same "
            "compound are two interventions if subjects are assigned to one or "
            "the other."
        ),
        guidance="""\
Include comparators and placebo. They are interventions, and a study that gives \
only the investigational product is the exception rather than the rule.

Distinguish the compound from the product. 'LY900018' is a compound code and \
belongs in `product_codes`; 'Nasal Glucagon' is what the protocol calls the \
thing administered and belongs in `name`.

Dose: put the number in `dose_value` and the unit in `dose_unit`, and put the \
whole sentence in `dose_text` regardless. The sentence usually carries \
information the fields cannot hold -- which nostril, over how long, whether it \
may be repeated -- and losing it is worse than duplicating it.

Where the dose varies by arm or by period, create one intervention per distinct \
dose and say in the description which arm it belongs to. Where the dose is \
titrated or weight-based, leave `dose_value` empty, put the rule in `dose_text`, \
and record a gap: a titration is not a single number and pretending otherwise \
is how a wrong dose reaches a database.

Route and frequency must match the permitted values. A protocol's 'intranasally' \
is the nasal route; 'as a single dose' is a frequency of once. If the protocol \
gives no frequency because the product is given once in an acute setting, leave \
it empty rather than inferring a schedule.""",
    )


def to_usdm(output: OutputModel, ctx: DomainContext) -> dict[str, Any]:
    interventions: list[dict[str, Any]] = []
    for item in output.items:
        if not item.name:
            continue
        key = ids.slug(item.name)
        intervention: dict[str, Any] = {
            "id": ctx.placeholder("StudyIntervention", key),
            "name": item.name,
            "label": item.label or item.name,
            "description": item.description or item.dose_text or item.name,
            "role": ctx.resolve_code("StudyIntervention", "role", item.role)
            or ctx.terminology.sponsor_code(item.role or "Not stated"),
            "type": ctx.resolve_code("StudyIntervention", "type", item.intervention_type)
            or ctx.terminology.sponsor_code(item.intervention_type or "Not stated"),
            "instanceType": "StudyIntervention",
        }
        if item.product_codes:
            intervention["codes"] = [
                ctx.terminology.sponsor_code(code) for code in item.product_codes
            ]

        administration = _administration(item, ctx, key)
        if administration:
            intervention["administrations"] = [administration]

        interventions.append(intervention)

    if not interventions:
        return {}
    return {
        "studyVersion.studyInterventions": interventions,
        # The design references interventions by id rather than containing them.
        "studyDesign.studyInterventionIds": [i["id"] for i in interventions],
    }


def _administration(
    item: InterventionItem, ctx: DomainContext, key: str
) -> dict[str, Any] | None:
    """Build the Administration object, if the protocol gave enough to build one."""
    if not (item.dose_value is not None or item.route or item.frequency or item.dose_text):
        return None

    administration: dict[str, Any] = {
        "id": ctx.placeholder("Administration", key),
        "name": f"{item.name} administration",
        "description": item.dose_text or item.name,
        # `duration` is required even when the protocol gives none, so it is
        # always built. `durationWillVary` is the honest answer when the
        # protocol left the duration unstated.
        "duration": {
            "id": ctx.placeholder("Duration", key),
            "text": item.duration_text or "Not stated in the protocol",
            "durationWillVary": not item.duration_text,
            "reasonDurationWillVary": (
                "" if item.duration_text else "The protocol does not state a duration."
            ),
            "instanceType": "Duration",
        },
        "instanceType": "Administration",
    }
    if item.dose_value is not None:
        dose: dict[str, Any] = {
            "id": ctx.placeholder("Quantity", f"{key}-dose"),
            "value": item.dose_value,
            "instanceType": "Quantity",
        }
        unit = ctx.resolve_code("Quantity", "unit", item.dose_unit) if item.dose_unit else None
        if unit:
            dose["unit"] = _alias(ctx, f"{key}-unit", unit)
        administration["dose"] = dose

    # route and frequency are AliasCode, not Code: they wrap a standard code
    # alongside any sponsor aliases for it.
    if item.route:
        route = ctx.resolve_code("Administration", "route", item.route)
        if route:
            administration["route"] = _alias(ctx, f"{key}-route", route)
    if item.frequency:
        frequency = ctx.resolve_code("Administration", "frequency", item.frequency)
        if frequency:
            administration["frequency"] = _alias(ctx, f"{key}-frequency", frequency)
    return administration


def _alias(ctx: DomainContext, key: str, code: dict[str, Any]) -> dict[str, Any]:
    return {
        "id": ctx.placeholder("AliasCode", key),
        "standardCode": code,
        "instanceType": "AliasCode",
    }
