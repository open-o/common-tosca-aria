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

from __future__ import absolute_import # so we can import standard 'types'

from .elements import Element, Template, Parameter, Interface, Operation, Artifact, GroupPolicy
from .plan_elements import DeploymentPlan, Node, Capability, Relationship, Group, Policy, Mapping, Substitution
from .utils import instantiate_dict, dump_list_values, dump_dict_values, dump_properties, dump_interfaces
from .. import Issue
from ..utils import StrictList, StrictDict, puts
from types import FunctionType

class DeploymentTemplate(Template):
    def __init__(self):
        self.description = None
        self.metadata = None
        self.node_templates = StrictDict(key_class=basestring, value_class=NodeTemplate)
        self.group_templates = StrictDict(key_class=basestring, value_class=GroupTemplate)
        self.policy_templates = StrictDict(key_class=basestring, value_class=PolicyTemplate)
        self.substitution_template = None
        self.inputs = StrictDict(key_class=basestring, value_class=Parameter)
        self.outputs = StrictDict(key_class=basestring, value_class=Parameter)
        self.operations = StrictDict(key_class=basestring, value_class=Operation)

    def instantiate(self, context, container):
        r = DeploymentPlan()
        context.deployment.plan = r
        
        r.description = self.description
        
        if self.metadata is not None:
            r.metadata = self.metadata.instantiate(context, container)
        
        for node_template in self.node_templates.itervalues():
            for _ in range(node_template.default_instances):
                node = node_template.instantiate(context, container)
                r.nodes[node.id] = node

        instantiate_dict(context, self, r.groups, self.group_templates)
        instantiate_dict(context, self, r.policies, self.policy_templates)
        instantiate_dict(context, self, r.operations, self.operations)
        
        if self.substitution_template is not None:
            r.substitution = self.substitution_template.instantiate(context, container)

        instantiate_dict(context, self, r.inputs, self.inputs)
        instantiate_dict(context, self, r.outputs, self.outputs)
        
        for name, the_input in context.deployment.inputs.iteritems():
            if name not in r.inputs:
                context.validation.report('input "%s" is not supported' % name)
            else:
                r.inputs[name].value = the_input
        
        return r

    def validate(self, context):
        if self.metadata is not None:
            self.metadata.validate(context)
        for node_template in self.node_templates.itervalues():
            node_template.validate(context)
        for group_template in self.group_templates.itervalues():
            group_template.validate(context)
        for policy_template in self.policy_templates.itervalues():
            policy_template.validate(context)
        if self.substitution_template is not None:
            self.substitution_template.validate(context)
        for operation in self.operations.itervalues():
            operation.validate(context)

    def dump(self, context):
        if self.description is not None:
            puts('Description: %s' % context.style.meta(self.description))
        if self.metadata is not None:
            self.metadata.dump(context)
        for node_template in self.node_templates.itervalues():
            node_template.dump(context)
        for group_template in self.group_templates.itervalues():
            group_template.dump(context)
        for policy_template in self.policy_templates.itervalues():
            policy_template.dump(context)
        if self.substitution_template is not None:
            self.substitution_template.dump(context)
        dump_properties(context, self.inputs, 'Inputs')
        dump_properties(context, self.outputs, 'Outputs')
        dump_dict_values(context, self.operations, 'Operations')

