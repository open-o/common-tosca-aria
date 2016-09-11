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

from aria import Issue, InvalidValueError, dsl_specification
from aria.deployment import Function, CannotEvaluateFunction
from aria.presentation import FakePresentation
from aria.utils import deepcopy_with_locators

@dsl_specification('intrinsic-functions-2', 'cloudify-1.0')
@dsl_specification('intrinsic-functions-2', 'cloudify-1.1')
@dsl_specification('intrinsic-functions-2', 'cloudify-1.2')
@dsl_specification('intrinsic-functions-2', 'cloudify-1.3')
class GetInput(Function):
    """
    :code:`get_input` is used for referencing :code:`inputs` described in the inputs section of the blueprint. :code:`get_input` can be used in node properties, outputs, and node/relationship operation inputs. The function is evaluated on deployment creation.
    
    See the `Cloudify DSL v1.3 specification <http://docs.getcloudify.org/3.4.0/blueprints/spec-intrinsic-functions/>`__.
    """

    def __init__(self, context, presentation, argument):
        self.locator = presentation._locator

        self.input_property_name = parse_string_expression(context, presentation, 'get_input', None, 'the input property name', argument)

        if context.presentation.presenter is not None:
            if isinstance(self.input_property_name, basestring):
                inputs = context.presentation.presenter.inputs
                if (inputs is None) or (self.input_property_name not in inputs):
                    raise InvalidValueError('function "get_input" argument is not a valid input name: %s' % repr(argument), locator=self.locator)
        
        self.context = context

    @property
    def as_raw(self):
        input_property_name = self.input_property_name
        if hasattr(input_property_name, 'as_raw'):
            input_property_name = input_property_name.as_raw
        return {'get_input': input_property_name}
    
    def _evaluate(self, context, container):
        if not hasattr(self.context.deployment, 'classic_plan'):
            raise CannotEvaluateFunction()
        inputs = self.context.deployment.classic_plan['inputs']
        if self.input_property_name not in inputs:
            raise CannotEvaluateFunction()
        return inputs[self.input_property_name]

    def _evaluate_classic(self, classic_context):
        inputs = self.context.deployment.classic_plan['inputs']
        if self.input_property_name not in inputs:
            raise InvalidValueError('input does not exist for function "get_input": %s' % repr(self.input_property_name), locator=self.locator)
        return deepcopy_with_locators(inputs[self.input_property_name])

@dsl_specification('intrinsic-functions-3', 'cloudify-1.0')
@dsl_specification('intrinsic-functions-3', 'cloudify-1.1')
@dsl_specification('intrinsic-functions-3', 'cloudify-1.2')
@dsl_specification('intrinsic-functions-3', 'cloudify-1.3')
class GetProperty(Function):
    """
    :code:`get_property` is used for referencing node properties within the blueprint. :code:`get_property` can be used in node properties, outputs, and node/relationship operation inputs. The function is evaluated on deployment creation.
    
    See the `Cloudify DSL v1.3 specification <http://docs.getcloudify.org/3.4.0/blueprints/spec-intrinsic-functions/>`__.
    """

    def __init__(self, context, presentation, argument):
        self.locator = presentation._locator
        
        if (not isinstance(argument, list)) or (len(argument) < 2):
            raise InvalidValueError('function "get_property" argument must be a list of at least 2 string expressions: %s' % repr(argument), locator=self.locator)

        self.modelable_entity_name = parse_modelable_entity_name(context, presentation, 'get_property', 0, argument[0])
        self.nested_property_name_or_index = argument[1:] # the first of these will be tried as a req-or-cap name

    @property
    def as_raw(self):
        return {'get_property': [self.modelable_entity_name] + self.nested_property_name_or_index}

    def _evaluate(self, context, container):
        raise CannotEvaluateFunction()

    def _evaluate_classic(self, classic_context):
        _, node_template = get_classic_node(classic_context, self.modelable_entity_name, 'get_property')
        return get_classic_property(node_template['properties'], self.nested_property_name_or_index, 'get_property')

@dsl_specification('intrinsic-functions-4', 'cloudify-1.0')
@dsl_specification('intrinsic-functions-4', 'cloudify-1.1')
@dsl_specification('intrinsic-functions-4', 'cloudify-1.2')
@dsl_specification('intrinsic-functions-4', 'cloudify-1.3')
class GetAttribute(Function):
    """
    :code:`get_attribute` is used to reference runtime-properties of different node-instances from within the blueprint.
    
    See the `Cloudify DSL v1.3 specification <http://docs.getcloudify.org/3.4.0/blueprints/spec-intrinsic-functions/>`__.
    """

    def __init__(self, context, presentation, argument):
        self.locator = presentation._locator
        
        if (not isinstance(argument, list)) or (len(argument) < 2):
            raise InvalidValueError('function "get_attribute" argument must be a list of at least 2 string expressions: %s' % repr(argument), locator=self.locator)

        self.modelable_entity_name = parse_modelable_entity_name(context, presentation, 'get_attribute', 0, argument[0])
        self.nested_property_name_or_index = argument[1:] # the first of these will be tried as a req-or-cap name

    @property
    def as_raw(self):
        return {'get_attribute': [self.modelable_entity_name] + self.nested_property_name_or_index}

    def _evaluate(self, context, container):
        raise CannotEvaluateFunction()

    def _evaluate_classic(self, classic_context):
        node, node_template = get_classic_node(classic_context, self.modelable_entity_name, 'get_attribute')

        try:
            return get_classic_property(node['runtime_properties'], self.nested_property_name_or_index, 'get_attribute')
        except InvalidValueError:
            return get_classic_property(node_template['properties'], self.nested_property_name_or_index, 'get_attribute')

