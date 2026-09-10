# InterventionalStudyDesign -- from the USDM Implementation Guide v4.0

_(IG page 18)_
4.8 Study Design
The StudyDesign class is the container for a single design within a study definition. It can be either an observational
study design (ObservationalStudyDesign class) or an interventional study design (InterventionalStudyDesign class).
Both classes inherit all the study design features from the StudyDesign class and include references to study
timelines (see Section 4.14, Study Timing); objectives and endpoints (Section 4.16); populations (see Section 4.18);
study interventions (see Section 4.15); and design elements like arms, epochs, and encounters (see Section 4.10). It
provides slots for key parameters such as therapeutic area, study phase, and study type. Specific interventional or
observational study design parameters referring to their own specific controlled terminology are stored in the
corresponding classes. Trial types are stored as subTypes in the InterventionalStudyDesign class as well as intent
types, blinding schema, and intervention model. Observational subtypes and model are stored in the
ObservationalStudyDesign class together with timePerspective and samplingMethod.

_(IG page 75)_
Class Name Attribute Name Data Type
NCI C-
Code Cardinality Preferred Term Definition Codelist Ref Inherited From
activities Activity 0..* A USDM relationship between the
InterventionalStudyDesign and Activity
classes which identifies the set of activities
associated with the interventional study
design.
StudyDesign
biospecimenRetentions BiospecimenRetention 0..* A USDM relationship between the
InterventionalStudyDesign and
BiospecimenRetention classes which
identifies the status of biospecimen
retentions related to the interventional
study design.
StudyDesign
encounters Encounter 0..* A USDM relationship between the
InterventionalStudyDesign and Encounter
classes which identifies the set of
encounters associated with the
interventional study design.
StudyDesign
estimands Estimand 0..* A USDM relationship between the
InterventionalStudyDesign and Estimand
classes which identifies the set of
estimands associated with the
interventional study design.
StudyDesign
indications Indication 0..* A USDM relationship between the
InterventionalStudyDesign and Indication
classes which identifies the set of
indications associated with the
interventional study design.
StudyDesign
objectives Objective 0..* A USDM relationship between the
InterventionalStudyDesign and Objective
classes which identifies the set of
objectives associated with the
interventional study design.
StudyDesign
scheduleTimelines ScheduleTimeline 0..* A USDM relationship between the
InterventionalStudyDesign and
ScheduleTimeline classes which identifies
the set of scheduled timelines associated
with the interventional study design.
StudyDesign
arms StudyArm 1..* A USDM relationship between the
InterventionalStudyDesign and StudyArm
classes which identifies the set of study
arms associated with the interventional
study design.
StudyDesign
studyCells StudyCell 1..* A USDM relationship between the
InterventionalStudyDesign and StudyCell
classes which identifies the set of study
cells associated with the interventional
study design.
StudyDesign
documentVersions StudyDefinitionDocumentVersi
on
0..* A USDM relationship between the
InterventionalStudyDesign and
StudyDefinitionDocumentVersion classes
which identifies the version of the study
definition documents associated with the
interventional study design.
StudyDesign
elements StudyElement 0..* A USDM relationship between the
InterventionalStudyDesign and
StudyElement classes which identifies the
set of study elements associated with the
interventional study design.
StudyDesign
studyInterventions StudyIntervention 0..* A USDM relationship between the
InterventionalStudyDesign and
StudyIntervention classes which identifies
the set of study interventions associated
with interventional study design.
StudyDesign
epochs StudyEpoch 1..* A USDM relationship between the
InterventionalStudyDesign and
StudyDesign
