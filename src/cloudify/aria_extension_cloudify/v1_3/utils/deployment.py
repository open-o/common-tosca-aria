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

from aria.deployment import DeploymentTemplate, Type, NodeTemplate, RelationshipTemplate, GroupTemplate, PolicyTemplate, Interface, Operation, Requirement

def get_deployment_template(context, presenter):
    r = DeploymentTemplate()

    normalize_types(context, context.deployment.node_types, presenter.node_types)

    normalize_property_values(r.inputs, presenter.service_template._get_input_values(context))
    normalize_property_values(r.outputs, presenter.service_template._get_output_values(context))

    node_templates = presenter.node_templates
    if node_templates:
        for node_template_name, node_template in node_templates.iteritems():
            r.node_templates[node_template_name] = normalize_node_template(context, node_template)

    groups = presenter.groups
    if groups:
        for group_name, group in groups.iteritems():
            r.group_templates[group_name] = normalize_group(context, group)

    policies = presenter.policies
    if policies:
        for policy_name, policy in policies.iteritems():
            r.policy_templates[policy_name] = normalize_policy(context, policy)

    return r

def normalize_types(context, root, types):
    if types is None:
        return
    
    def added_all():
        for name in types:
            if root.get_descendant(name) is None:
                return False
        return True

    while not added_all():    
        for name, the_type in types.iteritems():
            if root.get_descendant(name) is None:
                parent_type = the_type._get_parent(context)
                if parent_type is None:
                    root.children.append(Type(the_type._name))
                else:
                    container = root.get_descendant(parent_type._name)
                    if container is not None:
                        container.children.append(Type(the_type._name))

def normalize_node_template(context, node_template):
    the_type = node_template._get_type(context)
    r = NodeTemplate(name=node_template._name, type_name=the_type._name)
    
    normalize_property_values(r.properties, node_template._get_property_values(context))
    normalize_interfaces(context, r.interfaces, node_template._get_interfaces(context))
    
    relationships = node_template.relationships
    if relationships:
        for relationship in relationships:
            r.requirements.append(normalize_requirement(context, relationship))

    scalable = node_template._get_scalable(context)
    if scalable is not None:
        node_template.default_instances = scalable.default_instances
        node_template.min_instances = scalable.min_instances
        if scalable.max_instances != -1:
            node_template.max_instances = scalable.max_instances

    return r

def normalize_interface(context, interface):
    r = Interface(name=interface._name)

    operations = interface.operations
    if operations:
        for operation_name, operation in operations.iteritems():
            #if operation.implementation is not None:
            r.operations[operation_name] = normalize_operation(context, operation)
    
    return r #if r.operations else None

def normalize_operation(context, operation):
    r = Operation(name=operation._name)

    implementation = operation.implementation
    if implementation is not None:
        r.implementation = implementation
    executor = operation.executor
    if executor is not None:
        r.executor = executor
    max_retries = operation.max_retries
    if max_retries is not None:
        r.max_retries = max_retries
    retry_interval = operation.retry_interval
    if retry_interval is not None:
        r.retry_interval = retry_interval

    inputs = operation.inputs
    if inputs:
        for input_name, the_input in inputs.iteritems():
            r.inputs[input_name] = the_input.value
    
    return r

def normalize_requirement(context, relationship):
    r = {'name': relationship._name}
    r['target_node_template_name'] = relationship.target
    r = Requirement(**r)
    r.relationship_template = normalize_relationship(context, relationship)
    return r

def normalize_relationship(context, relationship):
    relationship_type = relationship._get_type(context)
    r = RelationshipTemplate(template_name=relationship_type._name)

    normalize_property_values(r.properties, relationship._get_property_values(context))
    normalize_interfaces(context, r.interfaces, relationship._get_target_interfaces(context))
    
    return r

def normalize_group(context, group):
    group_type = group._get_type(context)
    r = GroupTemplate(name=group._name, type_name=group_type._name)

    normalize_property_values(r.properties, group._get_property_values(context))
    normalize_interfaces(context, r.interfaces, group._get_interfaces(context))
    
    members = group.members
    if members:
        for member in members:
            r.member_node_template_names.append(member)
    
    return r

def normalize_policy(context, policy):
    policy_type = policy._get_type(context)
    r = PolicyTemplate(name=policy._name, type_name=policy_type._name)

    normalize_property_values(r.properties, policy._get_property_values(context))
    
    node_templates, groups = policy._get_targets(context)
    for node_template in node_templates:
        r.target_node_template_names.append(node_template._name)
    for group in groups:
        r.target_group_template_names.append(group._name)
    
    return r

#
# Utils
#

def normalize_property_values(properties, source_properties):
    if source_properties:
        for property_name, prop in source_properties.iteritems():
            properties[property_name] = prop

def normalize_properties(properties, source_properties):
    if source_properties:
        for property_name, prop in source_properties.iteritems():
            properties[property_name] = prop.value

def normalize_interfaces(context, interfaces, source_interfaces):
    if source_interfaces:
        for interface_name, interface in source_interfaces.iteritems():
            interface = normalize_interface(context, interface)
            if interface is not None:
                interfaces[interface_name] = interface
