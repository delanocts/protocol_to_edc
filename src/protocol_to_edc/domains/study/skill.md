# Skill: reading a protocol's identity

## Where the truth lives
The title page is authoritative for the official title, protocol number and
version. The synopsis repeats them and is frequently stale after an amendment --
if the two disagree, the title page wins and the disagreement is a gap worth
reporting.

## Protocol numbering conventions
Sponsors encode meaning in their protocol numbers. Lilly's `I8R-JE-IGBJ` is
compound (`I8R`), region (`JE` = Japan; `MC` = multi-country), then a study
code. A number that looks almost right but has the wrong region segment is a
transcription error worth flagging, not a variant to accept.

## Registry identifiers
- `NCT########` -- ClinicalTrials.gov
- `jRCT##########` / `JapicCTI-######` -- Japanese registries
- `20##-######-##` -- EudraCT
- `ISRCTN########` -- ISRCTN

A study may carry several. List all of them; they are how downstream systems
reconcile this study with public records.

## Version identifiers
Amendments are labelled inconsistently: `Amendment (a)`, `Amendment 1`,
`Version 3.0`, `Protocol Amendment a`. Reproduce the protocol's own label rather
than normalising it. The header or footer of every page usually carries it even
when the title page does not.

## Therapeutic area versus indication
The therapeutic area is the clinical domain the study sits in (diabetes,
oncology, respiratory). The indication is the specific condition treated. A
glucagon rescue study in diabetic patients has a diabetes/endocrinology
therapeutic area and severe hypoglycaemia as the indication -- do not put the
acute condition in the therapeutic area.
