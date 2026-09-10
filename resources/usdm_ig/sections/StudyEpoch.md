# StudyEpoch -- from the USDM Implementation Guide v4.0

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

_(IG page 85)_
Class Name Attribute Name Data Type
NCI C-
Code Cardinality Preferred Term Definition Codelist Ref Inherited From
id string ScheduledInstance
name string C207536 Scheduled
Decision
Instance Name
The literal identifier (i.e., distinctive
designation) of the scheduled Decision
instance.
ScheduledInstance
description string C207534 Scheduled
Decision
Instance
Description
A narrative representation of the scheduled
Decision instance.
ScheduledInstance
label string C207535 Scheduled
Decision
Instance Label
The short descriptive designation for the
scheduled Decision instance.
ScheduledInstance
defaultCondition ScheduledInstance 0..1 A USDM relationship within the
ScheduledDecisionInstance class which
identifies the default condition within a
scheduled decision instance.
ScheduledInstance
epoch StudyEpoch 0..1 A USDM relationship between the
ScheduledDecisionInstance and
StudyEpoch classes which identifies the
study epoch associated with a scheduled
decision instance.
ScheduledInstance
conditionAssignments ConditionAssignment 1..* A USDM relationship between the
ScheduledDecisionInstance and
ConditionAssignment classes which
identifies the set of condition assignments
associated with a scheduled decision
instance.
ScheduledInstance C201299 Scheduled
Instance
A scheduled occurrence of a temporal
event.
id string
name string C207455 Scheduled
Instance Name
The literal identifier (i.e., distinctive
designation) of the scheduled instance.
description string C207453 Scheduled
Instance
Description
A narrative representation of the scheduled
instance.
label string C207454 Scheduled
Instance Label
The short descriptive designation for the
scheduled instance.
defaultCondition ScheduledInstance 0..1 A USDM relationship within the
ScheduledInstance class which identifies
the default condition within a scheduled
instance.
epoch StudyEpoch 0..1 A USDM relationship between the
ScheduledInstance and StudyEpoch
classes which identifies the study epoch
associated with a scheduled instance.
Strength CNEW Substance
Strength
The content of an substance expressed
quantitatively per dosage unit, per unit of
volume, or per unit of weight, according to
the pharmaceutical dose form of the
product.
id string
name string CNEW Substance
Strength Name
The literal identifier (i.e., distinctive
designation) of the substance strength.
description string CNEW Substance
Strength
Description
A narrative representation of the substance
strength.
label string CNEW Substance
Strength Label
The short descriptive designation for the
substance strength.
numeratorRange Range CNEW Substance
Strength
Numerator
Range
The lowest and highest numerical values
that define a range for the substance
strength.
numeratorQuantity Quantity CNEW Substance
Strength
The value representing the numerator for
the substance strength.

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
