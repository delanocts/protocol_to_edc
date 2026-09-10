"""On-disk cache of agent responses.

Two different things both get called caching here, and they solve different
problems:

* **Prompt caching** (`cache_control` on a request) is Anthropic's -- it keeps
  the protocol resident server-side so the second agent to read it pays a
  fraction of the input cost. It saves money within a run.
* **This module** stores the finished result of a call on disk, keyed by
  everything that went into it. It saves the entire call on a *re-run*.

The second matters because of how this pipeline is used: a run is repeated after
changing one domain's prompt, or after a reviewer corrects one fragment. Without
a result cache, re-running to fix the epoch agent also re-pays for the seven
agents that were already right.

The key covers the model, the effort, the prompt, the schema and the document, so
changing any of them is a miss rather than a stale hit.
"""

from __future__ import annotations

import hashlib
import json
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from ..core import paths

CACHE_VERSION = "1"


def fingerprint(*parts: Any) -> str:
    """A stable hash over everything that determines a response."""
    digest = hashlib.sha256()
    digest.update(CACHE_VERSION.encode())
    for part in parts:
        if isinstance(part, (dict, list)):
            part = json.dumps(part, sort_keys=True, ensure_ascii=False)
        digest.update(str(part).encode("utf-8"))
        digest.update(b"\x00")
    return digest.hexdigest()[:32]


@dataclass
class CacheEntry:
    key: str
    payload: dict[str, Any]
    stored_at: float
    domain: str

    @property
    def age_seconds(self) -> float:
        return time.time() - self.stored_at


class ResponseCache:
    """A directory of JSON responses, one file per key."""

    def __init__(self, root: Path | None = None, *, enabled: bool = True) -> None:
        self.root = root or (paths.CACHE_DIR / "responses")
        self.enabled = enabled
        self.hits = 0
        self.misses = 0

    def _path(self, key: str) -> Path:
        return self.root / f"{key}.json"

    def get(self, key: str) -> CacheEntry | None:
        if not self.enabled:
            return None
        path = self._path(key)
        if not path.is_file():
            self.misses += 1
            return None
        try:
            raw = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            self.misses += 1
            return None
        self.hits += 1
        return CacheEntry(
            key=key,
            payload=raw["payload"],
            stored_at=raw.get("storedAt", 0.0),
            domain=raw.get("domain", ""),
        )

    def put(self, key: str, payload: dict[str, Any], *, domain: str = "") -> None:
        if not self.enabled:
            return
        self.root.mkdir(parents=True, exist_ok=True)
        self._path(key).write_text(
            json.dumps(
                {
                    "storedAt": time.time(),
                    "domain": domain,
                    "payload": payload,
                },
                indent=2,
                ensure_ascii=False,
            ),
            encoding="utf-8",
        )

    def clear(self, domain: str | None = None) -> int:
        """Drop cached responses, optionally only one domain's. Returns the count."""
        if not self.root.is_dir():
            return 0
        removed = 0
        for path in self.root.glob("*.json"):
            if domain:
                try:
                    stored = json.loads(path.read_text(encoding="utf-8")).get("domain")
                except (OSError, ValueError):
                    stored = None
                if stored != domain:
                    continue
            path.unlink()
            removed += 1
        return removed
