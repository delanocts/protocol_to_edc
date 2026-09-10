# StudyDesign -- from the USDM Implementation Guide v4.0

_(IG page 79)_
Class Name Attribute Name Data Type
NCI C-
Code Cardinality Preferred Term Definition Codelist Ref Inherited From
interventions for the purpose of treatment
and prevention, which is associated with
the observational study design.
studyType Code CNEW Observational
Study Design
Study Type
The study type associated with the
observational study design.
SDTM
Terminology
Codelist
C99077
StudyDesign
characteristics Code CNEW Observational
Study Design
Characteristics
The distinguishing qualities or prominent
aspects of an observational study design.
C207416 StudyDesign
studyPhase AliasCode CNEW Observational
Study Design
Study Phase
The study phase associated with the
observational study design.
SDTM
Terminology
Codelist
C66737
StudyDesign
notes CommentAnnotation CNEW Observational
Study Design
Notes
A brief written record relevant to the
observational study design.
StudyDesign
activities Activity 0..* A USDM relationship between the
ObservationalStudyDesign and Activity
classes which identifies the set of activities
associated with the observational study
design.
StudyDesign
biospecimenRetentions BiospecimenRetention 0..* A USDM relationship between the
ObservationalStudyDesign and
BiospecimenRetention classes which
identifies the status of biospecimen
retentions related to the observational
study design.
StudyDesign
encounters Encounter 0..* A USDM relationship between the
ObservationalStudyDesign and Encounter
classes which identifies the set of
encounters associated with the
observational study design.
StudyDesign
estimands Estimand 0..* A USDM relationship between the
ObservationalStudyDesign and Estimand
classes which identifies the set of
estimands associated with the
observational study design.
StudyDesign
indications Indication 0..* A USDM relationship between the
ObservationalStudyDesign and Indication
classes which identifies the set of
indications associated with the
observational study design.
StudyDesign
objectives Objective 0..* A USDM relationship between the
ObservationalStudyDesign and Objective
classes which identifies the set of
objectives associated with the
observational study design.
StudyDesign
scheduleTimelines ScheduleTimeline 0..* A USDM relationship between the
ObservationalStudyDesign and
ScheduleTimeline classes which identifies
the set of scheduled timelines associated
with the observational study design.
StudyDesign
arms StudyArm 1..* A USDM relationship between the
ObservationalStudyDesign and StudyArm
classes which identifies the set of study
arms associated with the observational
study design.
StudyDesign
studyCells StudyCell 1..* A USDM relationship between the
ObservationalStudyDesign and StudyCell
classes which identifies the set of study
cells associated with the observational
study design.
StudyDesign

_(IG page 91)_
Class Name Attribute Name Data Type
NCI C-
Code Cardinality Preferred Term Definition Codelist Ref Inherited From
categorized into four (sometimes five)
phases. A therapeutic intervention may be
evaluated in two or more phases
simultaneously in different trials, and some
trials may overlap two different phases. 21
CFR section 312.21; After ICH Topic E8
NOTE FOR GUIDANCE ON GENERAL
CONSIDERATIONS FOR CLINICAL
TRIALS, CPMP/ICH/291/95 March 1998
notes CommentAnnotation CNEW Study Design
Notes
A brief written record relevant to the study
design.
activities Activity 0..* A USDM relationship between the
StudyDesign and Activity classes which
identifies the set of activities associated
with the study design.
biospecimenRetentions BiospecimenRetention 0..* A USDM relationship between the
StudyDesign and BiospecimenRetention
classes which identifies the status of
biospecimen retentions related to the study
design.
encounters Encounter 0..* A USDM relationship between the
StudyDesign and Encounter classes which
identifies the set of encounters associated
with the study design.
estimands Estimand 0..* A USDM relationship between the
StudyDesign and Estimand classes which
identifies the set of estimands associated
with the study design.
indications Indication 0..* A USDM relationship between the
StudyDesign and Indication classes which
identifies the set of indications associated
with the study design.
objectives Objective 0..* A USDM relationship between the
StudyDesign and Objective classes which
identifies the set of objectives associated
with the study design.
scheduleTimelines ScheduleTimeline 0..* A USDM relationship between the
StudyDesign and ScheduleTimeline
classes which identifies the set of
scheduled timelines associated with the
study design.
arms StudyArm 1..* A USDM relationship between the
StudyDesign and StudyArm classes which
identifies the set of study arms associated
with the study design.
studyCells StudyCell 1..* A USDM relationship between the
StudyDesign and StudyCell classes which
identifies the set of study cells associated
with the study design.
documentVersions StudyDefinitionDocumentVersi
on
0..* A USDM relationship between the
StudyDesign and
StudyDefinitionDocumentVersion classes
which identifies the version of the study
definition documents associated with the
study design.
elements StudyElement 0..* A USDM relationship between the
StudyDesign and StudyElement classes
which identifies the set of study elements
associated with the study design.
studyInterventions StudyIntervention 0..* A USDM relationship between the
StudyDesign and StudyIntervention
classes which identifies the set of study
interventions associated with study design.

_(IG page 114)_
4 UML update for Study, Protocols, and
Amendments section
• Added notes attributes to StudyVersion and StudyDesign classes.

_(IG page 116)_
39 Updated Populations, Cohorts, and
Eligibility Criteria section
• Updated UML to reflect new StudyDesign subclasses.

_(IG page 116)_
41 Updated Study Objectives and
Endpoints section
• Updated UML to reflect dependency on StudyDesign class and the different
subclasses.
