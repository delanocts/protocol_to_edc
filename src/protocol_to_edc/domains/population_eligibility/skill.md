# Skill: population and eligibility criteria

## Completeness matters more than anything else here
A protocol with 28 criteria yields 28 items. A truncated list is worse than an
empty one because it looks complete and nobody re-checks it. If the list is long,
work through it methodically rather than summarising.

## Verbatim, with thresholds
> "Have HbA1c less than or equal to 10% at screening"

is the criterion. 'Adequate glycaemic control' is not. Numeric thresholds, units,
timings and parenthetical qualifications are the operative content of a
criterion -- an eligibility criterion without its threshold cannot be programmed.

## Numbering
Keep the protocol's numbering. Inclusion and exclusion lists that each start at 1
are normal; the category tells them apart. Some protocols use `I1`/`E1` prefixes;
reproduce whatever is printed.

## includesHealthySubjects
USDM requires this and offers no 'unknown':
- healthy volunteer studies -- true
- patients with a diagnosed condition -- false
- studies enrolling both -- true, with the detail in the description

## Age
Give the value with the protocol's unit: '20 years', '6 months'. Do not convert
to a single unit and do not invent an upper bound where the protocol sets only a
minimum.

## Enrolment numbers
'Approximately 60 subjects, up to a maximum of 72' -- put 60 in
`planned_enrolment` and the full phrasing in the description. Planned completion
is a separate number and only exists when the protocol states it.
