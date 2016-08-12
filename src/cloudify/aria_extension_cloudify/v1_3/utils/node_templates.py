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

from aria import Issue

class Scalable(object):
    """
    The :code:`capabilities.scalable.properties` key is used for configuring the deployment characteristics of the node template.
    """
    
    def __init__(self):
        self.default_instances = 1
        self.min_instances = 0
        self.max_instances = -1
        
    def validate(self, context, presentation, locator):
        def report(name, value, exception):
            context.validation.report('"%s" property in "scalable" capability in node template "%s" is not a valid integer: %s' % (name, presentation._fullname, repr(value)), locator=locator, level=Issue.FIELD, exception=e)

        try:
            self.min_instances = int(self.min_instances)
            if self.min_instances < 0:
                context.validation.report('"min_instances" property in "scalable" capability in node template "%s" is less than 0: %s' % (presentation._fullname, repr(self.min_instances)), locator=locator, level=Issue.FIELD)
        except ValueError as e:
            report('min_instances', self.min_instances, e)
            self.min_instances = 0
        
        if self.max_instances == 'UNBOUNDED':
            self.max_instances = -1
        try:
            self.max_instances = int(self.max_instances)
            if self.max_instances < -1:
                context.validation.report('"max_instances" property in "scalable" capability in node template "%s" is less than -1: %s' % (presentation._fullname, repr(self.max_instances)), locator=locator, level=Issue.FIELD)
            elif (self.max_instances != -1) and (self.max_instances < self.min_instances):
                context.validation.report('"max_instances" property in "scalable" capability in node template "%s" is less than "min_instances": %s' % (presentation._fullname, repr(self.max_instances)), locator=locator, level=Issue.BETWEEN_FIELDS)
        except ValueError as e:
            report('max_instances', self.max_instances, e)
            self.max_instances = -1
        
        try:
            self.default_instances = int(self.default_instances)
            if self.max_instances == -1:
                if self.default_instances < self.min_instances:
                    context.validation.report('"default_instances" property in "scalable" capability in node template "%s" is less than "min_instances": %s' % (presentation._fullname, repr(self.default_instances)), locator=locator, level=Issue.BETWEEN_FIELDS)
            elif (self.default_instances < self.min_instances) or (self.default_instances > self.max_instances):
                context.validation.report('"default_instances" property in "scalable" capability in node template "%s" is not bound between "min_instances" and "max_instances": %s' % (presentation._fullname, repr(self.default_instances)), locator=locator, level=Issue.BETWEEN_FIELDS)
        except ValueError as e:
            report('default_instances', self.default_instances, e)
            self.default_instances = 1


def get_node_template_scalable(context, presentation):
    scalable = Scalable()
    
    found = False
    capabilities = presentation.capabilities
    if capabilities:
        for key in capabilities.iterkeys():
            if key != 'scalable':
                context.validation.report('node template "%s" has unsupported capability: %s' % (presentation._fullname, repr(key)), locator=presentation._get_grandchild_locator('capabilities', key), level=Issue.BETWEEN_FIELDS)

        capability = capabilities.get('scalable')
        if capability is not None:
            properties = capability.properties
            if properties:
                for key in properties.iterkeys():
                    if key not in ('default_instances', 'min_instances', 'max_instances'):
                        context.validation.report('"scalable" capability in node template "%s" has unsupported property: %s' % (presentation._fullname, repr(key)), locator=capability._get_grandchild_locator('properties', key), level=Issue.BETWEEN_FIELDS)
                
                default_instances = properties.get('default_instances')
                scalable.default_instances = default_instances.value if default_instances is not None else 1
                min_instances = properties.get('min_instances')
                scalable.min_instances = min_instances.value if min_instances is not None else 0
                max_instances = properties.get('max_instances')
                scalable.max_instances = max_instances.value if max_instances is not None else -1
                scalable.validate(context, presentation, capability._locator)
                found = True

    if not found:
        # Deprecated
        instances = presentation.instances
        if instances is not None:
            scalable.default_instances = instances.deploy
            scalable.validate(context, presentation, instances._locator)

    return scalable
