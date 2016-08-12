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

from .consumer import Consumer

class Template(Consumer):
    """
    Emits the deployment template derived from the presentation.
    """

    def consume(self):
        self.create_deployment_template()
        if not self.context.validation.has_issues:
            if '--types' in self.context.args:
                self.context.deployment.dump_types(self.context)
            else:
                self.context.deployment.template.dump(self.context)
    
    def create_deployment_template(self):
        if hasattr(self.context.presentation, '_get_deployment_template'):
            self.context.deployment.template = self.context.presentation._get_deployment_template(self.context)
            if self.context.deployment.template is not None:
                self.context.deployment.template.validate(self.context)
