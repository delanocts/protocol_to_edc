# StudyDesignPopulation -- from the USDM Implementation Guide v4.0

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

_(IG page 43)_
The attributes and relationships of the SyntaxTemplate class are inherited by any class that is reusing its capabilities
(e.g., Endpoint, EligibilityCriterion, Characteristic, termed "template instances"). The text attribute stores the
structured text of the corresponding endpoint, criterion, or characteristic. The text attribute contains free text with
embedded XHTML tags that refer to the mapping in the SyntaxTemplateDictionary. Within the
SyntaxTemplateDictionary class, dictionaries can be defined that link the tags to the corresponding structured data
references (to data stored elsewhere in the USDM) or to a fixed value.
The tags used within the text attribute of SyntaxTemplate are formatted as follows:
<usdm:tag name="parametername"/>
These tags are used as illustrated in the following example:
Subjects shall be between <usdm:tag name="min_age"/> and <usdm:tag name="max_age"/>
Instances of the SyntaxTemplateDirectory class are linked to 1 or more ParameterMap class instances. Each
ParameterMap instance includes the tag (stored in the tag attribute) and a single reference or fixed value (stored in
the reference attribute):
<usdm:ref klass="klassName" id="idValue" attribute="attributeName"/> or 'fixedValue'
in which:
• klassName is the name of the class that holds the referenced structured data.
• idValue is the id attribute value of the referenced instance of klassName.
• attributeName is the name of the referenced data attribute within klassName.
• fixedValue is a fixed string.
Some examples of ParameterMap references are (formatted here as tag: reference or fixedValue):
min_age: <usdm:ref klass="Range" id="Range_3" attribute="minValue"/>
max_age: <usdm:ref klass="Range" id="Range_3" attribute="maxValue"/>
StudyPopulation: <usdm:ref klass="StudyDesignPopulation" id="StudyDesignPopulation_1"
attribute="description"/>
RefHbMax: "7.0"

_(IG page 92)_
Class Name Attribute Name Data Type
NCI C-
Code Cardinality Preferred Term Definition Codelist Ref Inherited From
epochs StudyEpoch 1..* A USDM relationship between the
StudyDesign and StudyEpoch classes
which identifies the set of study epochs
associated with the study design.
population StudyDesignPopulation 1 A USDM relationship between the
StudyDesign and StudyDesignPopulation
classes which identifies the population
associated with the study design.
StudyDesignPopulation C142728 Study Design
Population
The population within the general
population to which the study results can
be generalized.
id string PopulationDefinition
name string C207553 Study Design
Population
Name
The literal identifier (i.e., distinctive
designation) of the study design
population.
PopulationDefinition
description string C70834 Study Design
Population
Description
A narrative representation of the study
design population.
PopulationDefinition
label string C207550 Study Design
Population
Label
The short descriptive designation for the
study design population.
PopulationDefinition
plannedSex Code C207551 Study Design
Population
Planned Sex
The protocol-defined sex within the study
design population.
SDTM
Terminology
Codelist
C66732
PopulationDefinition
includesHealthySubjects Boolean C207549 Study Design
Population
Includes Healthy
Subjects
Indicator
An indication as to whether the study
design population includes healthy
subjects, that is, subjects without the
disease or condition under study.
PopulationDefinition
plannedAge Range C207450 Study Design
Population
Planned Age
The anticipated age of subjects within the
study design population.
PopulationDefinition
plannedCompletionNumberRange Range CNEW Study Design
Population
Planned
Completion
Number Range
The range of values representing the
planned number of subjects that must
complete the study in order to meet the
objectives and endpoints of the study,
within the study design population.
PopulationDefinition
plannedCompletionNumberQuantity Quantity CNEW Study Design
Population
Planned
Completion
Number
Quantity
The value representing the planned
number of subjects that must complete the
study in order to meet the objectives and
endpoints of the study, within the study
design population.
PopulationDefinition
plannedEnrollmentNumberRange Range CNEW Study Design
Population
Planned
Enrollment
Number Range
The range of values representing the
planned number of subjects to be entered
in a clinical trial, within the study design
population.
PopulationDefinition
plannedEnrollmentNumberQuantity Quantity CNEW Study Design
Population
Planned
Enrollment
Number
Quantity
The value representing the planned
number of subjects to be entered in a
clinical trial, within the study design
population.
PopulationDefinition
notes CommentAnnotation CNEW Study Design
Population
Notes
A brief written record relevant to the study
design population.
PopulationDefinition
criteria EligibilityCriterion 0..* A USDM relationship between the
StudyDesignPopulation and
EligibilityCriterion classes which identifies
the set of eligibility criteria associated with
the study design population.
PopulationDefinition
