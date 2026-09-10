"""Build the supplementary terminology layer.

`USDM_CT.xlsx` defines only 25 codelists. The eight domains need more than that:
`StudyEpoch.type`, `StudyArm.type`, `InterventionalStudyDesign.model`, study
phase, blinding schema, planned sex and others live in the wider NCI/CDISC
terminology rather than in the DDF workbook.

Rather than hand-maintain a mapping from USDM attribute to NCI codelist, this
tool derives it:

1. Walk a known-good USDM document and record which `Code` values are used for
   each `entity.attribute`. (`AliasCode`-typed attributes such as `studyPhase`
   and `blindingSchema` are unwrapped to their `standardCode`.)
2. Look each of those C-codes up in the published NCI terminology to find which
   codelist it belongs to.
3. Emit the **entire** codelist, not just the terms the reference document
   happened to use -- so an agent reading a different protocol still sees every
   permitted value.

Step 3 is what makes this worth doing: the reference document uses 3 epoch types,
while the published `Epoch` codelist has many more.

Sources (downloaded, then cached under `resources/usdm/<vN>/_ct_cache/`):

* DDF terminology  -- evs.nci.nih.gov/ftp1/CDISC/DDF/DDF Terminology.txt
* SDTM terminology -- evs.nci.nih.gov/ftp1/CDISC/SDTM/SDTM Terminology.txt

USDM writes the NCI **preferred term** into `Code.decode`, not the CDISC
submission value, so preferred terms are what this emits.

    python -m protocol_to_edc.usdm.build_ct
    python -m protocol_to_edc.usdm.build_ct --offline   # reuse the cache
"""

from __future__ import annotations

import argparse
import csv
import json
import urllib.error
import urllib.request
from dataclasses import dataclass, field
from datetime import date
from pathlib import Path
from typing import Any, Iterator

from ..core import paths
from . import ct

SOURCES = {
    "DDF": "https://evs.nci.nih.gov/ftp1/CDISC/DDF/DDF%20Terminology.txt",
    "SDTM": "https://evs.nci.nih.gov/ftp1/CDISC/SDTM/SDTM%20Terminology.txt",
}

# Attributes that are study-specific data rather than terminology: the reference
# document's values say nothing about what another protocol may legitimately use.
SKIP_ATTRIBUTES = frozenset(
    {
        "Address.country",
        "StudySite.country",
        "StudyIntervention.codes",
        "StudyVersion.businessTherapeuticAreas",
        "InterventionalStudyDesign.therapeuticAreas",
        "Indication.codes",
        "Procedure.code",
        "ResponseCode.code",
        "StudyDefinitionDocument.language",
        # Biomedical concepts map onto the full LOINC-style lab test codelist:
        # thousands of terms, and outside the scope of the eight domains.
        "BiomedicalConcept.code",
        "BiomedicalConceptProperty.code",
        "BiomedicalConceptSurrogate.code",
    }
)

# The NCI files are large and mostly irrelevant; a codelist is only kept if some
# attribute maps onto it.
_MIN_ROWS = 100


@dataclass
class NciTerm:
    code: str
    codelist_code: str
    codelist_name: str
    submission_value: str
    preferred_term: str
    definition: str
    extensible: bool = False


@dataclass
class NciTerminology:
    """Terms and codelists parsed from the NCI tab-delimited distributions."""

    by_code: dict[str, list[NciTerm]] = field(default_factory=dict)
    by_codelist: dict[str, list[NciTerm]] = field(default_factory=dict)
    codelist_names: dict[str, str] = field(default_factory=dict)
    extensible: dict[str, bool] = field(default_factory=dict)

    def add(self, term: NciTerm) -> None:
        if not term.codelist_code:
            # A header row: it defines the codelist itself rather than a value.
            self.codelist_names[term.code] = term.codelist_name
            self.extensible[term.code] = term.extensible
            return
        self.by_code.setdefault(term.code, []).append(term)
        self.by_codelist.setdefault(term.codelist_code, []).append(term)

    def codelists_for(self, codes: list[str]) -> list[str]:
        """Codelist codes covering the given term codes, most frequent first."""
        tally: dict[str, int] = {}
        for code in codes:
            for term in self.by_code.get(code, []):
                tally[term.codelist_code] = tally.get(term.codelist_code, 0) + 1
        return sorted(tally, key=lambda c: (-tally[c], c))


