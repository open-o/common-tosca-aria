#
# Copyright (c) 2016 GigaSpaces Technologies Ltd. All rights reserved.
# 
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
# 
#      http://www.apache.org/licenses/LICENSE-2.0
# 
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.
#

from .misc import Description, MetaData, Repository, Import, SubstitutionMappings
from .definitions import ParameterDefinition
from .assignments import PropertyAssignment, AttributeAssignment, RequirementAssignment, CapabilityAssignment, InterfaceAssignment, ArtifactAssignment
from .types import ArtifactType, DataType, CapabilityType, InterfaceType, RelationshipType, NodeType, GroupType, PolicyType
from .filters import NodeFilter
from .presentation.extensible import ExtensiblePresentation
from .presentation.field_validators import copy_validator, policy_targets_validator
from .modeling.properties import get_assigned_and_defined_property_values, get_parameter_values
from .modeling.interfaces import get_template_interfaces
from .modeling.requirements import get_template_requirements
from .modeling.capabilities import get_template_capabilities
from .modeling.artifacts import get_inherited_artifact_definitions
from .modeling.policies import get_policy_targets
from .modeling.copy import get_default_raw_from_copy
from aria import dsl_specification
from aria.utils import ReadOnlyDict, ReadOnlyList, cachedmethod
from aria.presentation import has_fields, primitive_field, primitive_list_field, object_field, object_list_field, object_dict_field, object_sequenced_list_field, field_validator, type_validator, list_type_validator

@has_fields
@dsl_specification('3.7.3', 'tosca-simple-profile-1.0')
class NodeTemplate(ExtensiblePresentation):
    """
    A Node Template specifies the occurrence of a manageable software component as part of an application's topology model which is defined in a TOSCA Service Template. A Node template is an instance of a specified Node Type and can provide customized properties, constraints or operations which override the defaults provided by its Node Type and its implementations.
    
    See the `TOSCA Simple Profile v1.0 cos01 specification <http://docs.oasis-open.org/tosca/TOSCA-Simple-Profile-YAML/v1.0/cos01/TOSCA-Simple-Profile-YAML-v1.0-cos01.html#DEFN_ENTITY_NODE_TEMPLATE>`__
    """

    @field_validator(type_validator('node type', 'node_types'))
    @primitive_field(str, required=True)
    def type(self):
        """
        The required name of the Node Type the Node Template is based upon.
        
        :rtype: str
        """

    @object_field(Description)
    def description(self):
        """
        An optional description for the Node Template.
        
        :rtype: :class:`Description`
        """

    @primitive_list_field(str)
    def directives(self):
        """
        An optional list of directive values to provide processing instructions to orchestrators and tooling.
        
        :rtype: list of str
        """

    @object_dict_field(PropertyAssignment)
    def properties(self):
        """
        An optional list of property value assignments for the Node Template.
        
        :rtype: dict of str, :class:`PropertyAssignment`
        """

    @object_dict_field(AttributeAssignment)
    def attributes(self):
        """
        An optional list of attribute value assignments for the Node Template.
        
        :rtype: dict of str, :class:`AttributeAssignment`
        """

    @object_sequenced_list_field(RequirementAssignment)
    def requirements(self):
        """
        An optional sequenced list of requirement assignments for the Node Template.
        
        :rtype: list of (str, :class:`RequirementAssignment`)
        """

    @object_dict_field(CapabilityAssignment)
    def capabilities(self):
        """
        An optional list of capability assignments for the Node Template.
        
        :rtype: dict of str, :class:`CapabilityAssignment`
        """

    @object_dict_field(InterfaceAssignment)
    def interfaces(self):
        """
        An optional list of named interface definitions for the Node Template.
        
        :rtype: dict of str, :class:`InterfaceAssignment`
        """

    @object_dict_field(ArtifactAssignment)
    def artifacts(self):
        """
        An optional list of named artifact definitions for the Node Template.
        
        :rtype: dict of str, :class:`ArtifactAssignment`
        """

    @object_field(NodeFilter)
    def node_filter(self):
        """
        The optional filter definition that TOSCA orchestrators would use to select the correct target node. This keyname is only valid if the directive has the value of "selectable" set.
        
        :rtype: :class:`NodeFilter`
        """

    @field_validator(copy_validator('node template', 'node_templates'))
    @primitive_field(str)
    def copy(self):
        """
        The optional (symbolic) name of another node template to copy into (all keynames and values) and use as a basis for this node template.
        
        :rtype: str
        """
    
    @cachedmethod
    def _get_default_raw(self):
        return get_default_raw_from_copy(self, 'node_templates')
    
    @cachedmethod
    def _get_type(self, context):
        return context.presentation.get_from_dict('service_template', 'node_types', self.type)

    @cachedmethod
    def _get_property_values(self, context):
        return ReadOnlyDict(get_assigned_and_defined_property_values(context, self))

    @cachedmethod
    def _get_requirements(self, context):
        return ReadOnlyList(get_template_requirements(context, self))

    @cachedmethod
    def _get_capabilities(self, context):
        return ReadOnlyDict(get_template_capabilities(context, self))

    @cachedmethod
    def _get_interfaces(self, context):
        return ReadOnlyDict(get_template_interfaces(context, self, 'node template'))
    
    @cachedmethod
    def _get_artifacts(self, context):
        return ReadOnlyDict(get_inherited_artifact_definitions(context, self))

    def _validate(self, context):
        super(NodeTemplate, self)._validate(context)
        self._get_property_values(context)
        self._get_requirements(context)
        self._get_capabilities(context)
        self._get_interfaces(context)
        self._get_artifacts(context)

    def _dump(self, context):
        self._dump_content(context, (
            'description',
            'type',
            'directives',
            'properties',
            'attributes',
            'requirements',
            'capabilities',
            'interfaces',
            'artifacts',
            'node_filter',
            'copy'))

