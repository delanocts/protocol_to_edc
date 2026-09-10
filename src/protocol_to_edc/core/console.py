"""UTF-8 console setup.

Windows consoles default to cp1252 here, so printing a protocol title with a
non-breaking hyphen or an en dash raises UnicodeEncodeError and kills the run.
Import `setup_console()` before any output. Idempotent.
"""

from __future__ import annotations

import io
import sys

_DONE = False


def setup_console() -> None:
    global _DONE
    if _DONE:
        return
    for name in ("stdout", "stderr"):
        stream = getattr(sys, name, None)
        buffer = getattr(stream, "buffer", None)
        if buffer is None:  # already wrapped, or redirected to something exotic
            continue
        if (getattr(stream, "encoding", "") or "").lower().replace("-", "") == "utf8":
            continue
        setattr(
            sys,
            name,
            io.TextIOWrapper(buffer, encoding="utf-8", errors="replace", line_buffering=True),
        )
    _DONE = True
