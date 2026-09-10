# USDM v4 reference set — downloaded, do not hand-edit

Source: https://github.com/cdisc-org/DDF-RA/tree/main/Deliverables  (branch `main`)
Downloaded: 2026-09-10 — USDM API version **4.0.0** (OpenAPI 3.1.0, 164 schemas)

| File | Purpose |
|---|---|
| `USDM_API.json`        | OpenAPI 3.1 schema. Authoritative for entity shape, required fields, enums. Drives validation and the per-domain schema slices. |
| `USDM_API.yaml`        | Same content, human-readable. |
| `USDM_CT.xlsx`         | USDM controlled terminology — codes for study type, phase, blinding, epoch type, encounter type, etc. |
| `USDM_CORE_Rules.xlsx` | CDISC CORE conformance rules. Second validation layer after JSON-schema validation. |

Refresh with `python -m protocol_to_edc.usdm.refresh --version 4.x`.
