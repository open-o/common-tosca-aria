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

from .exceptions import CannotEvaluateFunction
from .. import InvalidValueError
from ..presentation import Value
from ..utils import puts
from collections import OrderedDict
from shortuuid import ShortUUID
from random import randrange

#UUID = ShortUUID() # default alphabet is base57, which is alphanumeric without visually ambiguous characters; ID length is 22
UUID = ShortUUID(alphabet='abcdefghijklmnopqrstuvwxyz0123456789') # alphanumeric; ID length is 25

def generate_id_string(length=None):
    """
    A random string with a strong guarantee of universal uniqueness (uses UUID).
    
    The default length is 25 characters.
    """
    
    the_id = UUID.uuid()
    if length is not None:
        the_id = the_id[:length]
    return the_id

def generate_hex_string():
    """
    A random string of 5 hex digits with no guarantee of universal uniqueness.
    """

    return '%05x' % randrange(16 ** 5)

def coerce_value(context, container, value, report_issues=False):
    if isinstance(value, Value):
        value = value.value

    if isinstance(value, list):
        return [coerce_value(context, container, v, report_issues) for v in value]
    elif isinstance(value, dict):
        return OrderedDict((k, coerce_value(context, container, v, report_issues)) for k, v in value.iteritems())
    elif hasattr(value, '_evaluate'):
        try:
            value = value._evaluate(context, container)
            value = coerce_value(context, container, value, report_issues)
        except CannotEvaluateFunction:
            pass
        except InvalidValueError as e:
            if report_issues:
                context.validation.report(e.issue)
    return value

def validate_dict_values(context, the_dict):
    if not the_dict:
        return
    validate_list_values(context, the_dict.itervalues())

def validate_list_values(context, the_list):
    if not the_list:
        return
    for value in the_list:
        value.validate(context)

def coerce_dict_values(context, container, the_dict, report_issues=False):
    if not the_dict:
        return
    coerce_list_values(context, container, the_dict.itervalues(), report_issues)

def coerce_list_values(context, container, the_list, report_issues=False):
    if not the_list:
        return
    for value in the_list:
        value.coerce_values(context, container, report_issues)

def instantiate_dict(context, container, the_dict, from_dict):
    if not from_dict:
        return
    for name, value in from_dict.iteritems():
        value = value.instantiate(context, container)
        if value is not None:
            the_dict[name] = value

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
        for property_name, prop in properties.iteritems():
            if prop.type_name is not None:
                puts('%s = %s (%s)' % (context.style.property(property_name), context.style.literal(prop.value), context.style.type(prop.type_name)))
            else:
                puts('%s = %s' % (context.style.property(property_name), context.style.literal(prop.value)))

def dump_interfaces(context, interfaces, name='Interfaces'):
    if not interfaces:
        return
    puts('%s:' % name)
    with context.style.indent:
        for interface in interfaces.itervalues():
            interface.dump(context)
