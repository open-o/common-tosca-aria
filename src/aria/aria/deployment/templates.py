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

from .elements import Element, Template, Interface, Artifact
from .utils import instantiate_properties, instantiate_interfaces, dump_list_values, dump_dict_values, dump_properties, dump_interfaces
from .plan import DeploymentPlan, Node, Capability, Relationship, Group, Policy
from .. import Issue
from ..utils import StrictList, StrictDict
from clint.textui import puts
from types import FunctionType

class DeploymentTemplate(Template):
    def __init__(self):
        self.node_templates = StrictDict(str, NodeTemplate)
        self.group_templates = StrictDict(str, GroupTemplate)
        self.policy_templates = StrictDict(str, PolicyTemplate)
        self.inputs = StrictDict(str)
        self.outputs = StrictDict(str)

    def instantiate(self, context, container):
        r = DeploymentPlan()
        context.deployment.plan = r
        for node_template in self.node_templates.itervalues():
            node = node_template.instantiate(context, container)
            r.nodes[node.id] = node
        for group_template in self.group_templates.itervalues():
            group = group_template.instantiate(context, container)
            r.groups[group.id] = group
        for policy_template in self.policy_templates.itervalues():
            policy = policy_template.instantiate(context, container)
            r.policies[policy.name] = policy
        instantiate_properties(context, self, r.inputs, self.inputs)
        instantiate_properties(context, self, r.outputs, self.outputs)
        return r

    def validate(self, context):
        for node_template in self.node_templates.itervalues():
            node_template.validate(context)
        for group_template in self.group_templates.itervalues():
            group_template.validate(context)
        for policy_template in self.policy_templates.itervalues():
            policy_template.validate(context)

    def dump(self, context):
        for node_template in self.node_templates.itervalues():
            node_template.dump(context)
        for group_template in self.group_templates.itervalues():
            group_template.dump(context)
        for policy_template in self.policy_templates.itervalues():
            policy_template.dump(context)
        dump_properties(context, self.inputs, 'Inputs')
        dump_properties(context, self.outputs, 'Outputs')

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
        self.properties = StrictDict(str)
        self.interfaces = StrictDict(str, Interface)
        self.artifacts = StrictDict(str, Artifact)
        self.capabilities = StrictDict(str, CapabilityTemplate)
        self.requirements = StrictList(Requirement)
        self.target_node_type_constraints = StrictList(FunctionType)
    
    def is_target_node_valid(self, target_node_template):
        if self.target_node_type_constraints:
            for node_type_constraint in self.target_node_type_constraints:
                if not node_type_constraint(target_node_template, self):
                    return False
        return True
    
    def instantiate(self, context, container):
        r = Node(self.name)
        instantiate_properties(context, r, r.properties, self.properties)
        instantiate_interfaces(context, r, r.interfaces, self.interfaces)
        for artifact_name, artifact in self.artifacts.iteritems():
            r.artifacts[artifact_name] = artifact.instantiate(context, r)
        for capability_name, capability in self.capabilities.iteritems():
            r.capabilities[capability_name] = capability.instantiate(context, r)
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
        self.target_node_type_constraints = StrictList(FunctionType)
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
        self.properties = StrictDict(str)
        
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
        if requirement.target_node_type_constraints:
            for node_type_constraint in requirement.target_node_type_constraints:
                if not node_type_constraint(target_node_template, source_node_template):
                    return False
        
        return True

    def instantiate(self, context, container):
        r = Capability(self.name, self.type_name)
        r.min_occurrences = self.min_occurrences
        r.max_occurrences = self.max_occurrences
        instantiate_properties(context, container, r.properties, self.properties)
        return r

    def validate(self, context):
        if context.deployment.capability_types.get_descendant(self.type_name) is None:
            context.validation.report('capability "%s" has an unknown type: %s' % (self.name, repr(self.type)), level=Issue.BETWEEN_TYPES)        

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
        self.properties = StrictDict(str)
        self.interfaces = StrictDict(str, Interface)

    def instantiate(self, context, container):
        r = Relationship(self.type_name, self.template_name)
        instantiate_properties(context, container, r.properties, self.properties)
        instantiate_interfaces(context, container, r.interfaces, self.interfaces)
        return r

    def validate(self, context):
        for interface in self.interfaces.itervalues():
            interface.validate(context)

    def dump(self, context):
        if self.type_name is not None:
            puts('Relationship type: %s' % context.style.type(self.type_name))
        else:
            puts('Relationship template: %s' % context.style.node(self.template_name))
        with context.style.indent:
            dump_properties(context, self.properties)
            dump_interfaces(context, self.interfaces)

class GroupTemplate(Template):
    def __init__(self, name, type_name):
        if not isinstance(name, basestring):
            raise ValueError('must set name (string)')
        if not isinstance(type_name, basestring):
            raise ValueError('must set type_name (string)')
        
        self.name = name
        self.type_name = type_name
        self.properties = StrictDict(str)
        self.interfaces = StrictDict(str, Interface)
        self.member_node_template_names = StrictList(str)

    def instantiate(self, context, container):
        r = Group(self.name)
        instantiate_properties(context, self, r.properties, self.properties)
        instantiate_interfaces(context, self, r.interfaces, self.interfaces)
        for member_node_template_name in self.member_node_template_names:
            for node in context.deployment.plan.nodes.itervalues():
                if node.template_name == member_node_template_name:
                    r.member_node_ids.append(node.id)
        return r

    def dump(self, context):
        puts('Group template: %s' % context.style.node(self.name))
        with context.style.indent:
            puts('Type: %s' % context.style.type(self.type_name))
            dump_properties(context, self.properties)
            dump_interfaces(context, self.interfaces)
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
        self.properties = StrictDict(str)
        self.target_node_template_names = StrictList(str)
        self.target_group_template_names = StrictList(str)

    def instantiate(self, context, container):
        r = Policy(self.name, self.type_name)
        instantiate_properties(context, self, r.properties, self.properties)
        for node_template_name in self.target_node_template_names:
            for node in context.deployment.plan.find_nodes(node_template_name):
                if node not in r.target_node_ids:
                    r.target_node_ids.append(node.id)
        for group_template_name in self.target_group_template_names:
            for group in context.deployment.plan.find_groups(group_template_name):
                if group not in r.target_group_ids:
                    r.target_group_ids.append(group.id)
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
