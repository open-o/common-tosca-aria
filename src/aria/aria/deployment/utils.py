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

from .. import InvalidValueError
from clint.textui import puts
from collections import OrderedDict

def coerce_value(context, container, value, report_issues=False):
    if isinstance(value, list):
        return [coerce_value(context, container, v, report_issues) for v in value]
    elif isinstance(value, dict):
        return OrderedDict((k, coerce_value(context, container, v, report_issues)) for k, v in value.iteritems())
    elif hasattr(value, '_evaluate'):
        try:
            value = value._evaluate(context, container)
        except InvalidValueError as e:
            if report_issues:
                context.validation.report(e.issue)
            return value
        value = coerce_value(context, container, value, report_issues)
    return value

def coerce_dict_values(context, container, the_dict, report_issues=False):
    for k, value in the_dict.iteritems():
        the_dict[k] = coerce_value(context, container, value, report_issues)

def instantiate_properties(context, container, properties, from_properties):
    if not from_properties:
        return
    for property_name, value in from_properties.iteritems():
        properties[property_name] = coerce_value(context, container, value)

def instantiate_interfaces(context, container, interfaces, from_interfaces):
    if not from_interfaces:
        return
    for interface_name, interface in from_interfaces.iteritems():
        interfaces[interface_name] = interface.instantiate(context, container)

def dump_list_values(context, the_list, name):
    if not the_list:
        return
    puts('%s:' % name)
    with context.style.indent:
        for value in the_list:
            value.dump(context)

def dump_dict_values(context, the_dict, name):
    if not the_dict:
        return
    dump_list_values(context, the_dict.itervalues(), name)

def dump_properties(context, properties, name='Properties'):
    if not properties:
        return
    puts('%s:' % name)
    with context.style.indent:
        for property_name, value in properties.iteritems():
            puts('%s = %s' % (context.style.property(property_name), context.style.literal(value)))

def dump_interfaces(context, interfaces):
    if not interfaces:
        return
    puts('Interfaces:')
    with context.style.indent:
        for interface in interfaces.itervalues():
            interface.dump(context)