@has_fields
@dsl_specification('3.7.4', 'tosca-simple-profile-1.0')
class RelationshipTemplate(ExtensiblePresentation):
    """
    A Relationship Template specifies the occurrence of a manageable relationship between node templates as part of an application's topology model that is defined in a TOSCA Service Template. A Relationship template is an instance of a specified Relationship Type and can provide customized properties, constraints or operations which override the defaults provided by its Relationship Type and its implementations.
    
    See the `TOSCA Simple Profile v1.0 cos01 specification <http://docs.oasis-open.org/tosca/TOSCA-Simple-Profile-YAML/v1.0/cos01/TOSCA-Simple-Profile-YAML-v1.0-cos01.html#DEFN_ENTITY_RELATIONSHIP_TEMPLATE>`__
    """

    @field_validator(type_validator('relationship type', 'relationship_types'))
    @primitive_field(str, required=True)
    def type(self):
        """
        The required name of the Relationship Type the Relationship Template is based upon.
        
        :rtype: str
        """

    @object_field(Description)
    def description(self):
        """
        An optional description for the Relationship Template.
        
        :rtype: :class:`Description`
        """

    @object_dict_field(PropertyAssignment)
    def properties(self):
        """
        An optional list of property assignments for the Relationship Template.
        
        :rtype: dict of str, :class:`PropertyAssignment`
        """

    @object_dict_field(AttributeAssignment)
    def attributes(self):
        """
        An optional list of attribute assignments for the Relationship Template.
        
        :rtype: dict of str, :class:`AttributeAssignment`
        """

    @object_dict_field(InterfaceAssignment)
    def interfaces(self):
        """
        An optional list of named interface definitions for the Node Template.
        
        ARIA NOTE: Spec is wrong here, should be Relationship Template.
        
        :rtype: dict of str, :class:`InterfaceAssignment`
        """

    @field_validator(copy_validator('relationship template', 'relationship_templates'))
    @primitive_field(str)
    def copy(self):
        """
        The optional (symbolic) name of another relationship template to copy into (all keynames and values) and use as a basis for this relationship template.
        
        :rtype: str
        """

    @cachedmethod
    def _get_default_raw(self):
        return get_default_raw_from_copy(self, 'relationship_templates')

    @cachedmethod
    def _get_type(self, context):
        return context.presentation.get_from_dict('service_template', 'relationship_types', self.type)

    @cachedmethod
    def _get_property_values(self, context):
        return ReadOnlyDict(get_assigned_and_defined_property_values(context, self))

    @cachedmethod
    def _get_interfaces(self, context):
        return ReadOnlyDict(get_template_interfaces(context, self, 'relationship template'))
    
    def _validate(self, context):
        super(RelationshipTemplate, self)._validate(context)
        self._get_property_values(context)
        self._get_interfaces(context)

    def _dump(self, context):
        self._dump_content(context, (
            'description',
            'type',
            'properties',
            'attributes',
            'interfaces',
            'copy'))

