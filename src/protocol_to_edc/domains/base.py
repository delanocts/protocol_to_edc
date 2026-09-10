"""Shared scaffolding for domain agents.

A domain module supplies three things: what it extracts (`PAYLOAD_MODEL`), what
to ask for (`build_prompt`), and how to turn the answer into USDM (`to_usdm`).
Everything common to all eight -- the system prompt, the terminology and schema
material, the coding rules, the evidence requirement -- lives here, so a domain
module stays about its own subject matter.

The system prompt is built to be byte-identical across domains, because it is
the prompt-cached prefix: the first agent pays to place it and the protocol in
the cache, and the remaining seven read them back cheaply. Anything that varies
per domain therefore goes in the user message, never the system prompt.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from ..core.config import Settings
from ..core.registry import DomainSpec
from ..pdf.extract import ProtocolText
from ..usdm import ct as ct_module
from ..usdm import ids
from ..usdm.schema import UsdmSchema

SYSTEM_PROMPT = """\
You extract structured study design information from clinical trial protocols \
and express it as CDISC USDM, the Unified Study Definitions Model.

How to work:

- The protocol is the only source of truth. If it does not state something, say \
so in `gaps` rather than supplying a plausible value. A gap a reviewer can close \
in a minute costs far less than a wrong value that reaches a database build.
- Quote what you read. Every item carries `evidence`: the page number and a \
verbatim span from that page. Quotes are checked against the PDF text, so copy \
them exactly rather than paraphrasing or tidying them up.
- Score yourself honestly in `confidence`. Below 0.8 means a reviewer should \
look. Protocols are ambiguous in places and a low score on a genuinely ambiguous \
point is the correct answer, not a failure.
- Prefer the protocol's own wording for names and text. Do not translate a \
sponsor's terms into what you think they should have written.
- Read the whole protocol, not just the section named in the task. Study design \
information is routinely split between the synopsis, the design section, the \
schedule of activities and the appendices, and the synopsis is often out of date \
relative to the body.
- Where a coded value is asked for, choose from the permitted values given to \
you, by their exact wording. Never invent a code. If nothing fits, leave it \
empty and record a gap; a value outside the codelist is worse than an absent one.

You are the drafting half of a two-part process: a human reviews everything you \
produce. Make their review easy by being explicit about what you were unsure of."""


@dataclass
class DomainContext:
    """Everything a domain module needs to build its prompt and its fragment."""

    settings: Settings
    spec: DomainSpec
    schema: UsdmSchema
    terminology: ct_module.Terminology
    protocol: ProtocolText
    upstream: dict[str, Any] = field(default_factory=dict)
    ig_excerpt: str = ""

    @property
    def system_prompt(self) -> str:
        """Identical for every domain, so it stays a cacheable prefix."""
        return SYSTEM_PROMPT

    # -- helpers for prompt building ---------------------------------------

    def schema_block(self, entities: tuple[str, ...] | list[str] | None = None) -> str:
        names = list(entities or self.spec.produces)
        available = [n for n in names if self.schema.has_entity(n)]
        return self.schema.describe_many(available) if available else ""

    def terminology_block(self) -> str:
        return self.terminology.render(self.spec.ct_codelists)

    def definitions_block(self, entities: tuple[str, ...] | list[str] | None = None) -> str:
        lines = []
        for entity in entities or self.spec.produces:
            definition = self.terminology.definition(entity)
            if definition:
                lines.append(f"{entity}: {definition}")
        return "\n".join(lines)

    def study_hint(self) -> str:
        meta = self.settings.study
        known = [
            f"{label}: {value}"
            for label, value in (
                ("Protocol number", meta.protocol_number),
                ("Protocol version", meta.protocol_version),
                ("Sponsor", meta.sponsor),
                ("Registry id", meta.registry_id),
            )
            if value
        ]
        if not known:
            return ""
        return (
            "Study metadata recorded in the run configuration (confirm against "
            "the protocol; the protocol wins if they disagree):\n  "
            + "\n  ".join(known)
        )

    def resolve_code(self, entity: str, attribute: str, decode: str) -> dict[str, Any] | None:
        """Terminology lookup with a sponsor fallback, so no code is ever invented."""
        if not decode:
            return None
        return self.terminology.resolve(entity, attribute, decode) or (
            self.terminology.sponsor_code(decode)
        )

    def placeholder(self, entity: str, key: str) -> str:
        return ids.placeholder(entity, key)


def compose_prompt(ctx: DomainContext, task: str, *, guidance: str = "") -> str:
    """Assemble the user-message instruction from the domain's own material.

    Order is deliberate: what to do, then the reference material, then the
    output contract. The domain-specific task comes first because it is what
    the rest is in service of.
    """
    sections: list[tuple[str, str]] = [
        ("Your task", task.strip()),
        ("Where to look in the protocol", "\n".join(f"- {h}" for h in ctx.spec.protocol_hints)),
        ("Study context", ctx.study_hint()),
        ("What these USDM entities mean", ctx.definitions_block()),
        ("USDM entity structure you are filling in", ctx.schema_block()),
        ("Permitted coded values", ctx.terminology_block()),
        ("From the USDM Implementation Guide", ctx.ig_excerpt.strip()),
        ("Domain guidance", guidance.strip()),
        ("Skill", ctx.spec.load_skill().strip()),
    ]
    parts = [f"## {title}\n\n{body}" for title, body in sections if body and body.strip()]
    parts.append(
        "## Output\n\n"
        "Return every entity you found in `items`. Put anything the protocol "
        "does not settle in `gaps`. Do not leave `items` empty just because the "
        "protocol is unclear -- extract what is stated and record the rest as gaps."
    )
    return "\n\n".join(parts)
