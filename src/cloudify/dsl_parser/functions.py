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

from aria_extension_cloudify.v1_0.functions import get_function
from aria.consumption import ConsumptionContext
from aria.presentation import FakePresentation

class ClassicContext(object):
    def __init__(self, context, get_node_instances_method, get_node_instance_method, get_node_method):
        self.self_node_id = context.get('self')
        self.source_node_id = context.get('source')
        self.target_node_id = context.get('target')
        self.get_nodes = get_node_instances_method
        self.get_node = get_node_instance_method
        self.get_node_template = get_node_method

def evaluate_outputs(outputs_def, get_node_instances_method, get_node_instance_method, get_node_method):
    """
    Evaluates an outputs definition containing intrinsic functions.

    :param outputs_def: Outputs definition.
    :param get_node_instances_method: A method for getting node instances.
    :param get_node_instance_method: A method for getting a node instance.
    :param get_node_method: A method for getting a node.
    :return: Outputs dict.
    """
    print '!!! evaluate_outputs'

def evaluate_functions(payload, context, get_node_instances_method, get_node_instance_method, get_node_method):
    """
    Evaluate functions in payload.

    :param payload: The payload to evaluate.
    :param context: Context used during evaluation.
    :param get_node_instances_method: A method for getting node instances.
    :param get_node_instance_method: A method for getting a node instance.
    :param get_node_method: A method for getting a node.
    :return: payload.
    """
    
    #print '!!! evaluate_function', payload, context    
    
    classic_context = ClassicContext(context, get_node_instances_method, get_node_instance_method, get_node_method)
    consumption_context = ConsumptionContext()
    presentation = FakePresentation()
    
    r = {}
    if payload:
        for name, value in payload.iteritems():
            value = value['default']
            is_function, fn = get_function(consumption_context, presentation, value)
            if consumption_context.validation.dump_issues():
                break
            if is_function:
                r[name] = fn._evaluate_classic(classic_context)
            else:
                r[name] = value
            # TODO: coerce to value['type']?
    
    return r    
