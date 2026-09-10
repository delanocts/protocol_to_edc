"""Domain 6 -- Objectives and Endpoints.

What the study is trying to establish, and how it will measure whether it did.

USDM v4 has no `StudyObjective` class. Objectives are `Objective`, they carry
their endpoints as children, and both are levelled -- primary, secondary,
exploratory -- from a published codelist.

The pairing of objective to endpoint is the substance of this domain. Protocols
almost always present them in a two-column table, and the pairing is what a
downstream statistical analysis plan consumes. An objective extracted without
its endpoints is much less useful than one with them.
"""

from __future__ import annotations

from typing import Any

from pydantic import Field

from ...llm.schemas import DomainOutput, Grounded
from ...usdm import ids
from ..base import DomainContext, compose_prompt


class EndpointItem(Grounded):
    """One endpoint belonging to an objective."""

    text: str = Field(description="The endpoint statement, verbatim from the protocol.")
    label: str = Field(default="", description="A short label for the endpoint.")
    level: str = Field(
        default="",
        description="Primary, secondary or exploratory endpoint, in the permitted wording.",
    )
    purpose: str = Field(
        default="", description="What this endpoint establishes, if the protocol says."
    )


class ObjectiveItem(Grounded):
    """One objective and the endpoints that measure it."""

    text: str = Field(description="The objective statement, verbatim from the protocol.")
    label: str = Field(default="", description="A short label, e.g. 'Primary Objective'.")
    level: str = Field(
        default="",
        description="Primary, secondary or exploratory objective, in the permitted wording.",
    )
    endpoints: list[EndpointItem] = Field(
        default_factory=list,
        description=(
            "The endpoints that measure this objective, as the protocol pairs "
            "them. An objective with no stated endpoint gets an empty list and a gap."
        ),
    )


PAYLOAD_MODEL = ObjectiveItem
OutputModel = DomainOutput[ObjectiveItem]


def build_prompt(ctx: DomainContext) -> str:
    return compose_prompt(
        ctx,
        task=(
            "Extract the study's objectives and the endpoints that measure them.\n\n"
            "Return one item per objective, with its endpoints nested inside it. "
            "Keep the protocol's pairing: do not regroup endpoints under a "
            "different objective than the one the protocol places them with."
        ),
        guidance="""\
The objectives table in the synopsis is usually the cleanest source, and its \
two-column layout gives you the pairing directly. Check it against the body \
section, and where they differ prefer the body and record a gap -- synopses are \
routinely left un-amended.

Copy objective and endpoint text verbatim, including its clinical detail. \
'To demonstrate non-inferiority of nasal glucagon to intramuscular glucagon' is \
the objective; shortening it to 'efficacy' destroys what makes it usable.

Level is not always stated per row. Where a table has a 'Primary' header above \
several rows, every row under it inherits that level. Where a protocol lists \
objectives with no levels at all, take the first as primary only if the protocol \
supports that reading, and otherwise leave the level empty with a gap.

An endpoint whose objective is not stated still belongs in the output: attach it \
to the objective it most plainly measures and lower your confidence, or record \
it as a gap if there is no defensible attachment.

Do not merge several endpoints into one item because they share a sentence. \
'Change in glucose at 15, 30 and 45 minutes' is usually one endpoint with three \
time points; 'incidence of AEs and change in glucose' is two endpoints.""",
    )


def to_usdm(output: OutputModel, ctx: DomainContext) -> dict[str, Any]:
    objectives: list[dict[str, Any]] = []
    for index, item in enumerate(output.items, start=1):
        if not item.text:
            continue
        key = ids.slug(item.label or item.text[:40]) or f"objective-{index}"
        objective: dict[str, Any] = {
            "id": ctx.placeholder("Objective", key),
            "name": item.label or f"Objective {index}",
            "label": item.label or f"Objective {index}",
            "text": item.text,
            "level": ctx.resolve_code("Objective", "level", item.level)
            or ctx.terminology.sponsor_code(item.level or "Not stated"),
            "instanceType": "Objective",
        }

        endpoints = []
        for position, endpoint in enumerate(item.endpoints, start=1):
            if not endpoint.text:
                continue
            endpoint_key = f"{key}-endpoint-{position}"
            endpoints.append(
                {
                    "id": ctx.placeholder("Endpoint", endpoint_key),
                    "name": endpoint.label or f"Endpoint {position}",
                    "label": endpoint.label or f"Endpoint {position}",
                    "text": endpoint.text,
                    "purpose": endpoint.purpose or endpoint.text,
                    "level": ctx.resolve_code(
                        "Endpoint", "level", endpoint.level or item.level
                    )
                    or ctx.terminology.sponsor_code(endpoint.level or "Not stated"),
                    "instanceType": "Endpoint",
                }
            )
        if endpoints:
            objective["endpoints"] = endpoints
        objectives.append(objective)

    return {"studyDesign.objectives": objectives} if objectives else {}
