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

from ..v1_0 import ServiceTemplate as ServiceTemplate1_0
from .misc import Plugin
from aria.presentation import has_fields, object_dict_field

@has_fields
class ServiceTemplate(ServiceTemplate1_0):
    @object_dict_field(Plugin)
    def plugins(self):
        """
        :rtype: dict of str, :class:`Plugin`
        """
