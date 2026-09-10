# Range -- from the USDM Implementation Guide v4.0

_(IG page 43)_
The attributes and relationships of the SyntaxTemplate class are inherited by any class that is reusing its capabilities
(e.g., Endpoint, EligibilityCriterion, Characteristic, termed "template instances"). The text attribute stores the
structured text of the corresponding endpoint, criterion, or characteristic. The text attribute contains free text with
embedded XHTML tags that refer to the mapping in the SyntaxTemplateDictionary. Within the
SyntaxTemplateDictionary class, dictionaries can be defined that link the tags to the corresponding structured data
references (to data stored elsewhere in the USDM) or to a fixed value.
The tags used within the text attribute of SyntaxTemplate are formatted as follows:
<usdm:tag name="parametername"/>
These tags are used as illustrated in the following example:
Subjects shall be between <usdm:tag name="min_age"/> and <usdm:tag name="max_age"/>
Instances of the SyntaxTemplateDirectory class are linked to 1 or more ParameterMap class instances. Each
ParameterMap instance includes the tag (stored in the tag attribute) and a single reference or fixed value (stored in
the reference attribute):
<usdm:ref klass="klassName" id="idValue" attribute="attributeName"/> or 'fixedValue'
in which:
• klassName is the name of the class that holds the referenced structured data.
• idValue is the id attribute value of the referenced instance of klassName.
• attributeName is the name of the referenced data attribute within klassName.
• fixedValue is a fixed string.
Some examples of ParameterMap references are (formatted here as tag: reference or fixedValue):
min_age: <usdm:ref klass="Range" id="Range_3" attribute="minValue"/>
max_age: <usdm:ref klass="Range" id="Range_3" attribute="maxValue"/>
StudyPopulation: <usdm:ref klass="StudyDesignPopulation" id="StudyDesignPopulation_1"
attribute="description"/>
RefHbMax: "7.0"

_(IG page 81)_
Class Name Attribute Name Data Type
NCI C-
Code Cardinality Preferred Term Definition Codelist Ref Inherited From
legalAddress Address 0..1 A USDM relationship between the
Organization and Address classes which
provides the legal address for an
organization.
managedSites StudySite 0..* A USDM relationship between the
Organization and StudySite classes which
identifies the set of study sites managed by
the organization.
ParameterMap C207456 Parameter Map The paired name and value for a given
parameter.
id string
tag string C207515 Programming
Tag
Character strings bounded by angle
brackets that act as containers for
programming language elements.
reference string C207516 Programming
Tag Reference
The reference for a tag used in
programming languages, such as a
markup language (e.g., HTML, XML), to
store attributes and elements.
PopulationDefinition C207593 Population
Definition
A concise explanation of the meaning of a
population.
id string
name string C207520 Population
Definition Name
The literal identifier (i.e., distinctive
designation) of the population definition.
description string C207517 Population
Definition
Description
A narrative representation of the
population definition.
label string C207519 Population
Definition Label
The short descriptive designation for the
population definition.
plannedSex Code C207523 Population
Definition
Planned Sex
The protocol-defined sex within the
population definition.
SDTM
Terminology
Codelist
C66732
includesHealthySubjects Boolean C207518 Population
Definition
Includes Healthy
Subjects
Indicator
An indication as to whether the population
definition includes healthy subjects, that is,
subjects without the disease or condition
under study.
plannedAge Range C207701 Population
Definition
Planned Age
The anticipated age of subjects within the
population definition.
plannedCompletionNumberRange Range CNEW Population
Definition
Planned
Completion
Number Range
The range of values representing the
planned number of subjects that must
complete the study in order to meet the
objectives and endpoints of the study,
within the population definition.
plannedCompletionNumberQuantity Quantity CNEW Population
Definition
Planned
Completion
Number
Quantity
The value representing the planned
number of subjects that must complete the
study in order to meet the objectives and
endpoints of the study, within the
population definition.
plannedEnrollmentNumberRange Range CNEW Population
Definition
Planned
Enrollment
Number Range
The range of values representing the
planned number of subjects to be entered
in a clinical trial, within the population
definition.
plannedEnrollmentNumberQuantity Quantity CNEW Population
Definition
Planned
Enrollment
Number
Quantity
The value representing the planned
number of subjects to be entered in a
clinical trial, within the population definition.
notes CommentAnnotation CNEW Population
Definition Notes
A brief written record relevant to the
population definition.
