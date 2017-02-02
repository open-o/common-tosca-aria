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

import json

from aria.parser.consumption import ConsumerChain, Read, Validate, Model, Inputs, Instance
from aria.utils.formatting import json_dumps

from .aria_customisation import ConsumptionContextBuilder


def json_response(function):
    return lambda instance, **kwargs: json.loads(json_dumps(function(instance, **kwargs)))


def dump_issues(function):
    def render_issues(data, *args):
        try:
            return function(data, *args)
        except ControllerOperationError as e:
            return {'issues': e.issues}

    return render_issues


class ControllerOperationError(Exception):

    def __init__(self, issues):
        super(ControllerOperationError, self).__init__()
        self.issues = issues


# TODO in future if needed
class Controller(object):
    pass


class ParseController(Controller):

    @staticmethod
    def _execute_command(command_data, consumers, *args):
        context = ConsumptionContextBuilder(*args, **command_data).build()
        ConsumerChain(context, consumers).consume()

        if context.validation.has_issues:
            raise ControllerOperationError(context.validation.issues_as_raw)

        return context

    @classmethod
    @dump_issues
    def _validate(cls, data, *args):
        cls._execute_command(data, (Read, Validate), *args)

        return {}

    @classmethod
    @dump_issues
    def _model(cls, data, *args):
        context = cls._execute_command(data, (Read, Validate, Model), *args)

        return {
            'types': context.modeling.types_as_raw,
            'model': context.modeling.model_as_raw
        }

    @classmethod
    @dump_issues
    def _instance(cls, data, *args):
        context = cls._execute_command(data, (Read, Validate, Model, Inputs, Instance), *args)

        return {
            'types': context.modeling.types_as_raw,
            'model': context.modeling.model_as_raw,
            'instance': context.modeling.instance_as_raw
         }

    @json_response
    def validate_file(self, path):
        return self._validate({'uri': path})

    @json_response
    def validate_indirect(self, indirect_data):
        return self._validate(indirect_data)

    @json_response
    def validate_upload(self, upload_content, inputs=''):
        return self._validate({'literal_location': upload_content})

    @json_response
    def model_file(self, path):
        return self._model({'uri': path})

    @json_response
    def model_indirect(self, indirect_data):
        return self._model(indirect_data)

    @json_response
    def model_upload(self, upload_content, inputs=''):
        return self._model({'literal_location': upload_content})

    @json_response
    def instance_file(self, path, inputs=''):
        return self._instance({'uri': path, 'inputs': inputs})

    @json_response
    def instance_indirect(self, indirect_data):
        return self._instance(indirect_data, '--json')

    @json_response
    def instance_upload(self, upload_content, inputs=''):
        return self._instance({'literal_location': upload_content, 'inputs': inputs})
