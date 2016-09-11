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

from ..v1_2 import CloudifyPresenter1_2
from .templates import ServiceTemplate
from aria import Issue
from aria.utils import cachedmethod

class CloudifyPresenter1_3(CloudifyPresenter1_2):
    """
    ARIA presenter for the `Cloudify DSL v1.3 specification <http://docs.getcloudify.org/3.4.0/blueprints/overview/>`__.

    Changes over v1.2:

    * `Policies <http://docs.getcloudify.org/3.4.0/blueprints/spec-policies/>`__.
    * Imports no longer forbid `inputs`, `outputs', and `node_templates`.
    * Addition of `capabilities` to `node templates <http://docs.getcloudify.org/3.4.0/blueprints/spec-node-templates/>`__.
    * Deprecate `instances` in `node templates <http://docs.getcloudify.org/3.4.0/blueprints/spec-node-templates/>`__.
    """

    @property
    @cachedmethod
    def service_template(self):
        return ServiceTemplate(raw=self._raw)

    # Presenter

    @staticmethod
    def can_present(raw):
        dsl = raw.get('tosca_definitions_version')
        return dsl == 'cloudify_dsl_1_3'

    def _validate_import(self, context, presentation):
        r = True
        if (presentation.service_template.tosca_definitions_version is not None) and (presentation.service_template.tosca_definitions_version != self.service_template.tosca_definitions_version):
            context.validation.report('import "tosca_definitions_version" is not "%s": %s' % (self.service_template.tosca_definitions_version, presentation.service_template.tosca_definitions_version), locator=presentation._get_child_locator('inputs'), level=Issue.BETWEEN_TYPES)
            r = False
        if presentation.groups is not None:
            context.validation.report('import has forbidden "groups" section', locator=presentation._get_child_locator('groups'), level=Issue.BETWEEN_TYPES)
            r = False
        return r
    
    @property
    @cachedmethod
    def policies(self):
        return self.service_template.policies
