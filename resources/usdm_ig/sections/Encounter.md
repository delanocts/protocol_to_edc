# Encounter -- from the USDM Implementation Guide v4.0

_(IG page 28)_
<Timing.relativeToScheduledInstance> node". The timing definition allows for further precision in the timing by
specifying the relativeToFrom type.
For anchors, the relativeFrom node refers to the scheduled instance that provides the fixed reference. The
corresponding relativeTo node should either refer to the same scheduled instance or should be missing.
A timing may be referenced from an Encounter using the scheduleAt attribute allowing for a specific encounter
timing and corresponding windowing to be defined and presented in a scheduled of activities. An Encounter timing
might potentially overarch multiple scheduledInstances representing different blocks of activities within an
encounter.
Note: In the timing diagrams, the relativeFromScheduledInstance and relativeToScheduledInstance relationships
have been shortened ("From" and "To," respectively) so as to make the diagrams readable.
Planned timings are stored in the value attribute of the Timing class and are expected to be formatted according to
ISO 8601. A corresponding window can be identified using the window attributes. The windowLower and
windowUpper attributes are also expected to be formatted according to ISO 8601. Textual representations of these
values can be stored in the valueLabel and windowLabel attributes, respectively.
Timings can be defined between each consecutive scheduled instance or all or part of the timings can be related to a
fixed (anchor) timepoint:

_(IG page 48)_
Footnotes Representing Optional Alternative Encounter Methods
These footnotes specify potential encounter methods, such as:
• Performed by telephone by qualified staff
• If regulatory allowed, visits may take place at home
The encounter methods are specified by the attributes environmentalSetting and contactModes in the Encounter
class. If optional alternative encounter methods are allowed then more than 1 contactMode and/or environmental
setting may be specified.
Footnotes Representing Measurements to Be Done for a Specified Activity
In most protocols the exact assessments to be done are specified in dedicated paragraphs. However, in some cases,
they are specified in the footnotes of the SOA, for example:
• Hematology must include CBC with differential including but not limited to ….
• T/B/NK cell count (i.e. CD3, CD4, CD8, CD19, CD16/56)
These assessments can be specified as BCs and linked to the corresponding SOA activity as shown in the following
diagram.

_(IG page 70)_
Class Name Attribute Name Data Type
NCI C-
Code Cardinality Preferred Term Definition Codelist Ref Inherited From
EligibilityCriterionItem CNEW Eligibility
Criterion Item
An individual item within the container that
holds an instance of an eligibility criterion.
id string SyntaxTemplate
name string CNEW Eligibility
Criterion Item
Name
The literal identifier (i.e., distinctive
designation) of the eligibility criterion item.
SyntaxTemplate
description string CNEW Eligibility
Criterion Item
Description
A narrative representation of the eligibility
criterion item.
SyntaxTemplate
label string CNEW Eligibility
Criterion Item
Label
The short descriptive designation for the
eligibility criterion item.
SyntaxTemplate
text string CNEW Eligibility
Criterion Item
Text
An instance of structured text that
represents the eligibility criterion item.
SyntaxTemplate
notes CommentAnnotation CNEW Eligibility
Criterion Item
Notes
A brief written record relevant to the
eligibility criterion item.
SyntaxTemplate
dictionary SyntaxTemplateDictionary 0..1 A USDM relationship between the
EligibilityCriterionItem and
SyntaxTemplateDictionary classes which
provides the dictionary entry associated
with a eligibility criterion item.
SyntaxTemplate
Encounter CNEW Study Encounter Any physical or virtual contact between two
or more parties involved in a study, at
which an assessment or activity takes
place.
id string
name string C171010 Study Encounter
Name
The literal identifier (i.e., distinctive
designation) for a protocol-defined study
encounter.
description string C188836 Study Encounter
Description
A narrative representation of the protocol-
defined study encounter.
label string C207490 Study Encounter
Label
The short descriptive designation for the
study encounter.
type Code C188839 Study Encounter
Type
A characterization or classification of the
study encounter.
C188728
environmentalSettings Code C188840 Environmental
Setting
The environment/setting where the event,
intervention, or finding occurred.
SDTM
Terminology
Codelist
C127262
contactModes Code C188841 Contact Mode The means by which an interaction occurs
between the subject/participant and person
or entity (e.g., a device).
SDTM
Terminology
Codelist
C171445
notes CommentAnnotation CNEW Encounter
Notes
A brief written record relevant to the study
encounter.
transitionEndRule TransitionRule 0..1 A USDM relationship between the
Encounter and TransitionRule classes
which provides the details associated with
a transition rule used to trigger the end of
an encounter.
next Encounter 0..1 A USDM relationship within the Encounter
class which identifies the encounter that
chronologically follows the current
encounter.
transitionStartRule TransitionRule 0..1 A USDM relationship between the
Encounter and TransitionRule classes
which provides the details associated with
a transition rule used to trigger the start of
an encounter.
scheduledAt Timing 0..1 A USDM relationship between the
Encounter and Timing classes which

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