class NodeTemplate(Template):
    def __init__(self, name, type_name):
        if not isinstance(name, basestring):
            raise ValueError('must set name (string)')
        if not isinstance(type_name, basestring):
            raise ValueError('must set type_name (string)')
        
        self.name = name
        self.type_name = type_name
        self.default_instances = 1
        self.min_instances = 0
        self.max_instances = None
        self.properties = StrictDict(key_class=basestring, value_class=Parameter)
        self.interfaces = StrictDict(key_class=basestring, value_class=Interface)
        self.artifacts = StrictDict(key_class=basestring, value_class=Artifact)
        self.capabilities = StrictDict(key_class=basestring, value_class=CapabilityTemplate)
        self.requirements = StrictList(value_class=Requirement)
        self.target_node_template_constraints = StrictList(value_class=FunctionType)
    
    def is_target_node_valid(self, target_node_template):
        if self.target_node_template_constraints:
            for node_type_constraint in self.target_node_template_constraints:
                if not node_type_constraint(target_node_template, self):
                    return False
        return True
    
    def instantiate(self, context, container):
        r = Node(context, self.type_name, self.name)
        instantiate_dict(context, r, r.properties, self.properties)
        instantiate_dict(context, r, r.interfaces, self.interfaces)
        instantiate_dict(context, r, r.artifacts, self.artifacts)
        instantiate_dict(context, r, r.capabilities, self.capabilities)
        r.coerce_values(context, r, False)
        return r
    
    def validate(self, context):
        if context.deployment.node_types.get_descendant(self.type_name) is None:
            context.validation.report('node template "%s" has an unknown type: %s' % (self.name, repr(self.type_name)), level=Issue.BETWEEN_TYPES)        
        for interface in self.interfaces.itervalues():
            interface.validate(context)
        for artifact in self.artifacts.itervalues():
            artifact.validate(context)
        for capability in self.capabilities.itervalues():
            capability.validate(context)
        for requirement in self.requirements:
            requirement.validate(context)
    
    def dump(self, context):
        puts('Node template: %s' % context.style.node(self.name))
        with context.style.indent:
            puts('Type: %s' % context.style.type(self.type_name))
            puts('Instances: %d (%d%s)' % (self.default_instances, self.min_instances, (' to %d' % self.max_instances) if self.max_instances is not None else ' or more'))
            dump_properties(context, self.properties)
            dump_interfaces(context, self.interfaces)
            dump_dict_values(context, self.artifacts, 'Artifacts')
            dump_dict_values(context, self.capabilities, 'Capabilities')
            dump_list_values(context, self.requirements, 'Requirements')

