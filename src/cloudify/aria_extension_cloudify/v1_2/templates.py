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

from ..v1_1 import ServiceTemplate as ServiceTemplate1_1
from .types import DataType
from .misc import Plugin, UploadResources
from aria import dsl_specification
from aria.presentation import has_fields, primitive_field, object_field, object_dict_field

@has_fields
class ServiceTemplate(ServiceTemplate1_1):
    @primitive_field()
    @dsl_specification('dsl-definitions', 'cloudify-1.2')
    @dsl_specification('dsl-definitions', 'cloudify-1.3')
    def dsl_definitions(self):
        """
        The `dsl_definitions` section can be used to define arbitrary data structures that can then be reused in different parts of the blueprint using `YAML anchors and aliases <https://gist.github.com/ddlsmurf/1590434>`__.
        
        See the `Cloudify DSL v1.3 specification <http://docs.getcloudify.org/3.4.0/blueprints/spec-dsl-definitions/>`__
        """

    @object_dict_field(DataType)
    def data_types(self):
        """
        :rtype: dict of str, :class:`DataType`
        """

    @object_dict_field(Plugin)
    def plugins(self):
        """
        :rtype: dict of str, :class:`Plugin`
        """

    @object_field(UploadResources)
    def upload_resources(self):
        """
        :rtype: :class:`UploadResources`
        """

    def _dump(self, context):
        self._dump_content(context, (
            'description',
            'tosca_definitions_version',
            'imports',
            'plugins',
            'data_types',
            'node_types',
            'policy_types',
            'inputs',
            'node_templates',
            'relationships',
            'groups',
            'policy_triggers',
            'outputs',
            'workflows',
            'upload_resources'))
