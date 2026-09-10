# Timing -- from the USDM Implementation Guide v4.0

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

_(IG page 45)_
In case of an assessment sequence relating to 1 activity (e.g., repeated blood pressure measurements in different
positions), a sub-timeline can be directly referenced from the corresponding activity using the timeline relationship
in this class (see following diagram). The activity A2 (e.g., vital signs), refers to the sub-timeline indicating the
corresponding positioning and assessment actions. For example, put subject in supine position (A3), assess blood
pressure (A4); put subject in standing position (A5) and repeat the blood pressure assessments (A4). The timings in
between are defined by the information in the corresponding Timing class.
See Section 4.14, Study Timing, for more information on timelines.
Footnotes Representing Timing and/or Order of Activities
These footnotes indicate an order of activities and what should be done first, for example:
• Informed consent must be obtained prior to any study-related procedure
• Assessment X should be done before all other ….
• Assessments to be done on day of admission

_(IG page 98)_
Class Name Attribute Name Data Type
NCI C-
Code Cardinality Preferred Term Definition Codelist Ref Inherited From
ParameterMap classes which identifies the
set of parameter maps (parameter map
entries) associated with a syntax template
dictionary.
Timing C80484 Timing The chronological relationship between
temporal events.
id string
name string C207584 Timing Name The literal identifier (i.e., distinctive
designation) of the timing.
description string C164648 Timing
Description
A narrative representation of the
chronological relationship between
temporal events.
label string C207583 Timing Label The short descriptive designation for the
timing.
type Code C201298 Timing Type A characterization or classification of the
chronological relationship between
temporal events.
C201264
relativeToFrom Code C201297 Timing Relative
To From
The name of the reference event used to
define the temporal relationship with
another event.
C201265
value string C201341 Timing Value The temporal value of the chronological
relationship between temporal events.
valueLabel string C207585 Timing Value
Label
The short descriptive designation for the
timing value.
windowLabel string C207586 Timing Window
Label
The short descriptive designation for a time
period, or other type of interval, during
which a temporal event may be achieved,
obtained, or observed.
windowLower string C201342 Timing Window,
Lower
The earliest chronological value of an
allowable period of time during which a
temporal event takes place.
windowUpper string C201343 Timing Window,
Upper
The latest chronological value of an
allowable period of time during which a
temporal event takes place.
relativeToScheduledInstance ScheduledInstance 0..1 A USDM relationship between the Timing
and ScheduledInstance classes which
identifies the scheduled instance (e.g.,
scheduled activity instances or scheduled
decision instances) to which the timing is
relative to.
relativeFromScheduledInstance ScheduledInstance 1 A USDM relationship between the Timing
and ScheduledInstance classes which
identifies the scheduled instance (e.g.,
scheduled activity instances or scheduled
decision instances) to which the timing
applies.
TransitionRule C82567 Transition Rule A guide that governs the allocation of
subjects to operational options at a
discrete decision point or branch (e.g.,
assignment to a particular arm,
discontinuation) within a clinical trial plan.
id string
name string C207588 Transition Rule
Name
The literal identifier (i.e., distinctive
designation) of the transition rule.
description string C188835 Transition Rule
Description
A narrative representation of the transition
rule.
label string C207587 Transition Rule
Label
The short descriptive designation for the
transition rule.
text string C207589 Transition Rule
Text
An instance of unstructured text that
represents the transition rule.

_(IG page 114)_
2 UML update for Study Timing section • Moved relationships timeline and timelineExit.
• Name of encounter attribute environmentalSetting changed to
environmentalSettings.
• Added description for encounter timing - scheduledAt

_(IG page 114)_
11 UML and text update for for Study
Timing section
• Changed cardinality for relativeFromScheduleInstance relationship
• Added corresponding text for anchors relativeToScheduleInstance relationship
should be equal to relativeFromScheduleInstance or missing.
12 3.4
Updated CPT mapping section for
v3.0 and further alignment

_(IG page 117)_
74 Updated Study Timing section • Replaced UML view to reflect new plannedDuration attribute in the
scheduleTimeline class.

_(IG page 117)_
# Release
#
Overview Notes
54 Updated Study Timing section • Updated UML to replace complex datatype relationships with attributes.
