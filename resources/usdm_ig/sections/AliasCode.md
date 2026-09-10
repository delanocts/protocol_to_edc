# AliasCode -- from the USDM Implementation Guide v4.0

_(IG page 64)_
Class Name Attribute Name Data Type
NCI C-
Code Cardinality Preferred Term Definition Codelist Ref Inherited From
description string C207463 Administration
Description
A narrative representation for the
administration of a product, agent, or
therapy.
label string C207464 Administration
Label
The short descriptive designation for the
administration of a product, agent, or
therapy.
dose Quantity C167190 Administration
Dose
The value representing the amount of an
agent given to an individual at one time.
frequency AliasCode C89081 Dosing
Frequency
The number of doses administered per a
specific interval.
SDTM
Terminology
Codelist
C71113
route AliasCode C38114 Route of
Administration
The pathway by which a substance is
administered in order to reach the site of
action in the body.
SDTM
Terminology
Codelist
C66729
notes CommentAnnotation CNEW Administration
Notes
A brief written record relevant to the
administration of the product, agent, or
therapy.
administrableProduct AdministrableProduct 0..1 A USDM relationship between the
Administration and
AdministrableProductDefinition classes
which identifies the administrable product
associated with the administration of the
product, agent, or therapy.
duration AdministrationDuration 1 A USDM relationship between the
Administration and AdministrationDuration
classes which provides the duration of an
instance of product, agent, or therapy
administration.
medicalDevice MedicalDevice 0..1 A USDM relationship between the
Administration and MedicalDevice classes
which identifies the medical device
associated with an instance of product,
agent, or therapy administration.
AdministrationDuration C69282 Administration
Duration
The amount of time elapsed during the
administration of an agent.
id string
description string C207459 Administration
Duration
Description
A narrative representation of the agent
administration duration.
quantity Quantity C207460 Administration
Duration
Quantity Value
The value representing the amount of time
over which the administration of an agent
occurs.
durationWillVary Boolean C207461 Administration
Duration Will
Vary Indicator
An indication as to whether the agent
administration duration is planned to vary
within and/or across subjects.
reasonDurationWillVary string C207462 Administration
Duration
Reason
Duration Will
Vary
The explanation for why the agent
administration duration will vary within
and/or across subjects.
AliasCode C201344 Alias Code An alternative symbol or combination of
symbols which is assigned to the members
of a collection.
id string
standardCode Code CNEW Standard Code A combination of symbols that is used to
represent the standard code.
standardCodeAliases Code CNEW Standard Code
Aliases
Alternative combinations of symbols used
to represent aliases or alternatives to the
standard code.
AnalysisPopulation C188814 Analysis
Population
A target study population on which an
analysis is performed. These may be
represented by the entire study population,

_(IG page 72)_
Class Name Attribute Name Data Type
NCI C-
Code Cardinality Preferred Term Definition Codelist Ref Inherited From
variableOfInterest Endpoint 1 A USDM relationship between the
Estimand and Endpoint classes which
provides the details associated with an
instance of the variable of interest within a
study endpoint used to partially define a
study estimand.
intercurrentEvents IntercurrentEvent 1..* A USDM relationship between the
Estimand and IntercurrentEvent classes
which identifies the set of intercurrent
events associated with a study estimand.
interventions StudyIntervention 1..* A USDM relationship between the
Estimand and StudyIntervention classes
which identifies the set of study
interventions associated with the
Estimand.
ExtensionAttribute
id string
url string
valueString string
valueBoolean Boolean
valueInteger Integer
valueId string
valueRange Range
valueCode Code
valueQuantity Quantity
valueAliasCode AliasCode
extensionAttributes ExtensionAttribute 0..*
valueExtensionClass ExtensionClass 0..1
ExtensionClass
id string
url string
extensionAttributes ExtensionAttribute 1..*
GeographicScope C207591 Geographic
Scope
The extent or range related to the physical
location of an entity.
id string
type Code C207495 Geographic
Scope Type
A characterization or classification of the
geographic scope.
C207412
code AliasCode C207494 Geographic
Scope Code
A symbol or combination of symbols which
is assigned to the geographic scope.
(Point out to
external
dictionaries:
Standard code
is ISO-3166;
Alias codes
drawn from
GENC, UN
Region
Codes, etc.)
GovernanceDate C207595 Study
Governance
Date
Any of the dates associated with event
milestones within a clinical study's
oversight and management framework.
id string
name string C207499 Study
Governance
Date Name
The literal identifier (i.e., distinctive
designation) of the study governance date
description string C207497 Study
Governance
Date Description
A narrative representation of the study
governance date.
label string C207498 Study
Governance
Date Label
The short descriptive designation for the
study governance date.
type Code C207496 Study
Governance
Date Type
A characterization or classification of the
study governance date.
C207413

_(IG page 115)_
22 Updated Controlled Terminology
section
• Small tweak to section on AliasCode to clarify that standard value sets do not
have to be CDISC code lists.
