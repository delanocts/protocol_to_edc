"""The gap report -- the reviewer's worklist.

This pipeline is an accelerator with a reviewer, not an autopilot, and this file
is where that shows. It collects everything a human needs to decide, in the order
they should look at it:

1. things that make the document structurally wrong (validation errors)
2. quotes that could not be verified against the protocol
3. values the agent itself flagged as low confidence
4. gaps the agents reported -- what the protocol does not say
5. required content missing because a domain was disabled or empty
6. terminology that fell back to sponsor-defined

Ordering by severity rather than by domain matters: a reviewer with twenty
minutes should spend them on the first section.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Iterable

from ..usdm.assembler import AssemblyReport
from ..usdm.validator import ValidationReport
from .provenance import ProvenanceRow, summarise

MAX_ROWS = 60


def _table(headers: list[str], rows: Iterable[list[str]]) -> list[str]:
    body = list(rows)
    if not body:
        return []
    lines = [
        "| " + " | ".join(headers) + " |",
        "|" + "|".join("---" for _ in headers) + "|",
    ]
    for row in body[:MAX_ROWS]:
        cleaned = [str(cell).replace("|", "\\|").replace("\n", " ")[:220] for cell in row]
        lines.append("| " + " | ".join(cleaned) + " |")
    if len(body) > MAX_ROWS:
        lines.append(f"| ... | {len(body) - MAX_ROWS} more rows omitted |" + " |" * (len(headers) - 2))
    return lines


def build(
    *,
    study_id: str,
    settings: Any,
    results: list[Any],
    assembly: AssemblyReport | None,
    validation: ValidationReport | None,
    provenance_rows: list[ProvenanceRow],
) -> str:
    threshold = settings.qc.min_confidence
    lines: list[str] = [
        f"# Gap report -- {study_id}",
        "",
        f"USDM {settings.usdm.version}, output mode `{settings.usdm.output_mode}`, "
        f"model `{settings.llm.model}` at effort `{settings.llm.effort}`.",
        "",
        "This is a review worklist, ordered by how much each item matters. "
        "Everything below needs a human decision; nothing in it is a failure of "
        "the run.",
        "",
    ]

    # -- summary -----------------------------------------------------------

    ok = sum(1 for r in results if r.ok)
    lines += [
        "## Summary",
        "",
        f"- Domains run: {ok}/{len(results)} succeeded",
        f"- Items extracted: {sum(r.item_count for r in results)}",
        f"- Gaps reported by agents: {sum(len(r.gaps) for r in results)}",
    ]
    if validation:
        lines.append(
            f"- Validation: {len(validation.errors)} error(s), "
            f"{len(validation.warnings)} warning(s)"
        )
    if provenance_rows:
        counts = summarise(provenance_rows)
        lines.append(
            "- Evidence: " + ", ".join(f"{v} {k}" for k, v in counts.items())
        )
    lines.append("")

    # -- 1. structural errors ---------------------------------------------

    if validation and validation.errors:
        lines += [
            "## 1. Structural errors",
            "",
            "The document does not match the USDM schema, or refers to something "
            "that is not in it. These are the only items here that make the output "
            "unusable as it stands.",
            "",
        ]
        lines += _table(
            ["Kind", "Where", "Problem"],
            ([e.kind, e.path, e.message] for e in validation.errors),
        )
        lines.append("")

    # -- 2. unverified evidence -------------------------------------------

    unverified = [r for r in provenance_rows if not r.trustworthy]
    if unverified:
        lines += [
            "## 2. Quotes that could not be verified",
            "",
            "Each agent quotes the protocol text it read a value from, and every "
            "quote is checked against the PDF. The rows below did not match. A "
            "`reworded` quote usually means the value is right but was tidied up; "
            "a `not-found` quote means the value may not be in the protocol at all "
            "and should be checked first.",
            "",
        ]
        lines += _table(
            ["Domain", "Item", "Status", "Claimed page", "Quote"],
            (
                [r.domain, r.item, r.status, r.claimed_page, r.quote]
                for r in sorted(unverified, key=lambda r: (r.status != "not-found", r.domain))
            ),
        )
        lines.append("")

    # -- 3. low confidence -------------------------------------------------

    low = [r for r in results if r.ok and r.min_confidence < threshold]
    if low:
        lines += [
            f"## 3. Low-confidence extractions (below {threshold:.2f})",
            "",
            "The agent flagged its own uncertainty here. These are usually genuine "
            "protocol ambiguities rather than mistakes.",
            "",
        ]
        lines += _table(
            ["Domain", "Lowest confidence", "Items"],
            ([r.label, f"{r.min_confidence:.2f}", r.item_count] for r in low),
        )
        lines.append("")

    # -- 4. agent-reported gaps -------------------------------------------

    gap_rows = [
        [r.label, g.item, g.reason, g.where_to_look] for r in results for g in r.gaps
    ]
    if gap_rows:
        lines += [
            "## 4. What the protocol does not settle",
            "",
            "Reported by the agents rather than guessed at. Each needs a decision "
            "from someone who can consult the sponsor or the wider protocol set.",
            "",
        ]
        lines += _table(["Domain", "Item", "Why", "Where to look"], gap_rows)
        lines.append("")

    # -- 5. missing required content --------------------------------------

    if assembly and assembly.missing:
        lines += [
            "## 5. Required USDM content that is absent",
            "",
            "USDM marks these properties required. They are missing because the "
            "domain that produces them is disabled, or because it produced nothing.",
            "",
        ]
        lines += _table(
            ["Entity", "Property", "Why", "Stubbed"],
            (
                [m.entity, m.property, m.reason, "yes" if m.stubbed else "no"]
                for m in assembly.missing
            ),
        )
        lines.append("")

    if assembly and assembly.dangling:
        lines += [
            "### References that point at nothing",
            "",
            "Something referred to an entity that no enabled domain produced.",
            "",
        ]
        lines += _table(
            ["Reference", "Used at"],
            ([token, "; ".join(places[:3])] for token, places in assembly.dangling.items()),
        )
        lines.append("")

    # -- 6. sponsor-defined terminology -----------------------------------

    if validation and validation.warnings:
        lines += [
            "## 6. Values recorded as sponsor-defined",
            "",
            "No published CDISC codelist matched, so the value was kept as the "
            "protocol worded it rather than coded. Sometimes correct, sometimes a "
            "sign the wrong codelist was consulted.",
            "",
        ]
        lines += _table(
            ["Where", "Value"],
            ([w.path, w.message] for w in validation.warnings),
        )
        lines.append("")

    # -- failures ----------------------------------------------------------

    failed = [r for r in results if not r.ok]
    if failed:
        lines += ["## Domains that failed to run", ""]
        lines += _table(["Domain", "Error"], ([r.label, r.error] for r in failed))
        lines.append("")

    if len(lines) <= 12:
        lines.append("Nothing to review: no gaps, no errors, every quote verified.")

    return "\n".join(lines).rstrip() + "\n"


def write(path: Path, **kwargs: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(build(**kwargs), encoding="utf-8")
