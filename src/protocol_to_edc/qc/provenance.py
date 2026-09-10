"""Verify what each agent claimed to have read.

Every extracted item carries a page number and a verbatim quote. This module
checks each quote against the protocol's text layer and records the outcome.

The check is the difference between "the model says it read this in the protocol"
and "this is in the protocol". A quote that cannot be found is the clearest
available signal that a value was inferred, remembered or invented rather than
read, and it costs nothing to test.

Outcomes:

    verified      the quote is in the protocol, on the page the agent named
    page-shifted  the quote is there, on a different page
    reworded      the opening of the quote is there but the rest was rewritten
    not-found     the quote is not in the document at all
    unverifiable  too short to test meaningfully
"""

from __future__ import annotations

import csv
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable

from ..pdf.extract import ProtocolText

VERIFIED = "verified"
PAGE_SHIFTED = "page-shifted"
REWORDED = "reworded"
NOT_FOUND = "not-found"
UNVERIFIABLE = "unverifiable"

TRUSTWORTHY = frozenset({VERIFIED, PAGE_SHIFTED})


@dataclass
class ProvenanceRow:
    domain: str
    item: str
    claimed_page: int
    found_pages: tuple[int, ...]
    status: str
    confidence: float
    section: str
    quote: str
    note: str = ""

    @property
    def trustworthy(self) -> bool:
        return self.status in TRUSTWORTHY

    def as_dict(self) -> dict[str, Any]:
        return {
            "domain": self.domain,
            "item": self.item,
            "claimedPage": self.claimed_page,
            "foundPages": ";".join(str(p) for p in self.found_pages),
            "status": self.status,
            "confidence": round(self.confidence, 2),
            "section": self.section,
            "quote": self.quote,
            "note": self.note,
        }


def verify_output(domain_id: str, output: Any, protocol: ProtocolText) -> list[ProvenanceRow]:
    """Check every quote in one domain's output."""
    rows: list[ProvenanceRow] = []
    for label, evidence in output.all_evidence():
        match = protocol.find_quote(evidence.quote, evidence.page)
        if match.found:
            status = VERIFIED if match.exact_page else PAGE_SHIFTED
        elif match.pages:
            status = REWORDED
        elif "too short" in match.reason:
            status = UNVERIFIABLE
        else:
            status = NOT_FOUND

        confidence = 1.0
        for item in output.items:
            if str(getattr(item, "name", "") or getattr(item, "text", ""))[:80] == label:
                confidence = float(getattr(item, "confidence", 1.0))
                break

        rows.append(
            ProvenanceRow(
                domain=domain_id,
                item=label,
                claimed_page=evidence.page,
                found_pages=match.pages[:5],
                status=status,
                confidence=confidence,
                section=evidence.section,
                quote=evidence.quote[:300],
                note=match.reason,
            )
        )
    return rows


def verify_all(
    outputs: dict[str, Any], protocol: ProtocolText
) -> list[ProvenanceRow]:
    rows: list[ProvenanceRow] = []
    for domain_id, output in outputs.items():
        if output is not None:
            rows.extend(verify_output(domain_id, output, protocol))
    return rows


def summarise(rows: Iterable[ProvenanceRow]) -> dict[str, int]:
    counts: dict[str, int] = {}
    for row in rows:
        counts[row.status] = counts.get(row.status, 0) + 1
    return dict(sorted(counts.items()))


def write_csv(rows: list[ProvenanceRow], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = [
        "domain",
        "item",
        "claimedPage",
        "foundPages",
        "status",
        "confidence",
        "section",
        "quote",
        "note",
    ]
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow(row.as_dict())