class Requirement(Element):
    def __init__(self, name=None, target_node_type_name=None, target_node_template_name=None, target_capability_type_name=None, target_capability_name=None):
        if name and not isinstance(name, basestring):
            raise ValueError('name must be a string)')
        if target_node_type_name and not isinstance(target_node_type_name, basestring):
            raise ValueError('target_node_type_name must be string')
        if target_node_template_name and not isinstance(target_node_template_name, basestring):
            raise ValueError('target_node_template_name must be string')
        if target_capability_type_name and not isinstance(target_capability_type_name, basestring):
            raise ValueError('target_capability_type_name must be string')
        if target_capability_name and not isinstance(target_capability_name, basestring):
            raise ValueError('target_capability_name must be string')
        if (target_node_type_name and target_node_template_name) or ((not target_node_type_name) and (not target_node_template_name)):
            raise ValueError('must set either target_node_type_name or target_node_template_name')
        if target_capability_type_name and target_capability_name:
            raise ValueError('can set either target_capability_type_name or target_capability_name')
        
        self.name = name
        self.target_node_type_name = target_node_type_name
        self.target_node_template_name = target_node_template_name
        self.target_node_template_constraints = StrictList(value_class=FunctionType)
        self.target_capability_type_name = target_capability_type_name
        self.target_capability_name = target_capability_name
        self.relationship_template = None # optional

    def find_target(self, context, source_node_template):
        # We might already have a specific node template, so we'll just verify it
        if self.target_node_template_name is not None:
            target_node_template = context.deployment.template.node_templates.get(self.target_node_template_name)
            
            if not source_node_template.is_target_node_valid(target_node_template):
                context.validation.report('requirement "%s" of node template "%s" is for node template "%s" but it does not match constraints' % (self.name, self.target_node_template_name, source_node_template.name), level=Issue.BETWEEN_TYPES)
                return None, None
            
            if (self.target_capability_type_name is not None) or (self.target_capability_name is not None): 
                target_node_capability = self.find_target_capability(context, source_node_template, target_node_template)
                if target_node_capability is None:
                    return None, None
            else:
                target_node_capability = None
            
            return target_node_template, target_node_capability

        # Find first node that matches the type
        elif self.target_node_type_name is not None:
            for target_node_template in context.deployment.template.node_templates.itervalues():
                if not context.deployment.node_types.is_descendant(self.target_node_type_name, target_node_template.type_name):
                    continue
                
                if not source_node_template.is_target_node_valid(target_node_template):
                    continue
    
                target_node_capability = self.find_target_capability(context, source_node_template, target_node_template)
                if target_node_capability is None:
                    continue
                
                return target_node_template, target_node_capability
        
        return None, None

    def find_target_capability(self, context, source_node_template, target_node_template):
        for capability in target_node_template.capabilities.itervalues():
            if capability.satisfies_requirement(context, source_node_template, self, target_node_template):
                return capability
        return None

    def validate(self, context):
        if (self.target_node_type_name) and (context.deployment.node_types.get_descendant(self.target_node_type_name) is None):
            context.validation.report('requirement "%s" refers to an unknown node type: %s' % (self.name, repr(self.target_node_type_name)), level=Issue.BETWEEN_TYPES)        
        if (self.target_capability_type_name) and (context.deployment.capability_types.get_descendant(self.target_capability_type_name) is None):
            context.validation.report('requirement "%s" refers to an unknown capability type: %s' % (self.name, repr(self.target_capability_type_name)), level=Issue.BETWEEN_TYPES)        
        if self.relationship_template:
            self.relationship_template.validate(context)

    def dump(self, context):
        if self.name:
            puts(context.style.node(self.name))
        else:
            puts('Requirement:')
        with context.style.indent:
            if self.target_node_type_name is not None:
                puts('Target node type: %s' % context.style.type(self.target_node_type_name))
            elif self.target_node_template_name is not None:
                puts('Target node template: %s' % context.style.node(self.target_node_template_name))
            if self.target_capability_type_name is not None:
                puts('Target capability type: %s' % context.style.type(self.target_capability_type_name))
            elif self.target_capability_name is not None:
                puts('Target capability name: %s' % context.style.node(self.target_capability_name))
            if self.target_node_template_constraints:
                puts('Target node template constraints:')
                with context.style.indent:
                    for c in self.target_node_template_constraints:
                        puts(context.style.literal(c))
            if self.relationship_template:
                self.relationship_template.dump(context)

class CapabilityTemplate(Template):
    def __init__(self, name, type_name):
        if not isinstance(name, basestring):
            raise ValueError('name must be string')
        if not isinstance(type_name, basestring):
            raise ValueError('type_name must be string')
        
        self.name = name
        self.type_name = type_name
        self.min_occurrences = None # optional
        self.max_occurrences = None # optional
        self.valid_source_node_type_names = None
        self.properties = StrictDict(key_class=basestring, value_class=Parameter)
        
    def satisfies_requirement(self, context, source_node_template, requirement, target_node_template):
        # Do we match the required capability type?
        if not context.deployment.capability_types.is_descendant(requirement.target_capability_type_name, self.type_name):
            return False
        
        # Are we in valid_source_node_type_names?
        if self.valid_source_node_type_names:
            for valid_source_node_type_name in self.valid_source_node_type_names:
                if not context.deployment.node_types.is_descendant(valid_source_node_type_name, source_node_template.type_name):
                    return False
        
        # Apply requirement constraints
        if requirement.target_node_template_constraints:
            for node_type_constraint in requirement.target_node_template_constraints:
                if not node_type_constraint(target_node_template, source_node_template):
                    return False
        
        return True

    def instantiate(self, context, container):
        r = Capability(self.name, self.type_name)
        r.min_occurrences = self.min_occurrences
        r.max_occurrences = self.max_occurrences
        instantiate_dict(context, container, r.properties, self.properties)
        return r

    def validate(self, context):
        if context.deployment.capability_types.get_descendant(self.type_name) is None:
            context.validation.report('capability "%s" refers to an unknown type: %s' % (self.name, repr(self.type)), level=Issue.BETWEEN_TYPES)        

    def dump(self, context):
        puts(context.style.node(self.name))
        with context.style.indent:
            puts('Type: %s' % context.style.type(self.type_name))
            puts('Occurrences: %d%s' % (self.min_occurrences or 0, (' to %d' % self.max_occurrences) if self.max_occurrences is not None else ' or more'))
            if self.valid_source_node_type_names:
                puts('Valid source node types: %s' % ', '.join((str(context.style.type(v)) for v in self.valid_source_node_type_names)))
            dump_properties(context, self.properties)

