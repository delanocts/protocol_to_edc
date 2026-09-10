# StudyIntervention -- from the USDM Implementation Guide v4.0

_(IG page 33)_
The following is an example of a bioequivalence study comparing the bioavailability of 1 drug administered via
different devices. The test (experimental intervention) and reference (active comparator) interventions are stored as
2 separate instances in the StudyIntervention class, both as a combination product type of intervention. Because the
experimental intervention includes a device which can be refilled with the administrable product, the medical device
and administrable product are separately linked to the corresponding administration class. Contrary, for the active
comparator study intervention, the product is prefilled and therefore specified as an embedded product for the
medical device.
The actual dose given for both administrations is equal and set to 5 mg. Both interventions refer to the same
administrable product with a strength specified (via its ingredients/substance and strength nominator and
denominator) to be 10 mg/mL. All products are centrally sourced and in this case only 1 product organization role as
supplier was specified and applies to all products. The corresponding organization in this case is a pharmaceutical
company with the hypothetical name Company X.

_(IG page 55)_
document representation of the SOA this can be combined again and explained using footnotes, while a
study design solution allows one to follow the logic within an encounter using expand functionalities.
2. The specific assessments within each phase are modeled using sub-timelines (see section 4.14, Study
Timing) for both the hypoglycemic induction phase and the treatment phase. This allows for clearness in
timing in relation to the specific administration. In a document representation, these sub-timelines are often
represented as separate tables or as footnote instructions.
3. The additional advantage of a sub-timeline is that they can be referenced multiple times (e.g., in a crossover
study or repeat-cycle study). In this crossover example, each sub-timeline is referenced both from period 1
and from period 2.
4. All activities and corresponding labels (usually presented in the left column of the SOA) are stored in the
Activity class. In this example, only the dosing activities are shown.
a. The activity "Insulin infusion to Induce Hypolglycemia" includes a specific start-administration
procedure which refers to the corresponding study intervention instance.
b. The activity "Study Treatment Administration" includes 2 different procedures, 1 for the new test drug
administration and 1 for the reference drug administration. A condition in the context of the activity is
applicable to both procedures to indicate that the administration of either is based on randomization.
5. For each kind of intervention, a separate StudyIntervention instance is stored in the StudyIntervention part
of the USDM. This includes details on administration duration, administrable product, and corresponding
ingredients and strengths. Additional notes may be added if helpful for downstream processes, for example
to include more instructions on preparation and administration as shown in the example for the human
regular insulin administrable product. (For more information on this part of the model, see Section 4.15,
Study Interventions.)

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
7 UML update for Study Interventions
section
• Added notes attributes to StudyIntervention and AgentAdministration classes.

_(IG page 114)_
8 UML update for Study Objectives and
Endpoints section
• Added notes attributes to Estimand, AnalysisPopulation, IntercurrentEvent,
StudyIntervention and SyntaxTemplate classes.
• Added name, description and label to Estimand class
