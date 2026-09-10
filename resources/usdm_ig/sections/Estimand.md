# Estimand -- from the USDM Implementation Guide v4.0

_(IG page 71)_
Class Name Attribute Name Data Type
NCI C-
Code Cardinality Preferred Term Definition Codelist Ref Inherited From
provides information related to the
scheduled timing of an encounter.
previous Encounter 0..1 A USDM relationship within the Encounter
class which identifies the encounter that
chronologically precedes the current
encounter.
Endpoint C25212 Study Endpoint A defined variable intended to reflect an
outcome of interest that is statistically
analyzed to address a particular research
question. NOTE: A precise definition of an
endpoint typically specifies the type of
assessments made, the timing of those
assessments, the assessment tools used,
and possibly other details, as applicable,
such as how multiple assessments within
an individual are to be combined. After
BEST Resource (CDISC Glossary)
id string SyntaxTemplate
name string C207492 Study Endpoint
Name
The literal identifier (i.e., distinctive
designation) of the study endpoint.
SyntaxTemplate
description string C188824 Study Endpoint
Description
A narrative representation of the study
endpoint.
SyntaxTemplate
label string C207491 Study Endpoint
Label
The short descriptive designation for the
study endpoint.
SyntaxTemplate
text string C207493 Study Endpoint
Text
An instance of structured text that
represents the study endpoint.
SyntaxTemplate
notes CommentAnnotation CNEW Endpoint Notes A brief written record relevant to the study
endpoint.
SyntaxTemplate
dictionary SyntaxTemplateDictionary 0..1 A USDM relationship between the
Endpoint and SyntaxTemplateDictionary
classes which provides the set of
dictionary entries related to study
endpoints.
SyntaxTemplate
level Code C188826 Study Endpoint
Level
A characterization or classification of the
study endpoint that determines its category
of importance relative to other study
endpoints.
C188726
purpose string C188825 Study Endpoint
Purpose
Description
The textual representation of the study
endpoint purpose.
Estimand C188813 Estimand A precise description of the treatment
effect reflecting the clinical question posed
by a given clinical trial objective. It
summarises at a population level what the
outcomes would be in the same patients
under different treatment conditions being
compared. (ICH E9 R1 Addendum)
id string
populationSummary string C188853 Population-
Level Summary
A synopsis of the clinical endpoint of
interest within the analysis target study
population.
name string CNEW Estimand Name The literal identifier (i.e., distinctive
designation) of the estimand.
description string CNEW Estimand
Description
A narrative representation of the estimand.
label string CNEW Estimand Label The short descriptive designation for the
estimand.
notes CommentAnnotation CNEW Estimand Notes A brief written record relevant to the study
estimand.
analysisPopulation AnalysisPopulation 1 A USDM relationship between the
Estimand and AnalysisPopulation classes
which provides the details associated with
an instance of the analysis population used
to partially define a study estimand.

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

_(IG page 114)_
8 UML update for Study Objectives and
Endpoints section
• Added notes attributes to Estimand, AnalysisPopulation, IntercurrentEvent,
StudyIntervention and SyntaxTemplate classes.
• Added name, description and label to Estimand class
