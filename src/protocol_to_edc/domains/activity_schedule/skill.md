# Skill: reading a Schedule of Activities

## The structure
An SoA is a matrix. Rows are activities, columns are visits, and a mark in a cell
means that activity happens at that visit. Everything in this domain follows from
reading that matrix accurately.

## Marks
A performed activity may be marked with X, x, a bullet, a filled cell, a
superscript footnote reference, or a number. Any mark means performed. An empty
cell means not performed. A cell containing only a footnote marker still means
performed, conditionally.

## Footnotes carry what the grid cannot
Read every footnote. They typically encode:
- conditions ('only for subjects who...')
- timing detail ('within 30 minutes prior to dosing')
- window variations ('+/- 3 days for this visit only')
- repeated assessments ('at 15, 30, 45 and 60 minutes post-dose')
- early-termination behaviour

Quote them verbatim. A schedule extracted without its footnotes is a schedule
that will be wrong in exactly the places clinical operations cares about.

## Timings are relative, in ISO 8601
| Protocol | value | window_lower | window_upper |
|---|---|---|---|
| Day 1 (anchor) | `P0D` | | |
| Day 8, +/- 2 days | `P7D` | `-P2D` | `P2D` |
| Week 4, +/- 3 days | `P28D` | `-P3D` | `P3D` |
| 30 minutes post-dose | `PT30M` | | |

Offsets are from the previous visit. Day 8 is `P7D` after Day 1, not `P8D`,
because study days are 1-indexed and there is no Day 0.

Where the protocol gives no basis for computing an offset, leave the ISO fields
empty and keep the printed day. A fabricated duration is worse than a recorded
gap.

## Cycle-based schedules
'Day 1 of each 21-day cycle for up to 6 cycles' cannot be expanded without a
decision about how many cycles to materialise. Describe the cycle and record a
gap rather than expanding it silently.

## Multiple tables
Protocols often have a main SoA plus a separate follow-up, early-termination or
sub-study table. Extract the main one, and record the others as gaps naming their
page. Merging them produces a schedule that matches no table in the document.
