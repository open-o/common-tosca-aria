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

from .utils import generate_id_string 
from .types import TypeHierarchy
from ..utils import JsonAsRawEncoder, StrictDict, prune, puts
from ruamel import yaml
import json, itertools

class IdType(object):
    LOCAL_SERIAL = 0
    """
    Locally unique serial ID: a running integer.
    """

    LOCAL_RANDOM = 1
    """
    Locally unique ID: 6 random safe characters.
    """
    
    UNIVERSAL_RANDOM = 2
    """
    Universally unique ID (UUID): 25 random safe characters.
    """

class DeploymentContext(object):
    """
    Properties:
    
    * :code:`id_type`: Type of IDs to use for instances
    * :code:`id_max_length`: Maximum allowed instance ID length
    * :code:`inputs`: Dict of inputs values
    * :code:`template`: The generated deployment template
    * :code:`plan`: The generated deployment plan
    * :code:`node_types`: The generated hierarchy of node types
    * :code:`capability_types`: The generated hierarchy of capability types
    * :code:`relationship_types`: The generated hierarchy of relationship types
    """

    def __init__(self):
        #self.id_type = IdType.LOCAL_SERIAL
        #self.id_type = IdType.LOCAL_RANDOM
        self.id_type = IdType.UNIVERSAL_RANDOM
        self.id_max_length = 63 # See: http://www.faqs.org/rfcs/rfc1035.html
        self.inputs = StrictDict(key_class=basestring)
        self.template = None
        self.plan = None
        self.node_types = TypeHierarchy()
        self.capability_types = TypeHierarchy()
        self.relationship_types = TypeHierarchy()
        
        self._serial_id_counter = itertools.count(1)
        self._locally_unique_ids = set()
    
    def generate_id(self):
        if self.id_type == IdType.LOCAL_SERIAL:
            return self._serial_id_counter.next()
        
        elif self.id_type == IdType.LOCAL_RANDOM:
            the_id = generate_id_string(6)
            while the_id in self._locally_unique_ids:
                the_id = generate_id_string(6)
            self._locally_unique_ids.add(the_id)
            return the_id
        
        return generate_id_string()

    @property
    def plan_as_raw(self):
        raw = self.plan.as_raw
        prune(raw)
        return raw

    def get_plan_as_yaml(self, indent=None):
        raw = self.plan_as_raw
        return yaml.dump(raw, Dumper=yaml.Dumper, allow_unicode=True, indent=indent)

    def get_plan_as_json(self, indent=None):
        raw = self.plan_as_raw
        return json.dumps(raw, indent=indent, ensure_ascii=False, cls=JsonAsRawEncoder)

    def dump_types(self, context):
        if self.node_types.children:
            puts('Node types:')
            self.node_types.dump(context)
        if self.capability_types.children:
            puts('Capability types:')
            self.capability_types.dump(context)
        if self.relationship_types.children:
            puts('Relationship types:')
            self.relationship_types.dump(context)
