# Activity -- from the USDM Implementation Guide v4.0

_(IG page 23)_
4.11 Activities
Activities are the means by which the procedures to be performed and the data to be captured are specified within a
study design. The Activity class is used to group together data capture and procedures. The composition of these
groupings is left to those designing studies and may align with the activities presented in the schedule of activities.
The presentation ordering in the SOA can be handled with the previous and next attributes. Any presentation
groupings can be handled with the children attribute. Activities can be reused across multiple points within a study
timeline via the ScheduledActivityInstance class (see Section 4.14, Study Timing).

_(IG page 25)_
4.12 Procedures
The procedures linked to the Activity class allow for the procedures required by the activity to be detailed. A
procedure consists of a free-text name and description; procedures can be classified using a free-text type attribute
and coded using the code attribute. In cases where the procedure includes a study intervention (e.g., drug
administration), the corresponding study intervention can be referenced.

_(IG page 27)_
A timeline is named and can be referenced or reused within other timelines. The steps within a timeline link the
encounters with the activities required for each step and thus define the timing for the encounters. The
ScheduledActivityInstance class is the link between the high-level study design defined by the StudyArms and
StudyEpochs classes, the Encounter classes, and the detailed study design defined by the Activity class.
Timing
The timing between steps comprises a relative time of before or after, and an anchor time that is fixed. The
following figure illustrates the timing capabilities. The Timing class allows for explicit timing to be built into a
timeline using a combination of anchors (fixed timing) and relative timing. The timing definitions should be read as
"the <Timing.relativeFromScheduledInstance> node is <Timing.value> <Timing.type of before or after> the

_(IG page 61)_
5 USDM Data Dictionary
Note: Properties without a description in the following table are either relationships or instance identifiers and were deemed to be out of scope for terminology
development. Please see Section 4.4, Internal Identifiers Within the Model, for additional information on the use of identifier variables in the model.
Class Name Attribute Name Data Type
NCI C-
Code Cardinality Preferred Term Definition Codelist Ref Inherited From
Abbreviation C42610 Abbreviation A set of letters that are drawn from a word
or from a sequence of words and that are
used for brevity in place of the full word or
phrase. (CDISC Glossary)
id string
abbreviatedText string C42610 Abbreviation A set of letters that are drawn from a word
or from a sequence of words and that are
used for brevity in place of the full word or
phrase. (CDISC Glossary)
expandedText string CNEW Abbreviation
Long Name
The full literal representation of the
abbreviation.
notes CommentAnnotation CNEW Abbreviation
Notes
A brief written record relevant to the
abbreviation.
Activity C71473 Study Activity An action, undertaking, or event, which is
anticipated to be performed or observed,
or was performed or observed, according
to the study protocol during the execution
of the study.
id string
name string C188842 Study Activity
Name
The literal identifier (i.e., distinctive
designation) of the study activity.
description string C70960 Study Activity
Description
A narrative representation of the study
activity.
label string C207458 Study Activity
Label
The short descriptive designation for the
study activity.
notes CommentAnnotation CNEW Activity Notes A brief written record relevant to the
activity.
definedProcedures Procedure 0..* A USDM relationship between the Activity
and Procedure classes which identifies the
set of defined procedures associated with
the activity.
biomedicalConcepts BiomedicalConcept 0..* A USDM relationship between the Activity
and BiomedicalConcept classes which
identifies the set of biomedical concepts
associated with the activity.
next Activity 0..1 A USDM relationship within the Activity
class which identifies the activity that
follows the current activity in the display
order.
timeline ScheduleTimeline 0..1 A USDM relationship between the Activity
and ScheduleTimeline classes which
provides the details associated with an
instance of the scheduled timeline related
to the activity.
children Activity 0..* A USDM relationship within the Activity
class which identifies the set of child
activities associated with an activity.
previous Activity 0..1 A USDM relationship within the Activity
class which identifies the activity that
precedes the current activity in the display
order.

_(IG page 114)_
6 UML and text update for Activities
section
• Added notes attribute to Activity, Procedure, BiomedicalConcept,
BiomedicalConceptSurrogate, BiomedicalConceptCategory, and
BiomedicalConceptProperty classes.
• Added ScheduleTimeline class to the UML view
• Explained the use of timeline attribute in the Activity class

_(IG page 114)_
9 UML update for Syntax Templates
section
• Added notes attribute to SyntaxTemplate class.
10 3.3
UML and text update for Activities
section
• Added children attribute to Activity class
• Added example to explain how SoA activities are stored in the Activity class with
respect to the previous, next and children attributes.

_(IG page 117)_
61 Updated Overview section • Updated text to align with version 4.0
62 Created Schedule of Activity Views
section
• Pictured a simple SoA in different formats
• Described a number of suggestions for deploying USDM SoA information.

_(IG page 118)_
77 Updated Schedule of Activity Views
section
• Changed 'created of patient journeys' to 'creation of patient journeys'
