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

import json
        
def classname(o):
    """
    The full class name of an object.
    """
    
    return '%s.%s' % (o.__class__.__module__, o.__class__.__name__)

def safe_str(s):
    """
    Like :code:`str` coercion, but makes sure that Unicode strings are properly
    encoded, and will never return None.
    """
    
    if s is None:
        return ''
    try:
        return str(s)
    except UnicodeEncodeError:
        s = unicode(s)
        return s.encode('utf8')

def make_agnostic(value):
    """
    Converts subclasses of list and dict to standard lists and dicts, recursively.
    
    Useful for creating human-readable output of structures.
    """

    if isinstance(value, list) and (type(value) != list):
        value = list(value)
    elif isinstance(value, dict) and (type(value) != dict):
        value = dict(value)
        
    if isinstance(value, list):
        for i in range(len(value)):
            value[i] = make_agnostic(value[i])
    elif isinstance(value, dict):
        for k, v in value.iteritems():
            value[k] = make_agnostic(v)
            
    return value

class JsonAsRawEncoder(json.JSONEncoder):
    """
    A :class:`JSONEncoder` that will use the :code:`as_raw` property of objects
    if available.
    """
    
    def default(self, o):
        try:
            return iter(o)
        except TypeError:
            if hasattr(o, 'as_raw'):
                return o.as_raw
            return str(o)
        return json.JSONEncoder.default(self, o)
