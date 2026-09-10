"""Slice the USDM Implementation Guide into per-entity excerpts.

The IG is 119 pages. Sending it to every agent would cost more than the protocol
does and bury the relevant paragraph in ninety pages of unrelated modelling
guidance. So it is cut up once, offline, into an excerpt per entity, and each
domain manifest names the excerpts its agent needs.

Selection is by paragraph rather than by section heading, because the IG
discusses an entity in several places -- its own section, the worked examples,
and the modelling notes for entities that reference it -- and the examples are
often the most useful part.

    python -m protocol_to_edc.usdm.slice_ig
"""

from __future__ import annotations

import argparse
import re
from dataclasses import dataclass
from pathlib import Path

from pypdf import PdfReader

from ..core import paths, registry

# Every page repeats these; they add nothing and would dominate a keyword score.
_BOILERPLATE = re.compile(
    r"^(CDISC Unified Study Definitions Model|© \d{4} Clinical Data Interchange|"
    r"\d{4}-\d{2}-\d{2}\s*$|Page \d+\s*$)",
    re.IGNORECASE,
)
_TOC_LINE = re.compile(r"\.{6,}\s*\d+\s*$")
_WHITESPACE = re.compile(r"[ \t]+")

MIN_PARAGRAPH = 90
MAX_EXCERPT_CHARS = 6000


@dataclass
class Paragraph:
    page: int
    text: str

    def mentions(self, entity: str) -> int:
        return len(re.findall(rf"\b{re.escape(entity)}\b", self.text))


def _clean_page(text: str) -> str:
    lines = []
    for line in (text or "").splitlines():
        stripped = line.strip()
        if not stripped or _BOILERPLATE.match(stripped) or _TOC_LINE.search(stripped):
            continue
        lines.append(_WHITESPACE.sub(" ", stripped))
    return "\n".join(lines)


def read_paragraphs(pdf_path: Path) -> list[Paragraph]:
    reader = PdfReader(str(pdf_path))
    paragraphs: list[Paragraph] = []
    for number, page in enumerate(reader.pages, start=1):
        cleaned = _clean_page(page.extract_text() or "")
        if not cleaned:
            continue
        # The IG's paragraphs survive extraction as runs of lines; a blank line or
        # a numbered heading starts a new one.
        chunks = re.split(r"\n(?=\d+(?:\.\d+)*\s+[A-Z])|\n{2,}", cleaned)
        buffer = ""
        for chunk in chunks:
            chunk = chunk.strip()
            if not chunk:
                continue
            buffer = f"{buffer}\n{chunk}".strip() if buffer else chunk
            if len(buffer) >= MIN_PARAGRAPH:
                paragraphs.append(Paragraph(number, buffer))
                buffer = ""
        if buffer:
            paragraphs.append(Paragraph(number, buffer))
    return paragraphs


def excerpt_for(entity: str, paragraphs: list[Paragraph], limit: int) -> str:
    """The most entity-dense paragraphs, in document order, up to `limit` chars."""
    scored = [(p.mentions(entity), p) for p in paragraphs]
    relevant = [(score, p) for score, p in scored if score > 0]
    if not relevant:
        return ""

    # Rank by density so a paragraph *about* the entity beats one that mentions it
    # in passing, then restore document order for readability.
    ranked = sorted(
        relevant, key=lambda pair: (-pair[0] / max(len(pair[1].text), 1), pair[1].page)
    )
    chosen: list[Paragraph] = []
    total = 0
    for _, paragraph in ranked:
        if total + len(paragraph.text) > limit:
            continue
        chosen.append(paragraph)
        total += len(paragraph.text)
        if total >= limit * 0.9:
            break

    chosen.sort(key=lambda p: p.page)
    lines = [f"# {entity} -- from the USDM Implementation Guide v4.0", ""]
    for paragraph in chosen:
        lines.append(f"_(IG page {paragraph.page})_")
        lines.append(paragraph.text)
        lines.append("")
    return "\n".join(lines)


def wanted_entities() -> list[str]:
    """Every entity any domain manifest asks for, plus the ones they produce."""
    names: set[str] = set()
    for spec in registry.load_all():
        names.update(spec.ig_sections)
        names.update(spec.produces)
    return sorted(names)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Slice the USDM IG per entity")
    parser.add_argument("--ig", type=Path, default=paths.USDM_IG_PDF)
    parser.add_argument("--out", type=Path, default=paths.USDM_IG_SECTIONS)
    parser.add_argument("--limit", type=int, default=MAX_EXCERPT_CHARS)
    args = parser.parse_args(argv)

    if not args.ig.is_file():
        parser.error(f"Implementation Guide not found at {args.ig}")

    paragraphs = read_paragraphs(args.ig)
    print(f"read {len(paragraphs)} paragraphs from {args.ig.name}")

    args.out.mkdir(parents=True, exist_ok=True)
    written = 0
    empty: list[str] = []
    for entity in wanted_entities():
        text = excerpt_for(entity, paragraphs, args.limit)
        if not text:
            empty.append(entity)
            continue
        (args.out / f"{entity}.md").write_text(text, encoding="utf-8")
        written += 1
        print(f"  {entity:32} {len(text):6,} chars")

    print(f"\nwrote {written} excerpts to {args.out.relative_to(paths.PROJECT_ROOT)}")
    if empty:
        print(f"  no IG text found for: {', '.join(empty)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