@has_fields
@dsl_specification('3.7.5', 'tosca-simple-profile-1.0')
class GroupTemplate(ExtensiblePresentation):
    """
    A group definition defines a logical grouping of node templates, typically for management purposes, but is separate from the application's topology template.
    
    See the `TOSCA Simple Profile v1.0 cos01 specification <http://docs.oasis-open.org/tosca/TOSCA-Simple-Profile-YAML/v1.0/cos01/TOSCA-Simple-Profile-YAML-v1.0-cos01.html#DEFN_ELEMENT_GROUP_DEF>`__
    """

    @field_validator(type_validator('group type', 'group_types'))
    @primitive_field(str, required=True)
    def type(self):
        """
        The required name of the group type the group definition is based upon.
        
        :rtype: str
        """

    @object_field(Description)
    def description(self):
        """
        The optional description for the group definition.
        
        :rtype: :class:`Description`
        """

    @object_dict_field(PropertyAssignment)
    def properties(self):
        """
        An optional list of property value assignments for the group definition.
        
        :rtype: dict of str, :class:`PropertyAssignment`
        """

    @field_validator(list_type_validator('node template', 'topology_template', 'node_templates'))
    @primitive_list_field(str)
    def members(self):
        """
        The optional list of one or more node template names that are members of this group definition.
        
        :rtype: list of str
        """

    @object_dict_field(InterfaceAssignment)
    def interfaces(self):
        """
        An optional list of named interface definitions for the group definition.
        
        :rtype: dict of str, :class:`InterfaceDefinition`
        """

    @cachedmethod
    def _get_type(self, context):
        return context.presentation.get_from_dict('service_template', 'group_types', self.type)

    @cachedmethod
    def _get_property_values(self, context):
        return ReadOnlyDict(get_assigned_and_defined_property_values(context, self))

    @cachedmethod
    def _get_interfaces(self, context):
        return ReadOnlyDict(get_template_interfaces(context, self, 'group definition'))
    
    def _validate(self, context):
        super(GroupTemplate, self)._validate(context)
        self._get_property_values(context)
        self._get_interfaces(context)

@has_fields
@dsl_specification('3.7.6', 'tosca-simple-profile-1.0')
class PolicyTemplate(ExtensiblePresentation):
    """
    A policy definition defines a policy that can be associated with a TOSCA topology or top-level entity definition (e.g., group definition, node template, etc.).
    
    See the `TOSCA Simple Profile v1.0 cos01 specification <http://docs.oasis-open.org/tosca/TOSCA-Simple-Profile-YAML/v1.0/cos01/TOSCA-Simple-Profile-YAML-v1.0-cos01.html#DEFN_ELEMENT_POLICY_DEF>`__
    """

    @field_validator(type_validator('policy type', 'policy_types'))
    @primitive_field(str, required=True)
    def type(self):
        """
        The required name of the policy type the policy definition is based upon.
        
        :rtype: str
        """

    @object_field(Description)
    def description(self):
        """
        The optional description for the policy definition.
        
        :rtype: :class:`Description`
        """

    @object_dict_field(PropertyAssignment)
    def properties(self):
        """
        An optional list of property value assignments for the policy definition.
        
        :rtype: dict of str, :class:`PropertyAssignment`
        """

    @field_validator(policy_targets_validator)
    @primitive_list_field(str)
    def targets(self):
        """
        An optional list of valid Node Templates or Groups the Policy can be applied to.
        
        :rtype: list of str
        """

    @cachedmethod
    def _get_type(self, context):
        return context.presentation.get_from_dict('service_template', 'policy_types', self.type)

    @cachedmethod
    def _get_property_values(self, context):
        return ReadOnlyDict(get_assigned_and_defined_property_values(context, self))

    @cachedmethod
    def _get_targets(self, context):
        node_templates, groups = get_policy_targets(context, self)
        return ReadOnlyList(node_templates), ReadOnlyList(groups)

    def _validate(self, context):
        super(PolicyTemplate, self)._validate(context)
        self._get_property_values(context)