class RelationshipTemplate(Template):
    def __init__(self, type_name=None, template_name=None):
        if type_name and not isinstance(type_name, basestring):
            raise ValueError('type_name must be string')
        if template_name and not isinstance(template_name, basestring):
            raise ValueError('template_name must be string')
        if (type_name and template_name) or ((not type_name) and (not template_name)):
            raise ValueError('must set either type_name or template_name')
        
        self.type_name = type_name
        self.template_name = template_name
        self.properties = StrictDict(key_class=basestring, value_class=Parameter)
        self.source_interfaces = StrictDict(key_class=basestring, value_class=Interface)
        self.target_interfaces = StrictDict(key_class=basestring, value_class=Interface)

    def instantiate(self, context, container):
        r = Relationship(self.type_name, self.template_name)
        instantiate_dict(context, container, r.properties, self.properties)
        instantiate_dict(context, container, r.source_interfaces, self.source_interfaces)
        instantiate_dict(context, container, r.target_interfaces, self.target_interfaces)
        return r

    def validate(self, context):
        for interface in self.source_interfaces.itervalues():
            interface.validate(context)
        for interface in self.target_interfaces.itervalues():
            interface.validate(context)

    def dump(self, context):
        if self.type_name is not None:
            puts('Relationship type: %s' % context.style.type(self.type_name))
        else:
            puts('Relationship template: %s' % context.style.node(self.template_name))
        with context.style.indent:
            dump_properties(context, self.properties)
            dump_interfaces(context, self.source_interfaces, 'Source interfaces')
            dump_interfaces(context, self.target_interfaces, 'Target interfaces')

class GroupTemplate(Template):
    def __init__(self, name, type_name=None):
        if not isinstance(name, basestring):
            raise ValueError('must set name (string)')
        if type_name and not isinstance(type_name, basestring):
            raise ValueError('type_name must be string')
        
        self.name = name
        self.type_name = type_name
        self.properties = StrictDict(key_class=basestring, value_class=Parameter)
        self.interfaces = StrictDict(key_class=basestring, value_class=Interface)
        self.policies = StrictDict(key_class=basestring, value_class=GroupPolicy)
        self.member_node_template_names = StrictList(value_class=basestring)

    def instantiate(self, context, container):
        r = Group(context, self.type_name, self.name)
        instantiate_dict(context, self, r.properties, self.properties)
        instantiate_dict(context, self, r.interfaces, self.interfaces)
        instantiate_dict(context, self, r.policies, self.policies)
        for member_node_template_name in self.member_node_template_names:
            r.member_node_ids.extend(context.deployment.plan.get_node_ids(member_node_template_name))
        return r

    def dump(self, context):
        puts('Group template: %s' % context.style.node(self.name))
        with context.style.indent:
            if self.type_name:
                puts('Type: %s' % context.style.type(self.type_name))
            dump_properties(context, self.properties)
            dump_interfaces(context, self.interfaces)
            dump_dict_values(context, self.policies, 'Policies')
            if self.member_node_template_names:
                puts('Member node templates: %s' % ', '.join((str(context.style.node(v)) for v in self.member_node_template_names)))

