"""Single source of truth for every path in the project.

Nothing else builds paths by string concatenation. Study isolation is enforced
here: `StudyPaths` refuses to resolve outside its own study directory.
"""

from __future__ import annotations

import os
import re
from dataclasses import dataclass
from functools import cache
from pathlib import Path

# src/protocol_to_edc/core/paths.py -> project root is four levels up
PROJECT_ROOT = Path(__file__).resolve().parents[3]

CONFIG_DIR = PROJECT_ROOT / "config"
DOMAIN_MANIFEST_DIR = CONFIG_DIR / "domains"
DEFAULT_CONFIG = CONFIG_DIR / "default.yaml"

RESOURCES = PROJECT_ROOT / "resources"
USDM_RESOURCES = RESOURCES / "usdm"
USDM_IG_DIR = RESOURCES / "usdm_ig"
USDM_IG_PDF = USDM_IG_DIR / "USDM-IG.pdf"
USDM_IG_SECTIONS = USDM_IG_DIR / "sections"
REFERENCE_STUDIES = RESOURCES / "reference_studies"

STUDIES = PROJECT_ROOT / "studies"
STUDY_TEMPLATE = STUDIES / "_template"

CACHE_DIR = PROJECT_ROOT / ".cache"
DOMAINS_PACKAGE_DIR = Path(__file__).resolve().parents[1] / "domains"

# ASCII only. A U+2011 non-breaking hyphen in a study id is invisible on screen
# and breaks path handling on Windows, so ids are validated rather than trusted.
STUDY_ID_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]{0,63}$")


class StudyIdError(ValueError):
    """A study id that cannot be safely used as a directory name."""


def validate_study_id(study_id: str) -> str:
    """Return `study_id` unchanged, or explain precisely why it is unusable."""
    if not STUDY_ID_RE.match(study_id):
        bad = [(i, c, f"U+{ord(c):04X}") for i, c in enumerate(study_id) if ord(c) > 127]
        if bad:
            detail = ", ".join(f"position {i} {c!r} ({u})" for i, c, u in bad)
            raise StudyIdError(
                f"Study id {study_id!r} contains non-ASCII characters: {detail}. "
                "Use plain ASCII hyphens (U+002D), e.g. 'I8R-JE-IGBJ'."
            )
        raise StudyIdError(
            f"Study id {study_id!r} is not usable as a folder name. Allowed: "
            "letters, digits, dot, underscore, hyphen; 1-64 chars; must start alphanumeric."
        )
    return study_id


def usdm_resource_dir(version: str) -> Path:
    """Reference set for a USDM version. '4.0.0' and '4.x' both map to `usdm/v4`."""
    major = version.split(".", 1)[0].lstrip("vV")
    if not major.isdigit():
        raise ValueError(f"Cannot derive a major version from USDM version {version!r}")
    return USDM_RESOURCES / f"v{major}"


@dataclass(frozen=True)
class StudyPaths:
    """Every path belonging to one study. Constructed via `for_study`."""

    study_id: str
    root: Path

    @property
    def config_file(self) -> Path:
        return self.root / "study.yaml"

    @property
    def input_dir(self) -> Path:
        return self.root / "input"

    @property
    def protocol_dir(self) -> Path:
        return self.input_dir / "protocol"

    @property
    def reference_dir(self) -> Path:
        return self.input_dir / "reference"

    @property
    def work_dir(self) -> Path:
        return self.root / "work"

    @property
    def output_dir(self) -> Path:
        return self.root / "output"

    @property
    def usdm_dir(self) -> Path:
        return self.output_dir / "usdm"

    @property
    def fragments_dir(self) -> Path:
        return self.usdm_dir / "fragments"

    @property
    def reports_dir(self) -> Path:
        return self.output_dir / "reports"

    @property
    def logs_dir(self) -> Path:
        return self.root / "logs"

    @property
    def usdm_document(self) -> Path:
        return self.usdm_dir / f"{self.study_id}_usdm.json"

    def fragment(self, domain_id: str) -> Path:
        return self.fragments_dir / f"{domain_id}.json"

    def report(self, name: str) -> Path:
        return self.reports_dir / name

    def resolve_input(self, relative: str | os.PathLike[str]) -> Path:
        """Resolve a study-relative path, refusing to escape the study directory."""
        candidate = (self.root / Path(relative)).resolve()
        root = self.root.resolve()
        if not candidate.is_relative_to(root):
            raise ValueError(
                f"Path {relative!r} resolves outside study {self.study_id} ({candidate})"
            )
        return candidate

    def ensure_dirs(self) -> None:
        for path in (
            self.protocol_dir,
            self.reference_dir,
            self.work_dir,
            self.fragments_dir,
            self.reports_dir,
            self.logs_dir,
        ):
            path.mkdir(parents=True, exist_ok=True)


def for_study(study_id: str) -> StudyPaths:
    """Paths for `study_id`. Does not require the directory to exist yet."""
    validate_study_id(study_id)
    return StudyPaths(study_id=study_id, root=STUDIES / study_id)


@cache
def list_studies() -> tuple[str, ...]:
    """Study ids present on disk, excluding the template."""
    if not STUDIES.is_dir():
        return ()
    return tuple(
        sorted(
            p.name
            for p in STUDIES.iterdir()
            if p.is_dir() and not p.name.startswith("_") and STUDY_ID_RE.match(p.name)
        )
    )


def available_usdm_versions() -> tuple[str, ...]:
    """Full USDM versions with a downloaded reference set, newest first.

    The precise version is read from the schema's `info.version` (e.g. "4.0.0"),
    not inferred from the directory name, so the UI never offers a version that
    disagrees with the file that would actually be used to validate.
    """
    import json

    if not USDM_RESOURCES.is_dir():
        return ()
    found: list[tuple[int, str]] = []
    for d in sorted(USDM_RESOURCES.iterdir()):
        schema = d / "USDM_API.json"
        if not (d.is_dir() and schema.is_file()):
            continue
        try:
            version = json.loads(schema.read_text(encoding="utf-8"))["info"]["version"]
        except (OSError, ValueError, KeyError):
            continue
        found.append((int(d.name.lstrip("v") or 0), str(version)))
    return tuple(v for _, v in sorted(found, reverse=True))
