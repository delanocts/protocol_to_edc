"""Protocol PDF text extraction and quote verification.

The pipeline asks every agent to quote the protocol text it extracted a value
from, and to say which page it came from. This module is what makes that claim
checkable: it holds the protocol's text per page and can confirm that a quoted
span really does appear where the agent said it does.

An unverifiable quote is the strongest signal available that a value was inferred
rather than read, so verification results go straight into the gap report.

Matching is deliberately tolerant. PDF text layers break words across lines,
double up spaces, and use typographic dashes and quotes where the model will
write ASCII, so both sides are normalised aggressively before comparison.
"""

from __future__ import annotations

import re
import unicodedata
from dataclasses import dataclass
from functools import cached_property
from pathlib import Path

from pypdf import PdfReader

# Characters a PDF renders one way and a model reproduces another.
_TRANSLATIONS = str.maketrans(
    {
        "‐": "-", "‑": "-", "‒": "-", "–": "-", "—": "-",
        "‘": "'", "’": "'", "‚": "'", "‛": "'",
        "“": '"', "”": '"', "„": '"',
        " ": " ", " ": " ", " ": " ", "​": "",
        "­": "", "ﬁ": "fi", "ﬂ": "fl",
    }
)

_WHITESPACE = re.compile(r"\s+")
_NON_MATCHING = re.compile(r"[^a-z0-9 ]+")

MIN_QUOTE_LENGTH = 12


def normalise(text: str) -> str:
    """Fold text to a form where a PDF and a model agree: lowercase alphanumerics."""
    folded = unicodedata.normalize("NFKC", text or "").translate(_TRANSLATIONS)
    folded = _NON_MATCHING.sub(" ", folded.lower())
    return _WHITESPACE.sub(" ", folded).strip()


@dataclass(frozen=True)
class QuoteMatch:
    found: bool
    pages: tuple[int, ...]
    exact_page: bool
    reason: str = ""

    @property
    def best_page(self) -> int | None:
        return self.pages[0] if self.pages else None


class ProtocolText:
    """The text layer of one protocol PDF, addressable by page (1-indexed)."""

    def __init__(self, path: Path, pages: list[str]) -> None:
        self.path = path
        self.pages = pages

    @classmethod
    def load(cls, path: Path) -> ProtocolText:
        reader = PdfReader(str(path))
        pages = [(page.extract_text() or "") for page in reader.pages]
        return cls(path, pages)

    def __len__(self) -> int:
        return len(self.pages)

    @property
    def character_count(self) -> int:
        return sum(len(p) for p in self.pages)

    @property
    def has_text_layer(self) -> bool:
        """False for a scanned PDF, which is out of scope: no OCR in this pipeline."""
        if not self.pages:
            return False
        empty = sum(1 for p in self.pages if len(p.strip()) < 50)
        return self.character_count > 5000 and empty < len(self.pages) * 0.5

    def page_text(self, page: int) -> str:
        """1-indexed page text, or '' if out of range."""
        return self.pages[page - 1] if 1 <= page <= len(self.pages) else ""

    @cached_property
    def _normalised(self) -> list[str]:
        return [normalise(p) for p in self.pages]

    def find_quote(self, quote: str, page: int | None = None) -> QuoteMatch:
        """Check that `quote` appears in the protocol, ideally on `page`.

        A page one or two either side still counts as found -- page numbering in
        a protocol's own text often differs from the PDF's physical page order --
        but `exact_page` records whether the agent's page was right.
        """
        needle = normalise(quote)
        if len(needle) < MIN_QUOTE_LENGTH:
            return QuoteMatch(False, (), False, "quote too short to verify")

        hits = tuple(i + 1 for i, text in enumerate(self._normalised) if needle in text)
        if hits:
            return QuoteMatch(True, hits, page in hits if page else False)

        # Fall back to the longest leading fragment that does appear, which
        # distinguishes "reworded slightly" from "not in the document at all".
        words = needle.split()
        for size in range(min(len(words), 12), 5, -1):
            fragment = " ".join(words[:size])
            partial = tuple(
                i + 1 for i, text in enumerate(self._normalised) if fragment in text
            )
            if partial:
                return QuoteMatch(
                    False,
                    partial,
                    page in partial if page else False,
                    f"only the first {size} words match; the quote was reworded",
                )

        return QuoteMatch(False, (), False, "not found anywhere in the protocol")

    def window(self, page: int, radius: int = 0) -> str:
        """Text of `page`, optionally with neighbouring pages, for prompting."""
        first = max(1, page - radius)
        last = min(len(self.pages), page + radius)
        return "\n\n".join(
            f"[page {n}]\n{self.page_text(n)}" for n in range(first, last + 1)
        )

    def outline(self, max_chars: int = 90) -> list[tuple[int, str]]:
        """First meaningful line of each page: a cheap map of the document."""
        result = []
        for index, text in enumerate(self.pages, start=1):
            line = next(
                (ln.strip() for ln in text.splitlines() if len(ln.strip()) > 3), ""
            )
            result.append((index, line[:max_chars]))
        return result
