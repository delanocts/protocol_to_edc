# Organization -- from the USDM Implementation Guide v4.0

_(IG page 21)_
The following diagram presents examples of a sponsor entry and a CRO entry. Organization identifiers need to be
scoped using the identifierScheme attribute as there is no single mechanism to uniquely identify them. In case of a
commercial organization, the organizations DUNS number can be specified to uniquely identify the commercial
entity.

_(IG page 82)_
Class Name Attribute Name Data Type
NCI C-
Code Cardinality Preferred Term Definition Codelist Ref Inherited From
criteria EligibilityCriterion 0..* A USDM relationship between the
PopulationDefinition and EligibilityCriterion
classes which identifies the set of eligibility
criteria associated with the population
definition.
Procedure C98769 Procedure Any activity performed by manual and/or
instrumental means for the purpose of
diagnosis, assessment, therapy,
prevention, or palliative care.
id string
name string C201325 Procedure
Name
The literal identifier (i.e., distinctive
designation) of the procedure.
description string C201324 Procedure
Description
A narrative representation of the
procedure.
label string C207524 Procedure Label The short descriptive designation for the
procedure.
procedureType string C188848 Procedure Type A characterization or classification of the
study procedure.
code Code C154626 Procedure Code A symbol or combination of symbols which
is assigned to medical procedure.
(Point out to
external
dictionary like
CPT,
MedDRA,
SNOMEDCT,
etc.)
notes CommentAnnotation CNEW Procedure
Notes
A brief written record relevant to the
procedure.
studyIntervention StudyIntervention 0..1 A USDM relationship between the
Procedure and StudyInterventionclasses
which provides the details associated with
an instance of an intervention performed
during the conduct of a procedure.
ProductOrganizationRole CNEW Product
Organization
Role
A designation that identifies the function of
an organization within the context of the
product.
id string
name string CNEW Product
Organization
Role Name
The literal identifier (i.e., distinctive
designation) of the product organization
role.
description string CNEW Product
Organization
Role Description
A narrative representation of the product
organization role.
label string CNEW Product
Organization
Role Label
The short descriptive designation for the
product organization role.
code Code CNEW Product
Organization
Role Code
A symbol or combination of symbols which
is assigned to the product organization
role.
CNEW
Product
Organization
Role Code
Value Set
appliesTo AdministrableProduct,
MedicalDevice
0..* A USDM relationship between the
ProductOrganizationRole and either the
AdministrableProduct or MedicalDevice
class that identifies the administrable
product or medical device to which the
product organization role applies.
organization Organization 1 A USDM relationship between the
ProductOrganizationRole and Organization
classes which identifies the organization
associated with the product organization
role.
Quantity C25256 Quantity How much there is of something that can
be measured; the total amount or number.

_(IG page 110)_
Appendices
Appendix A: USDM Team
Name Institution/Organization
John Owen Project Manager, CDISC
Dave Iberson-Hurst USDM Product Owner and Technical Expert, CDISC
Berber Snoeijer USDM Technical Team Lead, CDISC
Erin Muhlbradt Controlled Terminology Expert, NCI-EVS
Craig Zwickl Controlled Terminology Expert, CDISC
Richard Marshall USDM Developer, CDISC
The USDM has been developed in partnership with TransCelerate Biopharma and Accenture. CDISC would like to
acknowledge the support and input from the following groups:
• TransCelerate DDF Core Team
• TransCelerate member company subject-matter experts
• Accenture DDF development team
• CDISC DDF volunteer teams and volunteer vendor organizations

_(IG page 112)_
IMP Investigational medical product
IOS International Organization for Standardization
JSON JavaScript Object Notation
LOINC Logical Observation Identifiers Names and Codes
MedDRA Medical Dictionary for Regulatory Activities. A global standard medical terminology designed to
supersede, in regulatory submissions, other terminologies previously used in the medical product
development process (such as COSTART and ICD9).
MeSH Medical Subject Headings (thesaurus)
NCI EVS (NIH) National Cancer Institute Enterprise Vocabulary Services
NCT National clinical trial
NIH National Institutes of Health
NMP Noninvestigational medical product
ODM Operational Data Model
On-demand USDM training Official USDM educational material available for learners to access from the CDISC learning
management system. Training materials and resources are available to learners at any time and
from any location. This type of training allows individuals to access courses, videos, tutorials, and
other educational content whenever they need it, rather than following a fixed schedule.
Patient A recipient of medical treatment
PHR Personal health record
POV Proof of viability
PRM Protocol Representation Model
PRO Patient-reported outcome
RA Reference architecture
SDM-XML Study/Trial Design Model in XML, extension of ODM-XML
SDR Study Definitions Repository
SDTM Study Data Tabulation Model
SDTMIG SDTM Implementation Guide (for Human Clinical Trials)
SME Subject-matter expert
SNOMED Systemized Nomenclature of Medicine
SOA Schedule of activities
SSU Study start-up
Subject A participant in a study
UDP Utilizing the Digital Protocol (project)
UML Unified modeling language
USDM United Study Definitions Model
USDM-IG USDM Implementation Guide
UUID Universally unique identifier
WHO World Health Organization
XML Extensible markup language
