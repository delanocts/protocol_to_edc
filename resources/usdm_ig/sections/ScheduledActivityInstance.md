# ScheduledActivityInstance -- from the USDM Implementation Guide v4.0

_(IG page 23)_
4.11 Activities
Activities are the means by which the procedures to be performed and the data to be captured are specified within a
study design. The Activity class is used to group together data capture and procedures. The composition of these
groupings is left to those designing studies and may align with the activities presented in the schedule of activities.
The presentation ordering in the SOA can be handled with the previous and next attributes. Any presentation
groupings can be handled with the children attribute. Activities can be reused across multiple points within a study
timeline via the ScheduledActivityInstance class (see Section 4.14, Study Timing).

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

_(IG page 30)_
not be. In this example, anchors are used to fix meal times over a single day and the associated observations
scheduled in relation to the fixed meal times. The activities are shared across the steps within the profile.
The profile can be "attached" to an activity using the ActivityTimeLineId attribute so that it is executed as part of
that activity, as illustrated in the following figure. This is useful for a sequence of repeated measures within the same
activity.
The timeline can also be attached to a ScheduledActivityInstance from another timeline using the timeline reference,
thus allowing time points within a visit to be constructed, as shown in the following figure.

_(IG page 32)_
Timeline Exit
It should be noted that the ScheduledTimelineExit instance does not perform any role other than marking the end of
a timeline. It is linked from the last ScheduledActivityInstance instances in the timeline.

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
