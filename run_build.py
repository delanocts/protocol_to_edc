#!/usr/bin/env python
"""Local entry point.

    python run_build.py I8R-JE-IGBJ
    python run_build.py I8R-JE-IGBJ --domains epoch,study_arm
    python run_build.py --help

Equivalent to `pte build`. Kept as a script so the pipeline runs from a checkout
without installing the package.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "src"))

from protocol_to_edc.cli import main  # noqa: E402

if __name__ == "__main__":
    argv = sys.argv[1:]
    if argv and not argv[0].startswith("-") and argv[0] not in {
        "studies", "domains", "new", "check", "build", "web",
    }:
        argv = ["build", *argv]
    raise SystemExit(main(argv))
