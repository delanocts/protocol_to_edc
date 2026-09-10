"""Domain 1 -- Study.

Study identity: the titles, the identifiers that name the study, the sponsor,
and the therapeutic area.

Two things about USDM v4 shape this domain and routinely surprise people coming
from the entity list in a statement of work:

* Titles and identifiers do not hang off `Study`. They belong to `StudyVersion`,
  because a protocol amendment can retitle a study without it becoming a
  different study.
* Therapeutic area and phase are properties of the *design*, not of the study.
  This domain extracts the therapeutic area and hands it to the study version's
  `businessTherapeuticAreas`; the design agent codes the phase.
"""

from __future__ import annotations

from typing import Any

from pydantic import Field

from ...llm.schemas import DomainOutput, Grounded
from ..base import DomainContext, compose_prompt

TITLE_TYPES = "Official Study Title, Brief Study Title, Study Acronym, Scientific Study Title"


class StudyIdentity(Grounded):
    """One named or coded fact about the study's identity."""

    official_title: str = Field(
        default="",
        description="The full official title, exactly as printed on the title page.",
    )
    brief_title: str = Field(
        default="", description="A short public title, if the protocol gives one."
    )
    acronym: str = Field(default="", description="Study acronym, if any.")
    protocol_identifier: str = Field(
        default="", description="The sponsor's protocol number, e.g. 'I8R-JE-IGBJ'."
    )
    registry_identifiers: list[str] = Field(
        default_factory=list,
        description="Public registry ids: NCT, EudraCT, jRCT, ISRCTN. Values only.",
    )
    sponsor_name: str = Field(default="", description="The sponsor organisation's legal name.")
    therapeutic_areas: list[str] = Field(
        default_factory=list,
        description="Therapeutic area(s), in the protocol's wording, e.g. 'Diabetes Mellitus'.",
    )
    version_identifier: str = Field(
        default="",
        description="Protocol version or amendment label, e.g. 'Amendment (a)' or '3.0'.",
    )
    version_rationale: str = Field(
        default="",
        description=(
            "Why this version exists. For an amendment, the stated reason for it; "
            "for an original protocol, say so."
        ),
    )


PAYLOAD_MODEL = StudyIdentity
OutputModel = DomainOutput[StudyIdentity]


def build_prompt(ctx: DomainContext) -> str:
    return compose_prompt(
        ctx,
        task=(
            "Identify this study: its titles, the identifiers that name it, the "
            "sponsor, the therapeutic area, and which protocol version this "
            "document is.\n\n"
            "Return a single item -- a study has one identity. If the protocol "
            "gives several titles (official, brief, acronym), put each in its own "
            "field rather than choosing between them."
        ),
        guidance=f"""\
The official title is the long one on the title page, reproduced word for word \
including the compound code and any parenthetical. Do not shorten it.

Protocol identifier is the sponsor's own number ({ctx.settings.study.protocol_number or 'e.g. I8R-JE-IGBJ'}), \
not the registry number. Registry identifiers are the public ones -- NCT, \
EudraCT, jRCT, ISRCTN -- and there may be more than one, or none.

Sponsor is the legal entity that holds the protocol. A local affiliate \
('Eli Lilly Japan K.K.') is the sponsor if that is what the protocol says, even \
when a parent company is named elsewhere in the document.

Version identifier is how the protocol labels itself: 'Amendment (a)', \
'Version 3.0', 'Original Protocol'. Look at the title page header and footer, \
which often carry it when the body does not.

Therapeutic area is the disease area under study, in the protocol's words. It is \
not the intervention and not the indication statement -- for a hypoglycaemia \
rescue study in diabetic patients, the therapeutic area is the diabetes/endocrine \
area, and the acute condition treated belongs to the indication.

Title types available when coding: {TITLE_TYPES}.""",
    )


def to_usdm(output: OutputModel, ctx: DomainContext) -> dict[str, Any]:
    """Build the study-identity fragments.

    Returns a mapping of anchor target -> payload, because this domain populates
    several places at once: titles and identifiers on the study version, the
    sponsor as an organisation, and the therapeutic areas alongside them.
    """
    if not output.items:
        return {}
    item = output.items[0]

    titles = []
    for value, decode, key in (
        (item.official_title, "Official Study Title", "official"),
        (item.brief_title, "Brief Study Title", "brief"),
        (item.acronym, "Study Acronym", "acronym"),
    ):
        if not value:
            continue
        titles.append(
            {
                "id": ctx.placeholder("StudyTitle", key),
                "text": value,
                "type": ctx.resolve_code("StudyTitle", "type", decode),
                "instanceType": "StudyTitle",
            }
        )

    organizations = []
    identifiers = []
    if item.protocol_identifier:
        sponsor_name = item.sponsor_name or "Sponsor"
        organizations.append(
            {
                "id": ctx.placeholder("Organization", "sponsor"),
                "name": sponsor_name,
                "label": sponsor_name,
                "type": ctx.resolve_code("Organization", "type", "Pharmaceutical Company"),
                "identifierScheme": "Sponsor",
                "identifier": item.protocol_identifier,
                "instanceType": "Organization",
            }
        )
        identifiers.append(
            {
                "id": ctx.placeholder("StudyIdentifier", "sponsor"),
                "text": item.protocol_identifier,
                "scopeId": ctx.placeholder("Organization", "sponsor"),
                "instanceType": "StudyIdentifier",
            }
        )

    for index, registry_id in enumerate(item.registry_identifiers, start=1):
        organizations.append(
            {
                "id": ctx.placeholder("Organization", f"registry-{index}"),
                "name": _registry_name(registry_id),
                "label": _registry_name(registry_id),
                "type": ctx.resolve_code("Organization", "type", "Clinical Study Registry"),
                "identifierScheme": _registry_name(registry_id),
                "identifier": registry_id,
                "instanceType": "Organization",
            }
        )
        identifiers.append(
            {
                "id": ctx.placeholder("StudyIdentifier", f"registry-{index}"),
                "text": registry_id,
                "scopeId": ctx.placeholder("Organization", f"registry-{index}"),
                "instanceType": "StudyIdentifier",
            }
        )

    fragment: dict[str, Any] = {}
    if titles:
        fragment["studyVersion.titles"] = titles
    if identifiers:
        fragment["studyVersion.studyIdentifiers"] = identifiers
    if organizations:
        fragment["studyVersion.organizations"] = organizations
    if item.therapeutic_areas:
        fragment["studyVersion.businessTherapeuticAreas"] = [
            ctx.terminology.sponsor_code(area) for area in item.therapeutic_areas
        ]
    return fragment


def _registry_name(identifier: str) -> str:
    upper = identifier.upper()
    if upper.startswith("NCT"):
        return "ClinicalTrials.gov"
    if upper.startswith("JRCT"):
        return "jRCT"
    if upper.startswith("ISRCTN"):
        return "ISRCTN"
    if "-" in identifier and identifier[:4].isdigit():
        return "EudraCT"
    return "Clinical Study Registry"
