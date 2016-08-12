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

from ..utils import merge
from .presentation import Presentation

class Presenter(Presentation):
    """
    Base class for ARIA presenters.
    
    Presenters provide a robust API over agnostic raw data.
    """

    def _merge_import(self, presentation):
        merge(self._raw, presentation._raw)
        if hasattr(self._raw, '_locator') and hasattr(presentation._raw, '_locator'):
            self._raw._locator.merge(presentation._raw._locator)

    def _link(self):
        locator = self._raw._locator
        locator.link(self._raw)

    def _get_import_locations(self):
        return None
    
    def _get_deployment_template(self, context):
        return None

    @property
    def repositories(self):
        return None

    @property
    def inputs(self):
        return None
            
    @property
    def outputs(self):
        return None

    @property
    def data_types(self):
        return None
    
    @property
    def node_types(self):
        return None
    
    @property
    def relationship_types(self):
        return None
    
    @property
    def group_types(self):
        return None

    @property
    def capability_types(self):
        return None

    @property
    def interface_types(self):
        return None

    @property
    def artifact_types(self):
        return None

    @property
    def policy_types(self):
        return None
    
    @property
    def node_templates(self):
        return None
    
    @property
    def relationship_templates(self):
        return None

    @property
    def groups(self):
        return None

    @property
    def policies(self):
        return None

    @property
    def policy_triggers(self):
        return None

    @property
    def workflows(self):
        return None