#
# Utils
#

def get_function(context, presentation, value):
    functions = context.presentation.presenter.functions
    if isinstance(value, dict) and (len(value) == 1):
        key = value.keys()[0]
        if key in functions:
            try:
                return True, functions[key](context, presentation, value[key])
            except InvalidValueError as e:
                context.validation.report(issue=e.issue)
                return True, None
    return False, None

def parse_string_expression(context, presentation, name, index, explanation, value):
    is_function, fn = get_function(context, presentation, value)
    if is_function:
        return fn
    else:
        value = str(value)
    return value

def parse_modelable_entity_name(context, presentation, name, index, value):
    value = parse_string_expression(context, presentation, name, index, 'the modelable entity name', value)
    if value == 'SELF':
        the_self, _ = parse_self(presentation)
        if the_self is None:
            raise invalid_modelable_entity_name(name, index, value, presentation._locator, 'a node template or a relationship template')
    elif value == 'HOST':
        _, self_variant = parse_self(presentation)
        if self_variant not in ('node_template', 'fake'):
            raise invalid_modelable_entity_name(name, index, value, presentation._locator, 'a node template')
    elif (value == 'SOURCE') or (value == 'TARGET'):
        _, self_variant = parse_self(presentation)
        if self_variant not in ('relationship_template', 'fake'):
            raise invalid_modelable_entity_name(name, index, value, presentation._locator, 'a relationship template')
    elif isinstance(value, basestring):
        if context.presentation.presenter is not None:
            node_templates = context.presentation.presenter.node_templates or {}
            relationship_templates = context.presentation.presenter.relationship_templates or {}
            if (value not in node_templates) and (value not in relationship_templates):
                raise InvalidValueError('function "%s" parameter %d is not a valid modelable entity name: %s' % (name, index + 1, repr(value)), locator=presentation._locator, level=Issue.BETWEEN_TYPES)
    return value

def parse_self(presentation):
    from .templates import NodeTemplate, RelationshipTemplate
    from .types import NodeType, RelationshipType
    
    if presentation is None:
        return None, None    
    elif isinstance(presentation, NodeTemplate) or isinstance(presentation, NodeType):
        return presentation, 'node_template'
    elif isinstance(presentation, RelationshipTemplate) or isinstance(presentation, RelationshipType):
        return presentation, 'relationship_template'
    elif isinstance(presentation, FakePresentation):
        return presentation, 'fake'
    else:
        return parse_self(presentation._container)

def invalid_modelable_entity_name(name, index, value, locator, contexts):
    return InvalidValueError('function "%s" parameter %d can be "%s" only in %s' % (name, index + 1, value, contexts), locator=locator, level=Issue.FIELD)

def get_classic_node(classic_context, modelable_entity_name, function_name):
    node = None
    
    def get_node(node_id):
        try:
            return classic_context.get_node(node_id)
        except Exception as e:
            raise InvalidValueError('function "%s" refers to an unknown node: %s' % (function_name, repr(node_id)), cause=e)

    if modelable_entity_name == 'SELF':
        node = get_node(classic_context.self_node_id)
    elif modelable_entity_name == 'SOURCE':
        node = get_node(classic_context.source_node_id)
    elif modelable_entity_name == 'TARGET':
        node = get_node(classic_context.target_node_id)
    else:
        try:
            nodes = classic_context.get_nodes(modelable_entity_name)
            node = nodes[0]
        except Exception as e:
            raise InvalidValueError('function "%s" refers to an unknown modelable entity: %s' % (function_name, repr(modelable_entity_name)), cause=e)
    
    node_template = classic_context.get_node_template(node['name'])
    
    return node, node_template

def get_classic_property(value, nested_property_name_or_index, function_name):
    for name_or_index in nested_property_name_or_index:
        try:
            value = value[name_or_index]
        except KeyError as e:
            raise InvalidValueError('function "%s" refers to an unknown nested property name: %s' % (function_name, repr(name_or_index)), cause=e)
        except IndexError as e:
            raise InvalidValueError('function "%s" refers to an unknown nested index: %s' % (function_name, repr(name_or_index)), cause=e)
    return value
