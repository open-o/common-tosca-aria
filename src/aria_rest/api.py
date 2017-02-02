#
# Copyright (c) 2017 GigaSpaces Technologies Ltd. All rights reserved.
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

import connexion
import os
import sys

from .controllers import ParseController


class AriaRestApi(object):
    DEFAULT_CONTROLLERS = [ParseController]
    DEFAULT_NAME = 'aria_rest'
    DEFAULT_PORT = 8080
    DEFAULT_SWAGGER_FILE = 'swagger.yaml'
    DEFAULT_BASE_PATH = '/'

    def _resolve(self, function_name):
        if '.' in function_name:
            controller_name, method_name = function_name.rsplit('.', 1)

            for controller in self.controllers:
                if controller_name == type(controller).__name__:
                    if hasattr(controller, method_name):
                        return getattr(controller, method_name)

        raise RuntimeError('Cannot resolve "{0}" function'.format(function_name))

    def __init__(self,
                 name=DEFAULT_NAME,
                 port=DEFAULT_PORT,
                 base_path=DEFAULT_BASE_PATH,
                 controllers=DEFAULT_CONTROLLERS,
                 swagger_file=DEFAULT_SWAGGER_FILE,
                 *args,
                 **kwargs):
        super(AriaRestApi, self).__init__(*args, **kwargs)

        self.port = port
        self.controllers = [controller_cls() for controller_cls in controllers]
        self.app = connexion.App(name,
                                 specification_dir=os.path.dirname(sys.modules[__name__].__file__))
        self.app.add_api(swagger_file,
                         base_path=base_path,
                         resolver=connexion.Resolver(function_resolver=self._resolve))

    def run(self):
        self.app.run(self.port)
