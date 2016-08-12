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

from .templates import ServiceTemplate
from .utils.deployment import get_deployment_template
from aria.presentation import Presenter
from aria.utils import ReadOnlyList, cachedmethod

class ToscaSimplePresenter1_0(Presenter):
    """
    ARIA presenter for the `TOSCA Simple Profile v1.0 <http://docs.oasis-open.org/tosca/TOSCA-Simple-Profile-YAML/v1.0/csprd02/TOSCA-Simple-Profile-YAML-v1.0-csprd02.html>`__.
    """
    
    @property
    @cachedmethod
    def service_template(self):
        return ServiceTemplate(raw=self._raw)
    
    # Presentation

    def _dump(self, context):
        self.service_template._dump(context)

    def _validate(self, context):
        self.service_template._validate(context)

    # Presenter

    @staticmethod
    def can_present(raw):
        dsl = raw.get('tosca_definitions_version')
        return dsl == 'tosca_simple_yaml_1_0'

    @cachedmethod
    def _get_import_locations(self):
        return ReadOnlyList([i.file for i in self.service_template.imports] if (self.service_template and self.service_template.imports) else [])

    @cachedmethod
    def _get_deployment_template(self, context):
        return get_deployment_template(context, self)

    @property
    @cachedmethod
    def repositories(self):
        return self.service_template.repositories

    @property
    @cachedmethod
    def inputs(self):
        return self.service_template.topology_template.inputs if self.service_template.topology_template is not None else None
            
    @property
    @cachedmethod
    def data_types(self):
        return self.service_template.data_types
    
    @property
    @cachedmethod
    def node_types(self):
        return self.service_template.node_types
    
    @property
    @cachedmethod
    def relationship_types(self):
        return self.service_template.relationship_types
    
    @property
    @cachedmethod
    def group_types(self):
        return self.service_template.group_types

    @property
    @cachedmethod
    def capability_types(self):
        return self.service_template.capability_types

    @property
    @cachedmethod
    def interface_types(self):
        return self.service_template.interface_types

    @property
    @cachedmethod
    def artifact_types(self):
        return self.service_template.artifact_types

    @property
    @cachedmethod
    def policy_types(self):
        return self.service_template.policy_types

    @property
    @cachedmethod
    def node_templates(self):
        return self.service_template.topology_template.node_templates if self.service_template.topology_template is not None else None

    @property
    @cachedmethod
    def relationship_templates(self):
        return self.service_template.topology_template.relationship_templates if self.service_template.topology_template is not None else None

    @property
    @cachedmethod
    def groups(self):
        return self.service_template.topology_template.groups if self.service_template.topology_template is not None else None

    @property
    @cachedmethod
    def policies(self):
        return self.service_template.topology_template.policies if self.service_template.topology_template is not None else None
