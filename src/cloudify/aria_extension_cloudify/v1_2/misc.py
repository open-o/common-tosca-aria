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

from aria import dsl_specification
from aria.presentation import Presentation, has_fields, primitive_field

@has_fields
@dsl_specification('node-templates', 'cloudify-1.2')
class Instances(Presentation):
    """
    The :code:`instances` key is used for configuring the deployment characteristics of the node template.
    
    See the `Cloudify DSL v1.2 specification <http://docs.getcloudify.org/3.3.1/blueprints/spec-node-templates/>`__.
    """
    
    @primitive_field(int, default=1)
    def deploy(self):
        """
        The number of node-instances this node template will have.
        
        :rtype: int
        """
