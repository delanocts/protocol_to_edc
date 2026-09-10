# Protocol to USDM

Turns an approved clinical protocol PDF into a CDISC **USDM v4** study
definition, using a pipeline of domain agents backed by the Claude API.

Eight agents each read the protocol for one part of the study design. Their
output is validated against the published USDM schema, assembled into one
document, and accompanied by a gap report listing everything a human needs to
decide. It is an accelerator with a reviewer, not an autopilot.

---

## What it produces

```
studies/<STUDY_ID>/output/
  usdm/<STUDY_ID>_usdm.json      the assembled USDM v4 document
  usdm/fragments/<domain>.json   each agent's contribution, kept separately
  reports/gap_report.md          the reviewer's worklist, ordered by severity
  reports/provenance.csv         every extracted value -> the protocol text it came from
  reports/validation_report.json schema and referential-integrity findings
  reports/run_summary.json       per-domain tokens, cache hits, timings
```

## Quick start

```bash
python -m venv .venv
.venv/Scripts/python -m pip install -e ".[dev]"     # Windows
# .venv/bin/python -m pip install -e ".[dev]"       # macOS / Linux

cp .env.example .env          # then put your ANTHROPIC_API_KEY in it

pte new MY-STUDY-01           # scaffold a study folder
# put the protocol PDF in studies/MY-STUDY-01/input/protocol/
# point input.protocol_pdf at it in studies/MY-STUDY-01/study.yaml

pte check MY-STUDY-01         # verifies everything without calling the API
pte build MY-STUDY-01         # runs the pipeline
```

Or through the browser:

```bash
python run_web.py             # http://127.0.0.1:8000
```

The web UI and the CLI call the same `orchestrator.execute`; neither is a
reimplementation of the other.

## The eight domains

| # | Domain | USDM v4 entities |
|---|---|---|
| 1 | Study | `Study`, `StudyVersion`, `StudyTitle`, `StudyIdentifier`, `Organization` |
| 2 | Study Design | `InterventionalStudyDesign` (type, model, phase, blinding) |
| 3 | Study Arm | `StudyArm` |
| 4 | Epoch | `StudyEpoch` |
| 5 | Study Intervention | `StudyIntervention`, `Administration`, `Quantity` |
| 6 | Study Objective | `Objective`, `Endpoint` |
| 7 | Population & Eligibility | `StudyDesignPopulation`, `EligibilityCriterion`, `EligibilityCriterionItem` |
| 8 | Activity & Schedule | `Activity`, `Encounter`, `ScheduleTimeline`, `ScheduledActivityInstance`, `Timing` |

Domains 1-7 run concurrently; domain 8 runs after, because it needs the epochs
and arms to attach visits to.

Two entities are produced by **code, not a model**: `StudyCell` (the arm x epoch
grid) and `StudyElement`. They are joins over other domains' output, so they are
derived deterministically in `usdm/joins.py`.

### Turning domains off

Set `enabled: false` in `config/default.yaml`, or per study in `study.yaml`, or
untick it in the UI, or `pte build <STUDY> --domains epoch,study_arm`. A disabled
agent makes no API call and costs nothing.

USDM marks several of these properties required, so disabling a domain makes the
document incomplete by design. `usdm.output_mode` decides what happens:

| Mode | Behaviour |
|---|---|
| `partial` | emit what exists, report what is missing (default) |
| `strict` | refuse to assemble an incomplete document |
| `stub` | insert minimal placeholders so it validates, and list every one |

### Adding a ninth domain

1. `config/domains/09_your_domain.yaml` — a manifest
2. `src/protocol_to_edc/domains/your_domain/` — `domain.py` with `PAYLOAD_MODEL`,
   `build_prompt`, `to_usdm`, plus `skill.md`

Nothing else changes. The orchestrator, the assembler, the CLI and the web UI all
read the registry; none of them names a domain.

## How it works

```
protocol.pdf ──> Files API (uploaded once, prompt-cached for every agent)
                      │
     ┌────────────────┴────────────────┐
     │  8 domain agents, by dependency │   each returns a validated pydantic
     │  level, concurrently            │   object with confidence + quotes
     └────────────────┬────────────────┘
                      │
   fragments ──> assembler ──> id resolution ──> validator ──> reports
                      │
              StudyCell / StudyElement joins (deterministic)
```

**The model judges, code builds.** Agents decide what an epoch *is*; Python
writes the JSON, mints the ids, derives the grid and resolves the terminology.

**No invented codes.** An agent picks a term by its wording from the codelists it
is shown; `usdm/ct.py` turns that choice into a `Code` object. A term that
matches nothing becomes a sponsor-defined value and appears in the gap report,
rather than a plausible-looking C-code.

**Every value is quoted and the quote is checked.** Agents return the protocol
text they read a value from; `qc/provenance.py` verifies each quote against the
PDF text layer. A quote that is not in the document is the clearest available
signal that a value was inferred rather than read.

**Ids are placeholders until assembly.** Agents emit `@StudyEpoch:screening`;
the assembler mints `StudyEpoch_1` and rewrites every reference. A reference to
something no enabled domain produced cannot be silently written as a valid id --
it is reported as dangling.

## Reference data

Downloaded into `resources/`, none of it hand-edited:

| What | Source |
|---|---|
| `usdm/v4/USDM_API.json` | [DDF-RA](https://github.com/cdisc-org/DDF-RA) — the schema, authoritative for entity shape |
| `usdm/v4/USDM_CT.xlsx` | DDF-RA — 25 codelists, plus a prose definition for every attribute |
| `usdm/v4/ct_supplement.json` | derived: NCI EVS codelists for the attributes the workbook omits |
| `usdm/v4/USDM_CORE_Rules.xlsx` | DDF-RA — CORE conformance rules |
| `usdm_ig/USDM-IG.pdf` | DDF-RA — the Implementation Guide |
| `usdm_ig/sections/*.md` | derived: per-entity excerpts, loaded into the prompts on demand |

Regenerate the derived files:

```bash
python -m protocol_to_edc.usdm.build_ct     # terminology (downloads ~14 MB from NCI)
python -m protocol_to_edc.usdm.slice_ig     # IG excerpts
```

## Cost control

- The protocol is uploaded once and prompt-cached with a 1-hour TTL, so agents
  after the first read it at a fraction of the input price.
- Responses are cached on disk keyed by model, effort, prompt, schema and
  document digest. Re-running after changing one domain does not re-pay for the
  other seven. `--refresh <domain>` drops one domain's cache; `--no-cache` drops
  all of them.
- `run_summary.json` records tokens and cache-hit ratio per domain.

## Testing

```bash
.venv/Scripts/python -m pytest -q
```

Tests run without an API key. Two groups matter most:

- **Regression against the CDISC pilot study.** A known-good USDM v4 document
  must produce zero validation errors. Any rule that flags it is wrong about
  USDM, not about us.
- **Schema guards.** The structured-outputs API rejects certain JSON-schema
  keywords, at request time, after the run has started. These tests catch them
  for all eight domains at development time instead.

## Scope

In: the eight domains above, USDM v4, single study design, text-layer English
PDFs.

Out, for now: the Architect Loader Specification and the Rave load, edit checks,
derivations, dynamics, and OCR. The structure anticipates the ALS phase — it is
a consumer of the USDM document, not a change to it.
