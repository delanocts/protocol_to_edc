# StudyCohort -- from the USDM Implementation Guide v4.0

_(IG page 35)_
4.18 Populations, Cohorts, and Eligibility Criteria
Populations and cohorts are a (sub-)group of subjects that take part in the study. The parent class
PopulationDefinition is used to define a group of subjects in general. This class includes references to the eligibility
criteria that are applicable to the population. All the elements of the PopulationDefinition class are inherited by both
the StudyDesignPopulation class, which stores the population details for a specific study design; and the
StudyCohort class, which stores the details of a subpopulation that, based on subject characteristics, may deviate in
how they are treated, assessed, or analyzed.
In addition to the inherited attributes from the PopulationDefinition class, the StudyDesignPopulation class may
refer to the corresponding subgroups stored as study cohorts. The standard PopulationDefinition attributes criteria,

_(IG page 89)_
Class Name Attribute Name Data Type
NCI C-
Code Cardinality Preferred Term Definition Codelist Ref Inherited From
plannedCompletionNumberRange Range CNEW Study Cohort
Planned
Completion
Number Range
The range of values representing the
planned number of subjects that must
complete the study in order to meet the
objectives and endpoints of the study,
within the study cohort.
PopulationDefinition
plannedCompletionNumberQuantity Quantity CNEW Study Cohort
Planned
Completion
Number
Quantity
The value representing the planned
number of subjects that must complete the
study in order to meet the objectives and
endpoints of the study, within the study
cohort.
PopulationDefinition
plannedEnrollmentNumberRange Range CNEW Study Cohort
Planned
Enrollment
Number Range
The range of values representing the
planned number of subjects to be entered
in a clinical trial, within the study cohort.
PopulationDefinition
plannedEnrollmentNumberQuantity Quantity CNEW Study Cohort
Planned
Enrollment
Number
Quantity
The value representing the planned
number of subjects to be entered in a
clinical trial, within the study cohort.
PopulationDefinition
notes CommentAnnotation CNEW Study Cohort
Notes
A brief written record relevant to the study
cohort.
PopulationDefinition
criteria EligibilityCriterion 0..* A USDM relationship between the
StudyCohort and EligibilityCriterion classes
which identifies the set of eligibility criteria
associated with the study cohort.
PopulationDefinition
characteristics Characteristic 0..* A USDM relationship between the
StudyCohort and Characteristic classes
which identifies the set of subject
characteristics associated with the study
cohort.
indications Indication 0..* A USDM relationship between the
StudyCohort and Indication classes which
identifies the set of indications associated
with the study cohort.
StudyDefinitionDocument CNEW Study Definition
Document
Any physical or electronic document that is
related to defining a study or part of a
study.
id string
name string CNEW Study Definition
Document
Name
The literal identifier (i.e., distinctive
designation) of the study definition
document.
description string CNEW Study Definition
Document
Description
A narrative representation of the study
definition document.
label string CNEW Study Definition
Document Label
The short descriptive designation for the
study definition document.
type Code CNEW Study Definition
Document Type
A characterization or classification of the
study definition document.
CNEW Study
Definition
Document
Type
templateName string CNEW Study Definition
Document
Template Name
The literal identifier (i.e., distinctive
designation) of the study definition
document template.
language Code CNEW Study Definition
Document
Language
The language in which the study definition
document is written.
(Point out to
ISO 639
language
value list)
notes CommentAnnotation CNEW Study Definition
Document
Notes
A brief written record relevant to the study
definition document.
versions StudyDefinitionDocumentVersi
on
0..* A USDM relationship between the
StudyDefinitionDocument and
StudyDefinitionDocumentVersion classes
which identifies the set of versions
