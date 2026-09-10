# Skill: identifying study arms

## The test
An arm is a property of a subject that holds for the whole study. Ask: "if I
picked one subject, would they be in this group for the entire study?" If the
answer is no because they cross over into another treatment, the groups are not
arms -- the *sequences* are.

## Crossover naming
A two-treatment, two-period crossover has two arms. Protocols name them
inconsistently:
- 'Sequence AB' / 'Sequence BA'
- 'Group 1' / 'Group 2'
- 'Treatment order A-B' / 'B-A'

Use the protocol's names. Put the composition ('nasal glucagon in Period 1 then
intramuscular glucagon in Period 2') in the description, where it is preserved
without polluting the name.

## Arm types
| Arm receives | Type |
|---|---|
| the investigational product | Investigational Arm |
| an approved active drug, for comparison | Active Comparator Arm |
| placebo | Placebo Control Arm |
| nothing / standard care only | No Intervention Arm |
| a sham procedure | Sham Comparator Arm |

In a crossover, a sequence arm contains more than one of these. Classify by the
protocol's own framing; where it does not frame it, say so in a gap rather than
picking arbitrarily.

## Allocation ratio
'randomised 1:1' with two arms means equal allocation. Do not compute per-arm
numbers from a total and a ratio -- state the total in the population domain and
leave `planned_subjects` empty unless the protocol gives it per arm.
