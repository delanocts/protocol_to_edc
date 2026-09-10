# Skill: extracting interventions and dosing

## What counts as an intervention
The investigational product, every active comparator, and placebo. Rescue
medication and background therapy are interventions only if the protocol
administers them as part of the design rather than permitting them as
concomitant medication.

## Compound code versus product name
`LY900018` is a compound code. `Nasal Glucagon` is the product. `Baqsimi` would
be a trade name. The name field takes what the protocol calls the administered
thing; codes go in `product_codes`.

## Dose parsing
Protocols write dose as prose. Split it, but keep the whole sentence too:

> "3 mg of nasal glucagon administered as a single actuation into one nostril"

- `dose_value`: 3
- `dose_unit`: mg
- `route`: nasal
- `frequency`: once
- `dose_text`: the whole sentence, which is the only place 'single actuation
  into one nostril' survives

## When not to give a number
Leave `dose_value` empty and record a gap when dosing is:
- weight-based ('0.5 mg/kg')
- titrated ('escalated in 5 mg increments to effect')
- a range ('10 to 20 mg')
- different per arm or per period -- instead, create one intervention per dose

A single number standing in for a titration schedule is a wrong dose in a
database, which is the most consequential error this domain can make.

## Routes
Match to the codelist by meaning: 'intranasally' is the nasal route,
'IM injection' is intramuscular, 'by mouth' is oral. Do not leave a route empty
because the protocol used an adverb.
