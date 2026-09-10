#!/usr/bin/env python
"""Start the web UI.

    python run_web.py            -> http://127.0.0.1:8000
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "src"))

from protocol_to_edc.cli import main  # noqa: E402

if __name__ == "__main__":
    raise SystemExit(main(["web", *sys.argv[1:]]))
