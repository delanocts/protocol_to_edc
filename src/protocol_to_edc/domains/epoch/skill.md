# Skill: identifying study epochs

## Epoch versus visit
An epoch spans time; a visit is a point in it. 'Screening' is an epoch and
'Screening Visit' is a visit. If a candidate has a single day rather than a
span, it belongs to the schedule domain.

## Epoch versus arm
Epochs are *when*, arms are *who*. Every subject passes through every epoch;
subjects differ by arm. If a candidate applies only to some subjects, it is an
arm characteristic, not an epoch.

## Common epochs and their codes
| Protocol wording | Epoch type |
|---|---|
| Screening, Pre-randomisation | Screening Epoch |
| Run-in, Lead-in, Stabilisation | Run-in Epoch |
| Treatment, Double-blind Treatment, Period 1 | Treatment Epoch or Blinded Treatment Epoch |
| Washout | Washout Epoch |
| Follow-up, Post-treatment, Safety Follow-up | Follow-Up Epoch |
| Open-label Extension | Extension Epoch |

## Crossover studies
Each treatment period is its own epoch, usually with a washout epoch between.
A two-period crossover typically gives: Screening, Treatment Period 1, Washout,
Treatment Period 2, Follow-up.

## Ordering
Epochs are returned in chronological order and the pipeline chains them with
`previousId` / `nextId` from that order. A misordered list produces a
misordered study, so use the schematic's left-to-right order rather than the
order sections happen to appear in the document.
