# USDM v4 reference set — downloaded, do not hand-edit

Source: https://github.com/cdisc-org/DDF-RA/tree/main/Deliverables  (branch `main`)
Downloaded: 2026-09-10 — USDM API version **4.0.0** (OpenAPI 3.1.0, 164 schemas)

| File | Purpose |
|---|---|
| `USDM_API.json`        | OpenAPI 3.1 schema. Authoritative for entity shape, required fields, enums. Drives validation and the per-domain schema slices. |
| `USDM_CT.xlsx`         | USDM controlled terminology — codes for study type, phase, blinding, epoch type, encounter type, etc. |

Refresh with `python -m protocol_to_edc.usdm.refresh --version 4.x`.

Not kept: `USDM_API.yaml` (same content as the JSON, which is what loads) and
`USDM_CORE_Rules.xlsx` (CORE conformance checking is not implemented). Both are
one `curl` away from the DDF-RA repository if they are ever needed.
