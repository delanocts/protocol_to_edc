# EligibilityCriterion -- from the USDM Implementation Guide v4.0

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

_(IG page 69)_
Class Name Attribute Name Data Type
NCI C-
Code Cardinality Preferred Term Definition Codelist Ref Inherited From
ConditionAssignment C201335 Condition
Assignment
An allotting or appointment to a condition
or set of conditions that are to be met in
order to make a logical decision.
id string
condition string C47953 Logical
Condition
An assumption on which rests the validity
or effect of something else.
conditionTarget ScheduledInstance 1 A USDM relationship between the
ConditionAssignment and
ScheduledInstance classes which
identifies the scheduled instance
associated with the condition assignment.
DocumentContentReference CNEW Document
Content
Reference
A citation pointing to the location of specific
content within a document.
id string
sectionNumber string CNEW Document
Content
Reference
Section Number
The numeric identifier of a particular
section for the document content
reference.
sectionTitle string CNEW Document
Content
Reference
Section Title
An identifying designation for a particular
section for the document content
reference.
appliesTo StudyDefinitionDocument 1 A USDM relationship between the
DocumentContentReference and
StudyDefinitionDocument classes which
identifies the study definition document to
which the document content reference
applies.
EligibilityCriterion C16112 Study Eligibility
Criterion
Characteristics which are necessary to
allow a subject to participate in a clinical
study, as outlined in the study protocol.
The concept covers inclusion and
exclusion criteria.
id string
name string C207488 Study Eligibility
Criterion Name
The literal identifier (i.e., distinctive
designation) of the study eligibility criterion.
description string C207486 Study Eligibility
Criterion
Description
A narrative representation of the study
eligibility criterion.
label string C207487 Study Eligibility
Criterion Label
The short descriptive designation for the
study eligibility criterion.
identifier string C207489 Study Eligibility
Criterion
Identifier
A sequence of characters used to identify,
name, or characterize the inclusion or
exclusion criterion.
category Code C83016 Study Eligibility
Criterion
Category
A classification of the inclusion exclusion
criterion.
SDTM
Terminology
Codelist
C66797
notes CommentAnnotation CNEW Eligibility
Criterion Notes
A brief written record relevant to the
eligibility criterion.
criterionItem EligibilityCriterionItem 1 A USDM relationship between the
EligibilityCriterion and
EligibilityCriterionItem classes which
identifies the item belonging to the
eligibility criterion.
next EligibilityCriterion 0..1 A USDM relationship within the
EligibilityCriterion class which identifies the
eligibility criterion that follows the current
eligibility criterion in the display order.
previous EligibilityCriterion 0..1 A USDM relationship within the
EligibilityCriterion class which identifies the
eligibility criterion that precedes the current
eligibility criterion in the display order.

_(IG page 114)_
3 UML and text update for Populations,
Cohorts, and Eligibility Criteria section
• Added relationship criteria from StudyVersion to EligibilityCriterion.
• Changed criteria cardinality from PopulationDefinition to EligibilityCriterion from
1..* to 0..* in UML.
• Added notes attributes to PopulationDefinition, SyntaxTemplate, Indication,
StudyArm, StudyDesign and StudyVersion classes.
• Updated text accordingly to specify that criteria should either be referenced from
Study Population or from Study Cohort.
• Updated text regarding eligibility criteria: removed reference to context attribute
and specify that they are defined within a study version.
• Added explanation of previous/next criteria