@has_fields
@dsl_specification('3.8', 'tosca-simple-profile-1.0')
class TopologyTemplate(ExtensiblePresentation):
    """
    This section defines the topology template of a cloud application. The main ingredients of the topology template are node templates representing components of the application and relationship templates representing links between the components. These elements are defined in the nested node_templates section and the nested relationship_templates sections, respectively. Furthermore, a topology template allows for defining input parameters, output parameters as well as grouping of node templates.
    
    See the `TOSCA Simple Profile v1.0 cos01 specification <http://docs.oasis-open.org/tosca/TOSCA-Simple-Profile-YAML/v1.0/cos01/TOSCA-Simple-Profile-YAML-v1.0-cos01.html#DEFN_ENTITY_TOPOLOGY_TEMPLATE>`__
    """

    @object_field(Description)
    def description(self):
        """
        The optional description for the Topology Template.
        
        :rtype: :class:`Description`
        """

    @object_dict_field(ParameterDefinition)
    def inputs(self):
        """
        An optional list of input parameters (i.e., as parameter definitions) for the Topology Template.
        
        :rtype: dict of str, :class:`ParameterDefinition`
        """

    @object_dict_field(NodeTemplate)
    def node_templates(self):
        """
        An optional list of node template definitions for the Topology Template.
        
        :rtype: dict of str, :class:`NodeTemplate`
        """

    @object_dict_field(RelationshipTemplate)
    def relationship_templates(self):
        """
        An optional list of relationship templates for the Topology Template.
        
        :rtype: dict of str, :class:`RelationshipTemplate`
        """

    @object_dict_field(GroupTemplate)
    def groups(self):
        """
        An optional list of Group definitions whose members are node templates defined within this same Topology Template.
        
        :class:`GroupTemplate`
        """

    @object_dict_field(PolicyTemplate)
    def policies(self):
        """
        An optional list of Policy definitions for the Topology Template.
        
        :rtype: dict of str, :class:`PolicyTemplate`
        """

    @object_dict_field(ParameterDefinition)
    def outputs(self):
        """
        An optional list of output parameters (i.e., as parameter definitions) for the Topology Template.
        
        :rtype: dict of str, :class:`ParameterDefinition`
        """
    
    @object_field(SubstitutionMappings)
    def substitution_mappings(self):
        """
        An optional declaration that exports the topology template as an implementation of a Node type.

        This also includes the mappings between the external Node Types named capabilities and requirements to existing implementations of those capabilities and requirements on Node templates declared within the topology template.
        """

    @cachedmethod
    def _get_input_values(self, context):
        return ReadOnlyDict(get_parameter_values(context, self, 'inputs'))

    @cachedmethod
    def _get_output_values(self, context):
        return ReadOnlyDict(get_parameter_values(context, self, 'outputs'))

    def _validate(self, context):
        super(TopologyTemplate, self)._validate(context)
        self._get_input_values(context)
        self._get_output_values(context)

    def _dump(self, context):
        self._dump_content(context, (
            'description',
            'inputs',
            'node_templates',
            'relationship_templates',
            'groups',
            'policies',
            'outputs',
            'substitution_mappings'))

