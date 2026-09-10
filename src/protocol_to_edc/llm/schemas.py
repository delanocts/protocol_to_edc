"""Shared shapes for what an agent returns.

Every extracted value carries its own evidence: the page it came from and a
verbatim quote. That is not decoration -- `qc.provenance` checks each quote
against the protocol text, so a value the model inferred rather than read shows
up as an unverifiable quote instead of blending in with the rest.

Why evidence is carried in the payload rather than taken from the API's own
citations: the Messages API rejects `output_config.format` together with
`citations`, so structured output and API citations cannot be combined in one
call. Self-reported evidence that is then verified against the source is in any
case the stronger of the two, because verification is a check we run rather than
a claim we relay.
"""

from __future__ import annotations

from typing import Any, Generic, TypeVar

from pydantic import BaseModel, ConfigDict, Field, field_validator

CONFIDENCE_DESCRIPTION = (
    "How confident you are in this value, from 0.0 to 1.0. Use below 0.8 when "
    "the protocol is ambiguous, when you inferred rather than read the value, "
    "or when more than one reading is defensible. An honest low score is more "
    "useful than a confident guess: low-confidence items are routed to a human "
    "reviewer, not discarded."
)


class Evidence(BaseModel):
    """Where in the protocol a value came from."""

    model_config = ConfigDict(extra="forbid")

    page: int = Field(description="PDF page number the quote appears on, 1-indexed.")
    quote: str = Field(
        description=(
            "A verbatim span copied from that page, long enough to be unique "
            "(at least a dozen characters). Do not paraphrase, correct spelling, "
            "or join text from two places -- the quote is checked against the "
            "PDF text and a reworded quote will be flagged."
        )
    )
    section: str = Field(
        default="",
        description="Protocol section number or heading, e.g. '6.1' or 'Study Design'.",
    )


class Grounded(BaseModel):
    """Mixin for anything an agent extracts: confidence plus evidence."""

    model_config = ConfigDict(extra="forbid")

    # Both are required on purpose. Given a default, the model simply omits them:
    # the first run returned confidence scores but not a single quote, which
    # left the provenance report empty and nothing to verify. A required field
    # is the only reliable way to make grounding non-optional.
    #
    # `confidence` is deliberately unconstrained in the schema -- structured
    # outputs rejects `minimum`/`maximum` on a number -- so the range is stated
    # in the description and clamped below, after parsing.
    confidence: float = Field(description=CONFIDENCE_DESCRIPTION)
    evidence: list[Evidence] = Field(
        description=(
            "One or more quotes from the protocol supporting this item. Required: "
            "give at least one. If you genuinely cannot point at supporting text, "
            "this item does not belong in `items` -- record it as a gap instead."
        )
    )

    @field_validator("confidence")
    @classmethod
    def _clamp(cls, value: float) -> float:
        return min(1.0, max(0.0, float(value)))


class Gap(BaseModel):
    """Something the agent could not determine, and why."""

    model_config = ConfigDict(extra="forbid")

    item: str = Field(description="What could not be determined, in USDM terms.")
    reason: str = Field(description="Why: absent from the protocol, ambiguous, or conflicting.")
    where_to_look: str = Field(
        default="",
        description="Where a human should look, if you have a hint. Section or page.",
    )


PayloadT = TypeVar("PayloadT", bound=BaseModel)


class DomainOutput(BaseModel, Generic[PayloadT]):
    """The envelope every domain agent returns."""

    model_config = ConfigDict(extra="forbid")

    items: list[PayloadT] = Field(
        default_factory=list, description="The entities extracted for this domain."
    )
    gaps: list[Gap] = Field(
        default_factory=list,
        description=(
            "Anything this domain needs that the protocol does not state, or "
            "states ambiguously. Report it here rather than inventing a value."
        ),
    )
    notes: str = Field(
        default="",
        description="Brief reading notes for a reviewer. Not part of the USDM output.",
    )

    def confidence_floor(self) -> float:
        scores = [
            getattr(item, "confidence") for item in self.items if hasattr(item, "confidence")
        ]
        return min(scores) if scores else 1.0

    def all_evidence(self) -> list[tuple[str, Evidence]]:
        out: list[tuple[str, Evidence]] = []
        for item in self.items:
            label = str(getattr(item, "name", "") or getattr(item, "text", "") or "item")
            for piece in getattr(item, "evidence", []) or []:
                out.append((label[:80], piece))
        return out


def strip_grounding(payload: dict[str, Any]) -> dict[str, Any]:
    """Remove confidence/evidence keys, recursively.

    Agent output carries grounding on every item; a USDM document must not. The
    grounding is kept separately for the provenance and gap reports.
    """
    if isinstance(payload, dict):
        return {
            key: strip_grounding(value)
            for key, value in payload.items()
            if key not in {"confidence", "evidence"}
        }
    if isinstance(payload, list):
        return [strip_grounding(item) for item in payload]
    return payload