class PolicyTemplate(Template):
    def __init__(self, name, type_name):
        if not isinstance(name, basestring):
            raise ValueError('must set name (string)')
        if not isinstance(type_name, basestring):
            raise ValueError('must set type_name (string)')
        
        self.name = name
        self.type_name = type_name
        self.properties = StrictDict(key_class=basestring, value_class=Parameter)
        self.target_node_template_names = StrictList(value_class=basestring)
        self.target_group_template_names = StrictList(value_class=basestring)

    def instantiate(self, context, container):
        r = Policy(self.name, self.type_name)
        instantiate_dict(context, self, r.properties, self.properties)
        for node_template_name in self.target_node_template_names:
            r.target_node_ids.extend(context.deployment.plan.get_node_ids(node_template_name))
        for group_template_name in self.target_group_template_names:
            r.target_group_ids.extend(context.deployment.plan.get_group_ids(group_template_name))
        return r

    def dump(self, context):
        puts('Policy template: %s' % context.style.node(self.name))
        with context.style.indent:
            puts('Type: %s' % context.style.type(self.type_name))
            dump_properties(context, self.properties)
            if self.target_node_template_names:
                puts('Target node templates: %s' % ', '.join((str(context.style.node(v)) for v in self.target_node_template_names)))
            if self.target_group_template_names:
                puts('Target group templates: %s' % ', '.join((str(context.style.node(v)) for v in self.target_group_template_names)))

class MappingTemplate(Template):
    def __init__(self, mapped_name, node_template_name, name):
        if not isinstance(mapped_name, basestring):
            raise ValueError('must set mapped_name (string)')
        if not isinstance(node_template_name, basestring):
            raise ValueError('must set node_template_name (string)')
        if not isinstance(name, basestring):
            raise ValueError('must set name (string)')

        self.mapped_name = mapped_name
        self.node_template_name = node_template_name
        self.name = name

    def validate(self, context):
        if self.node_template_name not in context.deployment.template.node_templates:
            context.validation.report('mapping "%s" refers to an unknown node template: %s' % (self.mapped_name, repr(self.node_template_name)), level=Issue.BETWEEN_TYPES)        

    def instantiate(self, context, container):
        nodes = context.deployment.plan.find_nodes(self.node_template_name)
        if len(nodes) == 0:
            context.validation.report('mapping "%s" refer to node template "%s" but there are no node instances' % (self.mapped_name, self.node_template_name), level=Issue.BETWEEN_INSTANCES)
            return None        
        return Mapping(self.mapped_name, nodes[0].id, self.name)

    def dump(self, context):
        puts('%s -> %s.%s' % (context.style.node(self.mapped_name), context.style.node(self.node_template_name), context.style.node(self.name)))

class SubstitutionTemplate(Template):
    def __init__(self, node_type_name):
        if not isinstance(node_type_name, basestring):
            raise ValueError('must set node_type_name (string)')
    
        self.node_type_name = node_type_name
        self.capabilities = StrictDict(key_class=basestring, value_class=MappingTemplate)
        self.requirements = StrictDict(key_class=basestring, value_class=MappingTemplate)

    def instantiate(self, context, container):
        r = Substitution(self.node_type_name)
        instantiate_dict(context, container, r.capabilities, self.capabilities)
        instantiate_dict(context, container, r.requirements, self.requirements)
        return r

    def validate(self, context):
        for capability in self.capabilities.itervalues():
            capability.validate(context)
        for requirement in self.requirements.itervalues():
            requirement.validate(context)

    def dump(self, context):
        puts('Substitution:')
        with context.style.indent:
            puts('Node type: %s' % context.style.type(self.node_type_name))
            dump_dict_values(context, self.capabilities, 'Capability mappings')
            dump_dict_values(context, self.requirements, 'Requirement mappings')
