# Study -- from the USDM Implementation Guide v4.0

_(IG page 87)_
Class Name Attribute Name Data Type
NCI C-
Code Cardinality Preferred Term Definition Codelist Ref Inherited From
changes StudyChange 1..* A USDM relationship between the
StudyAmendment and StudyChange
classes which identifies the set of changes
associated with the study amendment.
previous StudyAmendment 0..1 A USDM relationship within the
StudyAmendment class which identifies
the study amendment that chronologically
precedes the current study amendment.
primaryReason StudyAmendmentReason 1 A USDM relationship between the
StudyAmendment and
StudyAmendmentReason classes which
identifies the primary reason for issuing the
study amendment.
StudyAmendmentImpact CNEW Study
Amendment
Impact
The effect or consequence of an
amendment on some aspect of the study.
id string
text string CNEW Study
Amendment
Impact Text
An instance of unstructured text that
represents the study amendment impact.
isSubstantial Boolean C207538 Study
Amendment
Impact
Substantial
Indicator
An indication as to whether the study
amendment's impact on the study is
substantial.
type Code CNEW Study
Amendment
Impact Type
A characterization or classification of the
study amendment impact.
CNEW Study
Amendment
Impact Type
Response
notes CommentAnnotation CNEW Study
Amendment
Impact Notes
A brief written record relevant to the study
amendment impact.
StudyAmendmentReason C207457 Study
Amendment
Reason
The rationale for the change(s) to, or
formal clarification of, a protocol.
id string
otherReason string C207539 Other Reason
for Study
Amendment
The rationale for the change(s) to, or
formal clarification of, a protocol that is not
otherwise specified.
code Code C207540 Study
Amendment
Reason Code
A symbol or combination of symbols which
is assigned to the study amendment
reason.
C207415
StudyArm C174447 Study Arm A planned pathway assigned to the subject
as they progress through the study, usually
referred to by a name that reflects one or
more treatments, exposures, and/or
controls included in the path.
id string
name string C170984 Study Arm
Name
The literal identifier (i.e., distinctive
designation) of the study arm.
description string C93728 Study Arm
Description
A narrative representation of the study
arm.
label string C172456 Study Arm Label The short descriptive designation for the
study arm.
type Code C188827 Study Arm Type A characterization or classification of the
study arm.
Protocol
Terminology
Codelist
C174222
dataOriginType Code C188829 Study Arm Data
Origin Type
A characterization or classification of the
study arm with respect to where the study
arm data originates.
C188727
dataOriginDescription string C188828 Study Arm Data
Origin
Description
The textual representation of the study arm
data origin.

_(IG page 114)_
5 UML update for Study Identifiers and
Titles
• Added notes attribute to StudyVersion class.

_(IG page 114)_
4 UML update for Study, Protocols, and
Amendments section
• Added notes attributes to StudyVersion and StudyDesign classes.

_(IG page 114)_
7 UML update for Study Interventions
section
• Added notes attributes to StudyIntervention and AgentAdministration classes.

_(IG page 114)_
14 Updated Study, Protocols, and
Amendments section to include
multiple template support
• Updated UML.
• Adjusted text to refer to the right classes.

_(IG page 115)_
30 Updated Study Objectives and
Endpoints section
• updated UML to include new estimand changes

_(IG page 115)_
28 Updated Study Design section • Added UML
• Updated text to indicate all referenced areas not reflected in UML and explain
other references
29 3.8
Updated Study Design section • Updated UML to include studyDocumentVersions relationship
• Added reference to Study, Protocols, and Amendments

_(IG page 115)_
17 Updated Study, Protocols, and
Amendments section.
• Created cross-reference to Abbreviations section.

_(IG page 115)_
24 Updated Study Roles and
Organizations section
• Changed section name from 'Organizations' to 'Study Roles and Organizations'.
• Updated UML to include significant changes in the model.
• Updated text to explain this part of the model and expected use.
25 3.7
Updated Study Identifiers and Titles
section
• Changed address line to lines in UML

_(IG page 115)_
26 Updated Study Roles and
Organizations section
• Changed address line to lines in UML
27 Updated Study, Protocols, and
Amendments section
• Updated UML and text to include studyAmendMentChange,
StudyAmendmentImpact and changes to the studyEnrollment class
• Moved abbreviation part out of UML and text to abbreviation section.

_(IG page 115)_
21 Updated Study Interventions section • Updated UML to include all changes for the new model version.
• Updated explanation of the model and included some references to IDMP.

_(IG page 116)_
41 Updated Study Objectives and
Endpoints section
• Updated UML to reflect dependency on StudyDesign class and the different
subclasses.

_(IG page 116)_
51 Updated Study Identifiers and Titles
section
• Updated UML to replace complex datatype relationships with attributes.
• Restructured text order for readability purposes.

_(IG page 116)_
52 Updated Study Design section • Updated UML to replace complex datatype relationships with attributes.
• Updated UML to correct blindingSchema datatype and align with API

_(IG page 117)_
55 Updated Study Objectives and
Endpoints section
• Updated UML to replace complex datatype relationships with attributes.

_(IG page 117)_
74 Updated Study Timing section • Replaced UML view to reflect new plannedDuration attribute in the
scheduleTimeline class.

_(IG page 117)_
# Release
#
Overview Notes
54 Updated Study Timing section • Updated UML to replace complex datatype relationships with attributes.

_(IG page 118)_
76 Updated Study Design section • Replaced UML view to reflect move of children attribute from
StudyDefinitionDocumentVersion to StudyDefinitionDocument