def _parse_nci(text: str) -> Iterator[NciTerm]:
    reader = csv.DictReader(text.splitlines(), delimiter="\t")
    for row in reader:
        code = (row.get("Code") or "").strip()
        if not code:
            continue
        yield NciTerm(
            code=code,
            codelist_code=(row.get("Codelist Code") or "").strip(),
            codelist_name=(row.get("Codelist Name") or "").strip(),
            submission_value=(row.get("CDISC Submission Value") or "").strip(),
            preferred_term=(row.get("NCI Preferred Term") or "").strip(),
            definition=(row.get("CDISC Definition") or "").strip(),
            extensible=(row.get("Codelist Extensible (Yes/No)") or "").strip().lower()
            == "yes",
        )


def _fetch(name: str, url: str, cache_dir: Path, offline: bool) -> str:
    cache_dir.mkdir(parents=True, exist_ok=True)
    cached = cache_dir / f"{name}_Terminology.txt"

    if offline:
        if not cached.is_file():
            raise FileNotFoundError(f"--offline given but no cached {name} file at {cached}")
        return cached.read_text(encoding="utf-8", errors="replace")

    try:
        with urllib.request.urlopen(url, timeout=180) as response:
            raw = response.read().decode("utf-8", errors="replace")
    except (urllib.error.URLError, TimeoutError) as exc:
        if cached.is_file():
            print(f"  {name}: download failed ({exc}); using cache")
            return cached.read_text(encoding="utf-8", errors="replace")
        raise

    # The EVS site answers unknown paths with its single-page app, not a 404.
    if raw.lstrip().lower().startswith("<!doctype html") or len(raw.splitlines()) < _MIN_ROWS:
        if cached.is_file():
            print(f"  {name}: server returned a web page, not data; using cache")
            return cached.read_text(encoding="utf-8", errors="replace")
        raise ValueError(f"{url} did not return terminology data")

    cached.write_text(raw, encoding="utf-8")
    return raw


def collect_usage(document: Any) -> dict[str, dict[str, str]]:
    """Map `entity.attribute` -> {code: decode} as used in a reference document."""
    usage: dict[str, dict[str, str]] = {}

    def record(slot: str, code: dict[str, Any]) -> None:
        if code.get("codeSystem") != ct.CODE_SYSTEM:
            return  # sponsor / ISO / SNOMED values are not CDISC terminology
        if code.get("code") and code.get("decode"):
            usage.setdefault(slot, {})[code["code"]] = code["decode"]

    def walk(node: Any, owner: str | None) -> None:
        if isinstance(node, dict):
            owner_type = node.get("instanceType", owner)
            for key, value in node.items():
                if key == "instanceType":
                    continue
                for item in value if isinstance(value, list) else [value]:
                    if not isinstance(item, dict):
                        continue
                    slot = f"{owner_type}.{key}"
                    kind = item.get("instanceType")
                    if kind == "Code":
                        record(slot, item)
                    elif kind == "AliasCode":
                        # studyPhase / blindingSchema wrap their real code here.
                        standard = item.get("standardCode")
                        if isinstance(standard, dict):
                            record(slot, standard)
                    else:
                        walk(item, owner_type)
        elif isinstance(node, list):
            for item in node:
                walk(item, owner)

    walk(document, None)
    return usage


