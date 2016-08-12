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

from ..utils import JSONValueEncoder, prune
from .hierarchy import TypeHierarchy
from clint.textui import puts
import json

class DeploymentContext(object):
    def __init__(self):
        self.template = None
        self.plan = None
        self.node_types = TypeHierarchy()
        self.capability_types = TypeHierarchy()

    @property
    def plan_as_raw(self):
        raw = self.plan.as_raw
        prune(raw)
        return raw

    def get_plan_as_json(self, indent=None):
        raw = self.plan_as_raw
        return json.dumps(raw, indent=indent, cls=JSONValueEncoder)

    def dump_types(self, context):
        if self.node_types.children:
            puts('Node types:')
            self.node_types.dump(context)
        if self.capability_types.children:
            puts('Capability types:')
            self.capability_types.dump(context)
