# EligibilityCriterionItem -- from the USDM Implementation Guide v4.0

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

_(IG page 117)_
67 Updated the mapping to other
standards sections
• Added the new references to the EligibilityCriterionItem class.
68 3.13 Updated Study, Protocols, and
Amendments section
• Replaced UML view to reflect new label and description attributes for
StudyAmendment class.
• Replaced UML view to reflect move of children attribute from
StudyDefinitionDocumentVersion to StudyDefinitionDocument
