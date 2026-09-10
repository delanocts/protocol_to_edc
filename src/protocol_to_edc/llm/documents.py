"""Upload the protocol once, reference it from every agent.

Eight agents read the same 73-page PDF. Sending the file with each request would
mean uploading it eight times and paying full input price for it eight times.

The Files API solves the upload half: the PDF goes up once and every request
refers to it by `file_id`. Prompt caching solves the cost half: the first agent
pays to place the document in the cache, and the rest read it back at a fraction
of the price.

The `file_id` is recorded in the study's `work/` directory alongside a hash of
the PDF, so re-running a study reuses the upload -- and re-uploads automatically
if the protocol file itself changed.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import anthropic

MANIFEST_NAME = "uploaded_documents.json"


def file_digest(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


@dataclass(frozen=True)
class UploadedDocument:
    file_id: str
    filename: str
    digest: str
    size_bytes: int
    uploaded_at: str

    def as_content_block(self, *, cache: bool = False) -> dict[str, Any]:
        """A `document` content block referring to the uploaded file.

        `cache=True` marks the end of the cacheable prefix, so everything up to
        and including the document is served from Anthropic's prompt cache on
        subsequent agent calls.
        """
        block: dict[str, Any] = {
            "type": "document",
            "source": {"type": "file", "file_id": self.file_id},
            "title": self.filename,
        }
        if cache:
            block["cache_control"] = {"type": "ephemeral", "ttl": "1h"}
        return block


class DocumentStore:
    """Per-study record of what has been uploaded."""

    def __init__(self, work_dir: Path) -> None:
        self.path = work_dir / MANIFEST_NAME
        self._entries: dict[str, dict[str, Any]] = {}
        if self.path.is_file():
            try:
                self._entries = json.loads(self.path.read_text(encoding="utf-8"))
            except (OSError, ValueError):
                self._entries = {}

    def _save(self) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.path.write_text(
            json.dumps(self._entries, indent=2, ensure_ascii=False), encoding="utf-8"
        )

    def lookup(self, path: Path) -> UploadedDocument | None:
        entry = self._entries.get(path.name)
        if not entry:
            return None
        if entry.get("digest") != file_digest(path):
            return None  # the protocol changed; the old upload is not it
        return UploadedDocument(**entry)

    def ensure(
        self, client: anthropic.Anthropic, path: Path, *, force: bool = False
    ) -> UploadedDocument:
        """Return the uploaded document, uploading only if it is not already there."""
        if not force:
            existing = self.lookup(path)
            if existing:
                return existing

        uploaded = client.files.upload(file=path)
        document = UploadedDocument(
            file_id=uploaded.id,
            filename=path.name,
            digest=file_digest(path),
            size_bytes=path.stat().st_size,
            uploaded_at=datetime.now(timezone.utc).isoformat(timespec="seconds"),
        )
        self._entries[path.name] = document.__dict__.copy()
        self._save()
        return document

    def forget(self, filename: str) -> None:
        if self._entries.pop(filename, None) is not None:
            self._save()
