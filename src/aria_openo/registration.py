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
import requests
import warnings


class ServiceRegistration(object):

    def __init__(self, service_ip, service_port, service_name, service_version, openo_services_url):
        self.service_ip = service_ip
        self.service_port = service_port
        self.service_name = service_name
        self.service_version = service_version
        self.openo_services_url = openo_services_url
        self.is_registered = False

    def _register_request_headers(self):
        return {"Content-Type": "application/json"}

    def _register_request_payload(self):
        return {
            'serviceName': self.service_name,
            'version': self.service_version,
            'url': '/openoapi/{0}/{1}'.format(self.service_name, self.service_version),
            'protocol': 'REST',
            'visualRange': '1',
            'nodes': [{'ip': self.service_ip, 'port': '%d' % self.service_port}]
        }

    def _register_request(self):
        return {
            'url': self.openo_services_url,
            'data': json.dumps(self._register_request_payload()),
            'headers': self._register_request_headers()
        }

    def _unregister_request_url(self):
        return '{0}/{1}/version/{2}/nodes/{3}/{4}'.format(
            self.openo_services_url,
            self.service_name,
            self.service_version,
            self.service_ip,
            self.service_port)

    def _unregister_request(self):
        return {'url': self._unregister_request_url()}

    def register(self):
        response = requests.post(**self._register_request())

        if response.status_code != 201:
            raise RuntimeError('An error occurred while registering the parser service:\n {0} - {1}'
                               .format(response.status_code, response.reason))

        self.is_registered = True

    def unregister(self):
        response = requests.delete(**self._unregister_request())

        if response.status_code != 204:
            warnings.warn('Unregistering the parser service failed:\n {0} - {1}'
                          .format(response.status_code, response.reason))

        self.is_registered = False
