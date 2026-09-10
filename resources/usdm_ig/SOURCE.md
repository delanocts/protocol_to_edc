# USDM Implementation Guide — downloaded, do not hand-edit

Source: https://github.com/cdisc-org/DDF-RA/blob/main/Deliverables/IG/USDM-IG.pdf
Downloaded: 2026-09-10  (5.87 MB)

`USDM-IG.pdf` is the full guide. It is NOT sent to the model in full on every call.
A one-time preprocessing step slices it into per-entity excerpts under `sections/`,
and each domain skill loads only the sections it needs.

Regenerate the slices with:  python -m protocol_to_edc.usdm.slice_ig
