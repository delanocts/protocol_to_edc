# Administration -- from the USDM Implementation Guide v4.0

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

_(IG page 64)_
Class Name Attribute Name Data Type
NCI C-
Code Cardinality Preferred Term Definition Codelist Ref Inherited From
description string C207463 Administration
Description
A narrative representation for the
administration of a product, agent, or
therapy.
label string C207464 Administration
Label
The short descriptive designation for the
administration of a product, agent, or
therapy.
dose Quantity C167190 Administration
Dose
The value representing the amount of an
agent given to an individual at one time.
frequency AliasCode C89081 Dosing
Frequency
The number of doses administered per a
specific interval.
SDTM
Terminology
Codelist
C71113
route AliasCode C38114 Route of
Administration
The pathway by which a substance is
administered in order to reach the site of
action in the body.
SDTM
Terminology
Codelist
C66729
notes CommentAnnotation CNEW Administration
Notes
A brief written record relevant to the
administration of the product, agent, or
therapy.
administrableProduct AdministrableProduct 0..1 A USDM relationship between the
Administration and
AdministrableProductDefinition classes
which identifies the administrable product
associated with the administration of the
product, agent, or therapy.
duration AdministrationDuration 1 A USDM relationship between the
Administration and AdministrationDuration
classes which provides the duration of an
instance of product, agent, or therapy
administration.
medicalDevice MedicalDevice 0..1 A USDM relationship between the
Administration and MedicalDevice classes
which identifies the medical device
associated with an instance of product,
agent, or therapy administration.
AdministrationDuration C69282 Administration
Duration
The amount of time elapsed during the
administration of an agent.
id string
description string C207459 Administration
Duration
Description
A narrative representation of the agent
administration duration.
quantity Quantity C207460 Administration
Duration
Quantity Value
The value representing the amount of time
over which the administration of an agent
occurs.
durationWillVary Boolean C207461 Administration
Duration Will
Vary Indicator
An indication as to whether the agent
administration duration is planned to vary
within and/or across subjects.
reasonDurationWillVary string C207462 Administration
Duration
Reason
Duration Will
Vary
The explanation for why the agent
administration duration will vary within
and/or across subjects.
AliasCode C201344 Alias Code An alternative symbol or combination of
symbols which is assigned to the members
of a collection.
id string
standardCode Code CNEW Standard Code A combination of symbols that is used to
represent the standard code.
standardCodeAliases Code CNEW Standard Code
Aliases
Alternative combinations of symbols used
to represent aliases or alternatives to the
standard code.
AnalysisPopulation C188814 Analysis
Population
A target study population on which an
analysis is performed. These may be
represented by the entire study population,
