# StudyElement -- from the USDM Implementation Guide v4.0

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

_(IG page 93)_
Class Name Attribute Name Data Type
NCI C-
Code Cardinality Preferred Term Definition Codelist Ref Inherited From
cohorts StudyCohort 0..* A USDM relationship between the
StudyDesignPopulation and StudyCohort
classes which identifies the set of study
cohorts associated with the study design
population.
StudyElement C142735 Study Design
Element
A basic building block for time within a
clinical study comprising the following
characteristics: a description of what
happens to the subject during the element;
a definition of the start of the element; a
rule for ending the element.
id string
name string C188833 Study Design
Element Name
The literal identifier (i.e., distinctive
designation) of the study design element.
description string C188834 Study Design
Element
Description
A narrative representation of the study
design element.
label string C207554 Study Design
Element Label
The short descriptive designation for the
study design element.
notes CommentAnnotation CNEW Study Element
Notes
A brief written record relevant to the study
element.
transitionEndRule TransitionRule 0..1 A USDM relationship between the
StudyElement and TransitionRule classes
which provides the details associated with
a transition rule used to trigger the end of a
study element.
studyInterventions StudyIntervention 0..* A USDM relationship between the
StudyElement and StudyIntervention
classes which identifies the set of study
interventions associated with the study
element.
transitionStartRule TransitionRule 0..1 A USDM relationship between the
StudyElement and TransitionRule classes
which provides the details associated with
a transition rule used to trigger the start of
a study element.
StudyEpoch C71738 Study Epoch A named time period defined in the
protocol, wherein a study activity is
specified and unchanging throughout the
interval, to support a study-specific
purpose.
id string
name string C93825 Study Epoch
Name
The literal identifier (i.e., distinctive
designation) of the study epoch, i.e., the
named time period defined in the
protocol, wherein a study activity is
specified and unchanging throughout the
interval, to support a study-specific
purpose.
description string C93824 Study Epoch
Description
A narrative representation of the study
epoch.
label string C207555 Study Epoch
Label
The short descriptive designation for the
study epoch.
type Code C188830 Study Epoch
Type
A characterization or classification of the
study epoch, i.e., the named time period
defined in the protocol, wherein a study
activity is specified and unchanging
throughout the interval, to support a study-
specific purpose.
SDTM
Terminology
Codelist
C99079
notes CommentAnnotation CNEW Study Epoch
Notes
A brief written record relevant to the study
epoch.
previous StudyEpoch 0..1 A USDM relationship within the
StudyEpoch class which identifies the

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

_(IG page 116)_
44 Updated Use of USDM for Populating
Protocol Content section
• Updated mappings to align with USDM updates until v3.10
45 3.11
Updated Arms and Epochs section • Updated UML to reflect updated relationship cardinality between StudyCell and
StudyElement classes.
• Updated UML to replace complex datatype relationships with attributes.
