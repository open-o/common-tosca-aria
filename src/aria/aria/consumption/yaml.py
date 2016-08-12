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

from ..reading import init_yaml
from .consumer import Consumer
from .exceptions import ConsumerError
import ruamel.yaml as yaml # @UnresolvedImport

class Yaml(Consumer):
    """
    Emits the presentation's raw data as YAML.
    """
    
    def consume(self):
        try:
            init_yaml()
            text = yaml.dump(self.context.presentation._raw, Dumper=yaml.RoundTripDumper)
            self.context.out.write(text)
        except Exception as e:
            raise ConsumerError('YamlWriter: %s' % e, cause=e)
