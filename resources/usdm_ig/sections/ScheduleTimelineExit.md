# ScheduleTimelineExit -- from the USDM Implementation Guide v4.0

_(IG page 26)_
4.14 Study Timing
One of the key aspects of a study design is the timing of encounters (visits) and the activities to be performed within
those encounters. The USDM includes a mechanism for building timelines that can be reused within a study and,
given external library management, across studies. The corresponding classes and attributes are shown in the
following UML diagram. This model allows for multiple planned timings within an encounter as well as for decision
points in the study process. The corresponding information is stored in a timeline as scheduled activity instances and
scheduled decision instances, respectively. Both inherit all attributes and relationships from the ScheduledInstance
class (indicated by the closed arrows in the UML) and can be linked to the corresponding study epoch. The Timing
class includes all timing information with details on time between instances and corresponding windowing. One or
more scheduled activity instance can be related to a corresponding encounter, which is usually presented as a visit in
the schedule of activities.
Timelines
The study timing mechanism depicted in the following figure is based on the notion of a timeline. A timeline is
composed of an entry point with an associated entry condition (see ScheduleTimeline class), a sequence of steps (the
ScheduledActivityInstance class and scheduledDecisionInstance class), timing relating the steps (the Timing class),
and 1 or more exits (the ScheduleTimelineExit class) that mark the end of timeline processing. The planned duration
of a timeline can optionally be specified, which for the main timeline reflects the planned total study duration.

_(IG page 84)_
Class Name Attribute Name Data Type
NCI C-
Code Cardinality Preferred Term Definition Codelist Ref Inherited From
entry ScheduledInstance 1 A USDM relationship between the
ScheduleTimeline and ScheduledInstance
classes which defines the entry into a
scheduled instance (e.g., scheduled
activity instances or scheduled decision
instances) for a timeline.
exits ScheduleTimelineExit 0..* A USDM relationship between the
ScheduleTimeline and
ScheduleTimelineExit classes which
identifies the set of exits from the
scheduled timeline.
timings Timing 0..* A USDM relationship between the
ScheduleTimeline and Timing classes
which identifies the set of timings
associated with the scheduled timeline.
ScheduleTimelineExit C201349 Schedule
Timeline Exit
To go out of or leave the schedule timeline.
id string
ScheduledActivityInstance C201350 Scheduled
Activity Instance
A scheduled occurrence of an activity
event.
id string ScheduledInstance
name string C207533 Scheduled
Activity Instance
Name
The literal identifier (i.e., distinctive
designation) of the scheduled activity
instance.
ScheduledInstance
description string C207531 Scheduled
Activity Instance
Description
A narrative representation of the scheduled
activity instance.
ScheduledInstance
label string C207532 Scheduled
Activity Instance
Label
The short descriptive designation for the
scheduled activity instance.
ScheduledInstance
defaultCondition ScheduledInstance 0..1 A USDM relationship within the
ScheduledActivityInstance class which
identifies the default condition within a
scheduled activity instance.
ScheduledInstance
epoch StudyEpoch 0..1 A USDM relationship between the
ScheduledActivityInstance and
StudyEpoch classes which identifies the
study epoch associated with a scheduled
activity instance.
ScheduledInstance
activities Activity 0..* A USDM relationship between the
ScheduledActivityInstance and Activity
classes which identifies the set of activities
associated with a scheduled activity
instance.
encounter Encounter 0..1 A USDM relationship between the
ScheduledActivityInstance and Encounter
classes which defines the subject
encounter associated with the
ScheduleActivityInstance.
timeline ScheduleTimeline 0..1 A USDM relationship between the
ScheduledActivityInstance and
ScheduleTimeline classes which provides
the details associated with an instance of a
scheduled timeline related to a scheduled
activity instance.
timelineExit ScheduleTimelineExit 0..1 A USDM relationship between the
ScheduledActivityInstance and
ScheduleTimelineExit classes which
provides the details associated with the
exit from a timeline related to a scheduled
activity instance.
ScheduledDecisionInstance C201351 Scheduled
Decision
Instance
A scheduled occurrence of a decision
event.
