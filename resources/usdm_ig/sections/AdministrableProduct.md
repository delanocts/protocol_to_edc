# AdministrableProduct -- from the USDM Implementation Guide v4.0

_(IG page 63)_
Class Name Attribute Name Data Type
NCI C-
Code Cardinality Preferred Term Definition Codelist Ref Inherited From
productDesignation Code CNEW Administrable
Product Product
Designation
An indication as to whether the
administrable product is an investigational
medicinal product or an auxiliary medicinal
product.
C207418
pharmacologicClass Code CNEW Administrable
Product
Pharmacologic
Class
The pharmacological class of the
administrable product.
(Points to
external
codelists such
as UNII, MED-
RT)
notes CommentAnnotation CNEW Administrable
Product Notes
A brief written record relevant to the
administrable product.
identifiers AdministrableProductIdentifier 0..* A USDM relationship between the
AdministrableProduct and
AdministrableProductIdentifier classes
which provides the set of identifiers related
to the administrable product.
properties AdministrableProductProperty 0..* A USDM relationship between the
AdministrableProduct and
AdministrableProductProperty classes
which provides the set of properties related
to the administrable product.
ingredients Ingredient 0..* A USDM relationship between the
AdministrableProduct and Ingredient
classes which provides the set of
ingredients related to the administrable
product.
AdministrableProductIdentifier CNEW Administrable
Product
Identifier
A sequence of characters used to identify,
name, or characterize the administrable
product.
id string Identifier
text string CNEW Administrable
Product
Identifier Text
An instance of structured text that
represents the administrable product.
Identifier
scope Organization 1 A USDM relationship between the
AdministrableProductIdentifier and
Organization class which provides the
details associated with which provides the
details associated with each organization
that has assigned the administrable
product identifier.
Identifier
AdministrableProductProperty CNEW Administrable
Product
Property
A characteristic from a set of
characteristics used to define an
administrable product.
id string
name string CNEW Administrable
Product
Property Name
The literal identifier (i.e., distinctive
designation) of the administrable product
property.
type Code CNEW Administrable
Product
Property Type
A characterization or classification of the
administrable product property.
CNEW
Administrable
Product
Property Type
text string CNEW Administrable
Product
Property Text
An instance of structured text that
represents the administrable product
property.
quantity Quantity CNEW Administrable
Product
Property
Quantity Value
The numeric value associated with an
administrable product property.
Administration C25409 Administration The act of dispensing, applying, or
tendering a product, agent, or therapy.
id string
name string C207465 Administration
Name
The literal identifier (i.e., distinctive
designation) for the administration of a
product, agent, or therapy.

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
