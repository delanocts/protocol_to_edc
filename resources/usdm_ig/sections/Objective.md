# Objective -- from the USDM Implementation Guide v4.0

_(IG page 34)_
4.16 Study Objectives and Endpoints
The study design objectives and endpoints can be defined within the Objective class and the Endpoint class. The
Objective class allows for the textual description of the objective and its level (e.g., primary, secondary, exploratory)
and a link to 1 or more associated endpoints containing the endpoint definition in textual form. Both classes inherit
from the syntax template (see Section 4.21), allowing for references to information stored elsewhere in the data
model. The endpoint may be a variable of interest for the study estimand (see Section 4.17).

_(IG page 78)_
Class Name Attribute Name Data Type
NCI C-
Code Cardinality Preferred Term Definition Codelist Ref Inherited From
NarrativeContentItem CNEW Narrative
Content Item
An individual item within the container that
holds an instance of unstructured text and
which may include objects such as tables,
figures, and images.
id string
name string CNEW Narrative
Content Item
Name
The literal identifier (i.e., distinctive
designation) of the narrative content item.
text string CNEW Narrative
Content Item
Text
An instance of unstructured text that
represents the narrative content item.
Objective C142450 Study Objective The reason for performing a study in terms
of the scientific questions to be answered
by the analysis of data collected during the
study.
id string SyntaxTemplate
name string C207512 Study Objective
Name
The literal identifier (i.e., distinctive
designation) of the study objective.
SyntaxTemplate
description string C94090 Study Objective
Description
A narrative representation of the study
objective. (BRIDG)
SyntaxTemplate
label string C207511 Study Objective
Label
The short descriptive designation for the
study objective.
SyntaxTemplate
text string C207513 Study Objective
Text
An instance of structured text that
represents the study objective.
SyntaxTemplate
notes CommentAnnotation CNEW Objective Notes A brief written record relevant to the study
objective.
SyntaxTemplate
dictionary SyntaxTemplateDictionary 0..1 A USDM relationship between the
Objective and SyntaxTemplateDictionary
classes which provides the set of
dictionary entries related to study
objectives.
SyntaxTemplate
level Code C188823 Study Objective
Level
A characterization or classification of the
study objective that determines its
category of importance relative to other
study objectives.
C188725
endpoints Endpoint 0..* A USDM relationship between the
Objective and Endpoint classes which
identifies the set of endpoints associated
with the study objective.
ObservationalStudyDesign CNEW Observational
Study Design
The strategy that specifies the structure of
an observational study in terms of the
planned activities (including timing) and
statistical analysis approach intended to
meet the objectives of the study.
id string StudyDesign
name string CNEW Observational
Study Design
Name
The literal identifier (i.e., distinctive
designation) of the observational study
design.
StudyDesign
description string CNEW Observational
Study Design
Description
A narrative representation of the
observational study design.
StudyDesign
label string CNEW Observational
Study Design
Label
The short descriptive designation for the
observational study design.
StudyDesign
rationale string CNEW Observational
Study Design
Rationale
Reason(s) for choosing the observational
study design. This may include reasons for
the choice of control or comparator, as well
as the scientific rationale for the study
design.
StudyDesign
therapeuticAreas Code CNEW Observational
Study Design
Therapeutic
Areas
A categorization of a disease, disorder, or
other condition based on common
characteristics and often associated with a
medical specialty focusing on research and
development of specific therapeutic
(Point out to
external
dictionaries)
StudyDesign

_(IG page 99)_
6.2 Serialization
When expressing USDM data in a monolithic, hierarchical document format (e.g., JSON, XML), the same element
will appear multiple times because the model uses only class references for USDM entities. This is not optimal for
an API and, so as not to repeat the same information within the JSON structure, the API has been designed to
include an instance once and only once and allow for zero, 1, or more references to it as dictated by the USDM and
the relationships therein. This mechanism relies on the unique identifiers of each class.
To ensure no duplication of content in the API JSON format, the following steps are taken to translate the logical
USDM into the JSON format:
1. Where content is shared (referenced from 2 or more places), the "natural parent" relationship is identified.
An example is the Endpoint class that is referenced from both the Objective and Estimand classes.
Objective is considered the natural parent.
2. If a natural parent can be identified in the API, then the content of the child is included in the corresponding
item of the natural parent (attribute names remain unchanged) and other relationships are added as cross-
references, with the attribute names modified with a suffix of "Id" (singular) or "Ids" (plural) relationships.
The datatype is modified to string so as to accommodate the cross-references and the corresponding
identifiers.
3. If the natural parent cannot be identified, then a "collection" from a logical higher level class is formed and
all relationships to this class in the logical model are added as cross-references in the API with the
corresponding naming modifications as specified in step 2. This results in an additional relationship in the
API for the higher level class to the collection. An example is for the class BiomedicalConcepts, where a
collection is placed within the StudyDesign class.