@has_fields
@dsl_specification('3.9', 'tosca-simple-profile-1.0')
class ServiceTemplate(ExtensiblePresentation):
    """
    See the `TOSCA Simple Profile v1.0 cos01 specification <http://docs.oasis-open.org/tosca/TOSCA-Simple-Profile-YAML/v1.0/cos01/TOSCA-Simple-Profile-YAML-v1.0-cos01.html#DEFN_ELEMENT_SERVICE_TEMPLATE>`__.
    """
    
    @primitive_field(str)
    @dsl_specification('3.9.3.1', 'tosca-simple-profile-1.0')
    def tosca_definitions_version(self):
        """
        Defines the version of the TOSCA Simple Profile specification the template (grammar) complies with. 
        
        See the `TOSCA Simple Profile v1.0 cos01 specification <http://docs.oasis-open.org/tosca/TOSCA-Simple-Profile-YAML/v1.0/cos01/TOSCA-Simple-Profile-YAML-v1.0-cos01.html#_Toc379455047>`__
        
        :rtype: str
        """

    @object_field(MetaData)
    def metadata(self):
        """
        Defines a section used to declare additional metadata information. Domain-specific TOSCA profile specifications may define keynames that are required for their implementations.
        
        See the `TOSCA Simple Profile v1.0 cos01 specification <http://docs.oasis-open.org/tosca/TOSCA-Simple-Profile-YAML/v1.0/cos01/TOSCA-Simple-Profile-YAML-v1.0-cos01.html#_Toc379455048>`__
        
        :rtype: :class:`MetaData`
        """

    @object_field(Description)
    @dsl_specification('3.9.3.6', 'tosca-simple-profile-1.0')
    def description(self):
        """
        Declares a description for this Service Template and its contents.
        
        :rtype: :class:`Description`
        """
    
    @primitive_field()
    @dsl_specification('3.9.3.7', 'tosca-simple-profile-1.0')
    def dsl_definitions(self):
        """
        Declares optional DSL-specific definitions and conventions. For example, in YAML, this allows defining reusable YAML macros (i.e., YAML alias anchors) for use throughout the TOSCA Service Template.

        See the `TOSCA Simple Profile v1.0 cos01 specification <http://docs.oasis-open.org/tosca/TOSCA-Simple-Profile-YAML/v1.0/cos01/TOSCA-Simple-Profile-YAML-v1.0-cos01.html#_Toc397688790>`__
        """
        
    @object_dict_field(Repository)
    @dsl_specification('3.9.3.8', 'tosca-simple-profile-1.0')
    def repositories(self):
        """
        Declares the list of external repositories which contain artifacts that are referenced in the service template along with their addresses and necessary credential information used to connect to them in order to retrieve the artifacts.
        
        :rtype: dict of str, :class:`Repository`
        """

    @object_list_field(Import)
    @dsl_specification('3.9.3.9', 'tosca-simple-profile-1.0')
    def imports(self):
        """
        Declares import statements external TOSCA Definitions documents. For example, these may be file location or URIs relative to the service template file within the same TOSCA CSAR file.
        
        :rtype: list of :class:`Import`
        """
        
    @object_dict_field(ArtifactType)
    @dsl_specification('3.9.3.10', 'tosca-simple-profile-1.0')
    def artifact_types(self):
        """
        This section contains an optional list of artifact type definitions for use in the service template.
        
        :rtype: dict of str, :class:`ArtifactType`
        """
        
    @object_dict_field(DataType)
    @dsl_specification('3.9.3.11', 'tosca-simple-profile-1.0')
    def data_types(self):
        """
        Declares a list of optional TOSCA Data Type definitions.
        
        :rtype: dict of str, :class:`DataType`
        """
        
    @object_dict_field(CapabilityType)
    @dsl_specification('3.9.3.12', 'tosca-simple-profile-1.0')
    def capability_types(self):
        """
        This section contains an optional list of capability type definitions for use in the service template.
        
        :rtype: dict of str, :class:`CapabilityType`
        """
        
    @object_dict_field(InterfaceType)
    @dsl_specification('3.9.3.13', 'tosca-simple-profile-1.0')
    def interface_types(self):
        """
        This section contains an optional list of interface type definitions for use in the service template.
        
        :rtype: dict of str, :class:`InterfaceType`
        """
        
    @object_dict_field(RelationshipType)
    @dsl_specification('3.9.3.14', 'tosca-simple-profile-1.0')
    def relationship_types(self):
        """
        This section contains a set of relationship type definitions for use in the service template.
        
        :rtype: dict of str, :class:`RelationshipType`
        """

    @object_dict_field(NodeType)
    @dsl_specification('3.9.3.15', 'tosca-simple-profile-1.0')
    def node_types(self):
        """
        This section contains a set of node type definitions for use in the service template.
        
        :rtype: dict of str, :class:`NodeType`
        """

    @object_dict_field(GroupType)
    @dsl_specification('3.9.3.16', 'tosca-simple-profile-1.0')
    def group_types(self):
        """
        This section contains a list of group type definitions for use in the service template.
        
        :rtype: dict of str, :class:`GroupType`
        """

    @object_dict_field(PolicyType)
    @dsl_specification('3.9.3.17', 'tosca-simple-profile-1.0')
    def policy_types(self):
        """
        This section contains a list of policy type definitions for use in the service template.
        
        :rtype: dict of str, :class:`PolicyType`
        """

    @object_field(TopologyTemplate)
    def topology_template(self):
        """
        Defines the topology template of an application or service, consisting of node templates that represent the application's or service's components, as well as relationship templates representing relations between the components.
        
        :rtype: :class:`TopologyTemplate`
        """

    def _dump(self, context):
        self._dump_content(context, (
            'description',
            'tosca_definitions_version',
            'metadata',
            'repositories',
            'imports',
            'artifact_types',
            'data_types',
            'capability_types',
            'interface_types',
            'relationship_types',
            'node_types',
            'group_types',
            'policy_types',
            'topology_template'))
