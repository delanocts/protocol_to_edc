# StudyArm -- from the USDM Implementation Guide v4.0

_(IG page 23)_
4.10 Arms and Epochs
The high-level study design based on arms and epochs is defined using the StudyArm, StudyEpoch, StudyCell, and
StudyElement classes. The manner in which the classes are used follows the CDISC SDTM. Epochs are related to
the study encounters (a more generic term for visits) via ScheduledInstances that form a ScheduleTimeline (see
Section 4.14, Study Timing). StudyElements can relate to the corresponding studyInterventions that are planned for
the specific StudyArm and in the specific StudyEpoch.
StudyElements and Encounters have entry and exit rules that are defined using the TransitionRule class. It should be
noted that although the StudyElements and Encounter classes share the use of the TransitionRule class, it is not
expected that the instances within any study design will overlap; they are, most likely, distinct sets.
Given that the use of the classes is based on the SDTM, the information within these classes can be used to populate
the SDTM Trial Design domains (see Section 7.1).

_(IG page 88)_
Class Name Attribute Name Data Type
NCI C-
Code Cardinality Preferred Term Definition Codelist Ref Inherited From
notes CommentAnnotation CNEW Study Arm
Notes
A brief written record relevant to the study
arm.
populations PopulationDefinition 0..* A USDM relationship between the
StudyArm and PopulationDefinition classes
which identifies the set of populations
associated with the study arm.
StudyCell C188810 Study Design
Cell
A partitioning of a study arm into individual
pieces, which are associated with an
epoch and any number of sequential
elements within that epoch.
id string
arm StudyArm 1 A USDM relationship between the
StudyCell and StudyArm classes which
identifies the study arm associated with a
study cell.
epoch StudyEpoch 1 A USDM relationship between the
StudyCell and StudyEpoch classes which
identifies the study epoch associated with
a study cell.
elements StudyElement 1..* A USDM relationship between the
StudyCell and StudyElement classes
which identifies the set of study elements
associated with the study cell.
StudyChange CNEW Study Change The act of alteration or modification to a
study.
id string
name string CNEW Study Change
Name
The literal identifier (i.e., distinctive
designation) of the study change.
description string CNEW Study Change
Description
A narrative representation of the study
change.
label string CNEW Study Change
Label
The short descriptive designation for the
study change.
rationale string CNEW Study Change
Rationale
An explanation as to the logical reasons for
why a study change has occurred.
summary string CNEW Study Change
Summary
A short narrative representation describing
the changes introduced in the current
version of the study.
changedSections DocumentContentReference 1..* A USDM relationship between the
StudyChange and
DocumentContentReference class which
provides the set of changed document
sections related to the study change.
StudyCohort C61512 Study Cohort A group of individuals who share a set of
characteristics (e.g., exposures,
experiences, attributes), which logically
defines a population under study.
id string PopulationDefinition
name string C207544 Study Cohort
Name
The literal identifier (i.e., distinctive
designation) of the study cohort.
PopulationDefinition
description string C207542 Study Cohort
Description
A narrative representation of the study
cohort.
PopulationDefinition
label string C207543 Study Cohort
Label
The short descriptive designation for the
study cohort.
PopulationDefinition
plannedSex Code C207541 Study Cohort
Planned Sex
The protocol-defined sex within the study
cohort.
SDTM
Terminology
Codelist
C66732
PopulationDefinition
includesHealthySubjects Boolean C207480 Study Cohort
Includes Healthy
Subjects
Indicator
An indication as to whether the study
cohort includes healthy subjects, that is,
subjects without the disease or condition
under study.
PopulationDefinition
plannedAge Range C207545 Study Cohort
Planned Age
The anticipated age of subjects within the
study cohort.
PopulationDefinition

_(IG page 114)_
Appendix D: Revision History
USDM Implementation Guide
This section details the changes made to the USDMIG between v3.0 and v4.0.
# Release
#
Overview Notes
1 3.2 UML update for Arms and Epochs
section
• Name of encounter attribute environmentalSetting changed to
environmentalSettings
• Added notes attributes to Encounter, StudyArm, StudyElement and StudyEpoch
classes

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
