# Masking -- from the USDM Implementation Guide v4.0

_(IG page 20)_
4.9 Study Roles and Organizations
A clinical study may include a number of different roles on different levels (e.g., sponsors, investigators, monitoring
committees). These roles are stored in the StudyRole class. A role may apply to the study as a whole or to 1 or more
of the study designs specified within that study.
Names of persons assigned to a study role are specified in the AssignedPerson class. The actual name is to be
specified in the personName complex datatype attribute which allows for specification of given names, family
names, prefixes and suffixes as well as the complete text of the name. If no specific persons are assigned to the role
then the StudyRole may directly link to an organization that is responsible for the role. The organization type
identifies what kind of organization is specified (e.g., pharmaceutical company, healthcare facility, contract research
organization (CRO), regulatory agency). An identifier should refer to one of the defined organizations as its
scope (see Section 4.7).
An organization can optionally manage 1 or more study sites. These study sites are included to allow for reporting
the subject enrollment status for a site as part of an amendment (see Section 4.6, Study, Protocols, and
Amendments). If a role is masked in a study then this can be further specified in the Masking class.

_(IG page 76)_
Class Name Attribute Name Data Type
NCI C-
Code Cardinality Preferred Term Definition Codelist Ref Inherited From
StudyEpoch classes which identifies the
set of study epochs associated with the
interventional study design.
population StudyDesignPopulation 1 A USDM relationship between the
InterventionalStudyDesign and
StudyDesignPopulation classes which
identifies the population associated with
the interventional study design.
StudyDesign
model Code C98746 Intervention
Model Type
The general design of the strategy for
assigning interventions to subjects in a
clinical study. (clinicaltrials.gov)
SDTM
Terminology
Codelist
C99076
subTypes Code C49660 Trial Type The nature of the interventional study for
which information is being collected.
SDTM
Terminology
Codelist
C66739
blindingSchema AliasCode C49658 Trial Blinding
Schema
The type of experimental design used to
describe the level of awareness of the
study subjects and/ or study personnel as
it relates to the respective intervention(s)
or assessments being observed, received
or administered.
SDTM
Terminology
Codelist
C66735
intentTypes Code C49652 Trial Intent Type The planned purpose of the therapy,
device, or agent under study in the clinical
trial.
SDTM
Terminology
Codelist
C66736
Masking C191278 Masking The mechanism used to obscure the
distinctive characteristics of the study
intervention or procedure to make it
indistinguishable from a comparator.
(CDISC Glossary)
id string
text string CNEW Masking Text An instance of unstructured text that
represents how the masking is performed
and maintained.
isMasked Boolean CNEW Masked
Indicator
An indication as to whether the study role
is masked.
MedicalDevice C16830 Medical Device Any instrument, apparatus, implement,
machine, appliance, implant, reagent for in
vitro use, software, material or other similar
or related article, intended by the
manufacturer to be used, alone or in
combination for, one or more specific
medical purpose(s).[6]
id string
name string CNEW Medical Device
Name
The literal identifier (i.e., distinctive
designation) of the medical device.
description string CNEW Medical Device
Description
A narrative representation of the medical
device.
label string CNEW Medical Device
Label
The short descriptive designation for the
medical device.
hardwareVersion string CNEW Hardware
Version
A form or variant of hardware; one of a
sequence of copies of the physical
components from which a computer is
constructed, each incorporating new
modifications.
softwareVersion string C111093 Software
Version
A form or variant of software; one of a
sequence of copies of a software program,
each incorporating new modifications.
(NCI)
sourcing Code CNEW Medical Device
Sourcing
An indication as to whether the medical
device is obtained from a local or central
source.
CNEW -
Product
Sourcing
Value Set
