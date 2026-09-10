# StudyTitle -- from the USDM Implementation Guide v4.0

_(IG page 95)_
Class Name Attribute Name Data Type
NCI C-
Code Cardinality Preferred Term Definition Codelist Ref Inherited From
label string CNEW Study Role
Label
The short descriptive designation for the
study role.
description string CNEW Study Role
Description
A narrative representation of the study
role.
code Code CNEW Study Role
Code
A symbol or combination of symbols which
is assigned to the study role.
CNEW Study
Role Code
assignedPersons AssignedPerson 0..* A USDM relationship between the
StudyRole and AssignedPerson classes
that identifies the set of individuals that are
assigned to fill a particular role within the
study.
masking Masking 0..1 A USDM relationship between the
StudyRole and Masking classes which
describes the masking associated with the
study role.
organizations Organization 0..* A USDM relationship between the
StudyRole and Organization classes which
identifies the set of organizations
associated with the study role.
appliesTo StudyDesign, StudyVersion 0..* A USDM relationship between the
StudyRole and either StudyVersion or
StudyDesign classes that identifies the
study version or study design to which the
study role applies.
StudySite C80403 Study Site The location at which a study investigator
conducts study activities.
id string
name string C207566 Study Site
Name
The literal identifier (i.e., distinctive
designation) of the study site.
description string C207564 Study Site
Description
A narrative representation of the study site.
label string C207565 Study Site Label The short descriptive designation for the
study site.
country Code C170990 Country of
Study Site
The country in which the study site is
located.
(Point out to
ISO 3166-1
Alpha-3
Country code)
StudyTitle C49802 Study Title The sponsor-defined name of the clinical
study.
id string
type Code C207568 Study Title Type A characterization or classification of the
study title.
C207419
text string C207567 Study Title Text An instance of unstructured text that
represents the study title.
StudyVersion C188816 Study Version A plan at a particular point in time for a
study.
id string
versionIdentifier string C207570 Study Version
Identifier
A sequence of characters used to identify,
name, or characterize the study version.
businessTherapeuticAreas Code C201322 Business
Therapeutic
Areas
A therapeutic area classification based on
the structure and operations of the
business unit.
(Point out to
external
dictionaries)
rationale string C94122 Study Rationale A statement describing the overall
rationale of the study. This field describes
the contribution of this study to product
development, i.e., what knowledge is being
contributed from the conduct of this study.
notes CommentAnnotation CNEW Study Version
Notes
A brief written record relevant to the study
version.
abbreviations Abbreviation 0..* A USDM relationship between the
StudyVersion and Abbreviation classes
which provides the set of abbreviations
associated with the study version.

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
