# StudyVersion -- from the USDM Implementation Guide v4.0

_(IG page 16)_
4.7 Study Identifiers and Titles
Study identifiers, reference identifiers, and titles are stored in separate dedicated classes (as presented in the
following UML) and are referred to from the StudyVersion class. A study identifier specifically identifies the study
represented in the data model. A reference identifier is optional and identifies an overarching plan (e.g., pediatric
investigational plan number, clinical development plan number).

_(IG page 17)_
One or more study titles are required for a study. They can be of different types (e.g., official, scientific, short titles).
If available, the acronym should be stored as a title as well, specifying the type as acronym.
The StudyVersion class allows for including 1 or more study identifiers. Although multiple identifiers are permitted,
the study definition should have 1, and only 1, sponsor identifier. A sponsor identifier is identified by its scope of an
organization that has the Sponsor study role as shown in the following instance diagram. Identifiers of co-sponsors
may be linked in a similar fashion to the co-sponsor study role.
Registry identifiers (e.g., NCT, EudraCT) should refer to a clinical study registry organization type as presented in
the following diagram.

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

_(IG page 114)_
5 UML update for Study Identifiers and
Titles
• Added notes attribute to StudyVersion class.

_(IG page 114)_
4 UML update for Study, Protocols, and
Amendments section
• Added notes attributes to StudyVersion and StudyDesign classes.

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