def build(source: Path, version: str, offline: bool) -> dict[str, Any]:
    document = json.loads(source.read_text(encoding="utf-8"))
    usage = collect_usage(document)

    cache_dir = paths.usdm_resource_dir(version) / "_ct_cache"
    nci = NciTerminology()
    fetched: list[str] = []
    for name, url in SOURCES.items():
        print(f"  fetching {name} terminology ...")
        for term in _parse_nci(_fetch(name, url, cache_dir, offline)):
            nci.add(term)
        fetched.append(name)

    # Only the published workbook counts as "already covered" here. Consulting
    # ct.load() instead would read this tool's own previous output and skip
    # every codelist it had added on the last run.
    workbook_codelists, _ = ct._load_workbook_layer(
        paths.usdm_resource_dir(version) / "USDM_CT.xlsx"
    )
    codelists: dict[str, Any] = {}
    unresolved: dict[str, list[str]] = {}

    for slot in sorted(usage):
        entity, _, attribute = slot.partition(".")
        if slot in SKIP_ATTRIBUTES or entity == "None":
            continue
        if slot in workbook_codelists:
            continue  # the DDF workbook is authoritative where it has an answer

        candidates = nci.codelists_for(list(usage[slot]))
        if not candidates:
            unresolved[slot] = sorted(usage[slot].values())
            continue

        codelist_code = candidates[0]
        terms = nci.by_codelist[codelist_code]
        codelists[slot] = {
            "codelistCode": codelist_code,
            "codelistName": nci.codelist_names.get(codelist_code, ""),
            "extensible": nci.extensible.get(codelist_code, True),
            "source": f"NCI EVS codelist {codelist_code}",
            "derivedFrom": source.name,
            "terms": [
                {
                    "code": t.code,
                    "decode": t.preferred_term or t.submission_value,
                    "submissionValue": t.submission_value,
                    "definition": t.definition,
                }
                for t in sorted(terms, key=lambda t: t.preferred_term or t.submission_value)
            ],
        }

    # Anything the published terminology could not explain still gets recorded,
    # so an agent has the reference document's own values to fall back on.
    for slot, decodes in unresolved.items():
        entity, _, attribute = slot.partition(".")
        codelists[slot] = {
            "codelistCode": "",
            "codelistName": "",
            "extensible": True,
            "source": f"observed in {source.name} only (no NCI codelist matched)",
            "derivedFrom": source.name,
            "terms": [
                {"code": code, "decode": decode, "submissionValue": "", "definition": ""}
                for code, decode in sorted(usage[slot].items(), key=lambda kv: kv[1])
            ],
        }

    return {
        "generatedOn": date.today().isoformat(),
        "usdmVersion": version,
        "codeSystem": ct.CODE_SYSTEM,
        "codeSystemVersion": _code_system_version(document),
        "sources": fetched,
        "referenceDocument": source.name,
        "note": (
            "Second-layer terminology for USDM attributes with no codelist in "
            "USDM_CT.xlsx. Attribute-to-codelist mapping is derived from a "
            "known-good USDM document; the terms are the complete published NCI "
            "codelist. Decodes are NCI preferred terms, matching USDM convention. "
            "Regenerate with `python -m protocol_to_edc.usdm.build_ct`."
        ),
        "unresolved": sorted(unresolved),
        "codelists": codelists,
    }


def _code_system_version(document: Any) -> str:
    tally: dict[str, int] = {}

    def scan(node: Any) -> None:
        if isinstance(node, dict):
            if node.get("instanceType") == "Code" and node.get("codeSystem") == ct.CODE_SYSTEM:
                version = str(node.get("codeSystemVersion", ""))
                if version:
                    tally[version] = tally.get(version, 0) + 1
            for value in node.values():
                scan(value)
        elif isinstance(node, list):
            for value in node:
                scan(value)

    scan(document)
    return max(tally, key=tally.get) if tally else "2024-09-27"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Build supplementary USDM terminology")
    parser.add_argument(
        "--source",
        type=Path,
        default=paths.REFERENCE_STUDIES / "lzzt" / "CDISC_Pilot_Study.json",
        help="known-good USDM document used to map attributes onto codelists",
    )
    parser.add_argument("--usdm-version", default="4.0.0")
    parser.add_argument(
        "--offline", action="store_true", help="reuse cached NCI files, do not download"
    )
    args = parser.parse_args(argv)

    if not args.source.is_file():
        parser.error(f"reference document not found: {args.source}")

    payload = build(args.source, args.usdm_version, args.offline)
    target = paths.usdm_resource_dir(args.usdm_version) / "ct_supplement.json"
    target.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")

    total = sum(len(c["terms"]) for c in payload["codelists"].values())
    print(f"\nwrote {target.relative_to(paths.PROJECT_ROOT)}")
    print(f"  {len(payload['codelists'])} codelists, {total} terms")
    for slot, entry in sorted(payload["codelists"].items()):
        label = entry["codelistName"] or entry["source"]
        print(f"    {slot:46} {len(entry['terms']):4}  {label[:44]}")
    if payload["unresolved"]:
        print(f"  no NCI codelist matched: {', '.join(payload['unresolved'])}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
