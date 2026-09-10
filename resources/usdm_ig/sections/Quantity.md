# Quantity -- from the USDM Implementation Guide v4.0

_(IG page 81)_
Class Name Attribute Name Data Type
NCI C-
Code Cardinality Preferred Term Definition Codelist Ref Inherited From
legalAddress Address 0..1 A USDM relationship between the
Organization and Address classes which
provides the legal address for an
organization.
managedSites StudySite 0..* A USDM relationship between the
Organization and StudySite classes which
identifies the set of study sites managed by
the organization.
ParameterMap C207456 Parameter Map The paired name and value for a given
parameter.
id string
tag string C207515 Programming
Tag
Character strings bounded by angle
brackets that act as containers for
programming language elements.
reference string C207516 Programming
Tag Reference
The reference for a tag used in
programming languages, such as a
markup language (e.g., HTML, XML), to
store attributes and elements.
PopulationDefinition C207593 Population
Definition
A concise explanation of the meaning of a
population.
id string
name string C207520 Population
Definition Name
The literal identifier (i.e., distinctive
designation) of the population definition.
description string C207517 Population
Definition
Description
A narrative representation of the
population definition.
label string C207519 Population
Definition Label
The short descriptive designation for the
population definition.
plannedSex Code C207523 Population
Definition
Planned Sex
The protocol-defined sex within the
population definition.
SDTM
Terminology
Codelist
C66732
includesHealthySubjects Boolean C207518 Population
Definition
Includes Healthy
Subjects
Indicator
An indication as to whether the population
definition includes healthy subjects, that is,
subjects without the disease or condition
under study.
plannedAge Range C207701 Population
Definition
Planned Age
The anticipated age of subjects within the
population definition.
plannedCompletionNumberRange Range CNEW Population
Definition
Planned
Completion
Number Range
The range of values representing the
planned number of subjects that must
complete the study in order to meet the
objectives and endpoints of the study,
within the population definition.
plannedCompletionNumberQuantity Quantity CNEW Population
Definition
Planned
Completion
Number
Quantity
The value representing the planned
number of subjects that must complete the
study in order to meet the objectives and
endpoints of the study, within the
population definition.
plannedEnrollmentNumberRange Range CNEW Population
Definition
Planned
Enrollment
Number Range
The range of values representing the
planned number of subjects to be entered
in a clinical trial, within the population
definition.
plannedEnrollmentNumberQuantity Quantity CNEW Population
Definition
Planned
Enrollment
Number
Quantity
The value representing the planned
number of subjects to be entered in a
clinical trial, within the population definition.
notes CommentAnnotation CNEW Population
Definition Notes
A brief written record relevant to the
population definition.

_(IG page 83)_
Class Name Attribute Name Data Type
NCI C-
Code Cardinality Preferred Term Definition Codelist Ref Inherited From
id string
value Float C25712 Quantity Value A numerical quantity measured or
assigned or computed.
unit AliasCode C44258 Quantity Unit The type of unit of measure being used to
express a quantity.
SDTM
Terminology
Codelist
C71620
Range C38013 Range The difference between the lowest and
highest numerical values; the limits or
scale of variation.
id string
minValue Quantity C25570 Minimum Value The smallest value in quantity or degree in
a set of values.
maxValue Quantity C25564 Maximum Value The largest value in quantity or degree in a
set of values.
isApproximate Boolean C207525 Value Range is
Approximate
Indicator
An indication as to whether the value
range is almost, but not quite, exact.
ReferenceIdentifier CNEW Reference
Identifier
A sequence of characters used to identify,
name, or characterize the reference.
id string Identifier
text string CNEW Reference
Identifier Text
An instance of structured text that
represents the reference identifier.
Identifier
scope Organization 1 A USDM relationship between the
ReferenceIdentifier and Organization
classes which provides the details
associated with each organization that has
assigned the reference identifier.
Identifier
type Code CNEW Reference
Identifier Type
A characterization or classification of the
reference identifier.
CNEW
Reference
Identifier Type
ResponseCode C201347 Response Code A symbol or combination of symbols
representing the response to the question.
id string
isEnabled Boolean C201330 Response Code
Enabled
Indicator
An indication as to whether the response
code is activated for use within a given
usage context.
code Code C25162 Code A symbol or combination of symbols which
is assigned to the members of a collection.
ScheduleTimeline C201348 Schedule
Timeline
A chronological schedule of planned
temporal events.
id string
name string C201334 Schedule
Timeline Name
The literal identifier (i.e., distinctive
designation) of the schedule timeline.
description string C201332 Schedule
Timeline
Description
A narrative representation of the schedule
timeline.
label string C207530 Schedule
Timeline Label
The short descriptive designation for the
schedule timeline.
entryCondition string C201333 Schedule
Timeline Entry
Condition
A logical evaluation on which rests the
validity of entry into a schedule timeline.
mainTimeline Boolean C201331 Main Timeline
Indicator
An indication as to whether the timeline or
timeline component is part of the central or
principal timeline.
instances ScheduledInstance 0..* A USDM relationship between the
ScheduleTimeline and ScheduledInstance
classes which identifies the set of
scheduled instances (e.g., scheduled
activity instances or scheduled decision
instances) associated with the scheduled
timeline.
