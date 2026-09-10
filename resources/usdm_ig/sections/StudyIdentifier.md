# StudyIdentifier -- from the USDM Implementation Guide v4.0

_(IG page 94)_
Class Name Attribute Name Data Type
NCI C-
Code Cardinality Preferred Term Definition Codelist Ref Inherited From
study epoch that chronologically precedes
the current study epoch.
next StudyEpoch 0..1 A USDM relationship within the
StudyEpoch class which identifies the
study epoch that chronologically follows
the current study epoch.
StudyIdentifier C83082 Study Identifier A sequence of characters used to identify,
name, or characterize the study.
id string Identifier
text string CNEW Study Identifier
Text
An instance of structured text that
represents the study identifier.
Identifier
scope Organization 1 A USDM relationship between the
StudyIdentifier and Organization classes
which provides the details associated with
each organization that has assigned the
study identifier.
Identifier
StudyIntervention C207649 Study
Intervention
Any agent, device, or procedure being
tested or used as a reference or
comparator in the conduct of a clinical trial.
id string
description string C207647 Study
Intervention
Description
A narrative representation of the study
intervention.
name string C207558 Study
Intervention
Name
The literal identifier (i.e., distinctive
designation) of the study intervention.
label string C207556 Study
Intervention
Label
The short descriptive designation for the
study intervention.
role Code C207560 Study
Intervention
Role
The intended use of the trial intervention
within the context of the study design.
C207417
type Code C98747 Study
Intervention
Type
The kind of product or procedure studied in
a trial.
SDTM
Terminology
Codelist
C99078
codes Code C207648 Study
Intervention
Code
A symbol or combination of symbols which
is assigned to the study intervention.
(Point out to
multiple
Biomedical
coding
dictionaries
such as
WHODrug,
ATC, UNII,
etc.)
minimumResponseDuration Quantity C207557 Study
Intervention
Minimum
Response
Duration
The value representing the minimum
amount of time required to meet the criteria
for response to study intervention.
notes CommentAnnotation CNEW Study
Intervention
Notes
A brief written record relevant to the study
intervention.
administrations Administration 0..* A USDM relationship between the
StudyIntervention and AgentAdministration
classes which identifies the set of agent
administrations associated with the study
intervention.
StudyRole CNEW Study Role A designation that identifies the function of
study personnel or an organization within
the context of the study.
id string
name string CNEW Study Role
Name
The literal identifier (i.e., distinctive
designation) of the study role.

_(IG page 96)_
Class Name Attribute Name Data Type
NCI C-
Code Cardinality Preferred Term Definition Codelist Ref Inherited From
dateValues GovernanceDate 0..* A USDM relationship between the
StudyVersion and GovernanceDate
classes which provides the set of
governance dates associated with the
study version.
referenceIdentifiers ReferenceIdentifier 0..* A USDM relationship between the
StudyVersion and ReferenceIdentifier
classes which identifies the set of
reference identifiers associated with the
study version.
amendments StudyAmendment 0..* A USDM relationship between the
StudyVersion and StudyAmendment
classes which identifies the set of study
amendments associated with the study
version.
documentVersions StudyDefinitionDocumentVersi
on
0..* A USDM relationship between the
StudyVersion and
StudyDefinitionDocumentVersion classes
which identifies the version of the study
definition document associated with the
study version.
studyDesigns StudyDesign 0..* A USDM relationship between the
StudyVersion and StudyDesign classes
which identifies the set of study designs
associated with the study version.
studyIdentifiers StudyIdentifier 1..* A USDM relationship between the
StudyVersion and StudyIdentifier classes
which identifies the set of study identifiers
associated with the study version.
titles StudyTitle 1..* A USDM relationship between the
StudyVersion and StudyTitle classes which
identifies the set of study titles associated
with the study version.
SubjectEnrollment C37948 Subject
Enrollment
The act of enrolling subjects into a study.
The subject will have met the
inclusion/exclusion criteria to participate in
the trial and will have signed an informed
consent form. (CDISC Glossary)
id string
name string CNEW Subject
Enrollment
Name
The literal identifier (i.e., distinctive
designation) of the subject enrollment.
description string CNEW Subject
Enrollment
Description
A narrative representation of the subject
enrollment.
label string CNEW Subject
Enrollment
Label
The short descriptive designation for the
subject enrollment..
quantity Quantity C207573 Subject
Enrollment
Quantity Value
The value representing the number of
individuals enrolled in a study.
forGeographicScope GeographicScope 0..1 A USDM relationship between the
SubjectEnrollment and GeographicScope
classes which identifies the geographic
scope to which the subject enrollment
applies.
forStudyCohort StudyCohort 0..1 A USDM relationship between the
SubjectEnrollment and StudyCohort
classes which identifies the study cohort to
which the subject enrollment applies.
forStudySite StudySite 0..1 A USDM relationship between the
SubjectEnrollment and StudySite classes
which identifies the study site to which the
subject enrollment applies.

_(IG page 100)_
API Required Content
When sending data using the API, it is recommended that the data include the following:
1. There is only 1 StudyVersion.
2. There is 1 StudyIdentifier within the StudyVersion which is scoped by an organization that is referred to by
the clinical study sponsor (C70793) role.
3. There is at least 1 StudyDesign within the StudyVersion.
