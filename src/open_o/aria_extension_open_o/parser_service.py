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

import json
import requests
import warnings

import ruamel.yaml as yaml

from aria import install_aria_extensions
from aria.tools.rest import Configuration as BaseConfiguration, validate_get, validate_post, model_get, model_post, instance_get, instance_post, indirect_validate_post, indirect_instance_post, indirect_model_post
from aria.tools.utils import CommonArgumentParser
from aria.utils import RestServer, JsonAsRawEncoder, print_exception, start_daemon, stop_daemon, status_daemon, puts, colored
from collections import OrderedDict
import os

API_VERSION = 1
SERVICE_NAME = 'tosca'
PATH_PREFIX = 'openoapi/%s/v%d' % (SERVICE_NAME, API_VERSION)
VALIDATE_PATH = '%s/validate' % PATH_PREFIX
INDIRECT_VALIDATE_PATH = '%s/indirect/validate' % PATH_PREFIX
MODEL_PATH = '%s/model' % PATH_PREFIX
INDIRECT_MODEL_PATH = '%s/indirect/model' % PATH_PREFIX
INSTANCE_PATH = '%s/instance' % PATH_PREFIX
INDIRECT_INSTANCE_PATH = '%s/indirect/instance' % PATH_PREFIX

CONFIG_FILE_PATH = '{0}/config/config.yaml'.format(os.path.dirname(os.path.abspath(__file__)))
DEFAULT_PORT = 8204

ROUTES = OrderedDict((
    ('^/$', {'file': 'index.html', 'media_type': 'text/html'}),
    ('^/' + VALIDATE_PATH, {'GET': validate_get, 'POST': validate_post, 'media_type': 'application/json'}),
    ('^/' + MODEL_PATH, {'GET': model_get, 'POST': model_post, 'media_type': 'application/json'}),
    ('^/' + INSTANCE_PATH, {'GET': instance_get, 'POST': instance_post, 'media_type': 'application/json'}),
    ('^/' + INDIRECT_VALIDATE_PATH, {'POST': indirect_validate_post, 'media_type': 'application/json'}),
    ('^/' + INDIRECT_MODEL_PATH, {'POST': indirect_model_post, 'media_type': 'application/json'}),
    ('^/' + INDIRECT_INSTANCE_PATH, {'POST': indirect_instance_post, 'media_type': 'application/json'})))

class ArgumentParser(CommonArgumentParser):
    def __init__(self):
        super(ArgumentParser, self).__init__(description='Open-O Common TOSCA Parser Service', prog='open-o-common-tosca-parser-service')
        self.add_argument('command', nargs='?', help='daemon command: start, stop, restart, or status')
        self.add_argument('--port', type=int, default=DEFAULT_PORT, help='HTTP port')
        self.add_argument('--root', help='web root directory')
        self.add_argument('--rundir', help='pid and log files directory for daemons (defaults to user home)')

class Configuration(BaseConfiguration):
    def __init__(self, arguments):
        super(Configuration, self).__init__(arguments)

    def create_context(self, uri):
        context = super(Configuration, self).create_context(uri)
        context.validation.allow_primitive_coersion = True # For TOSCA-155
        return context


class ServiceRegistration(object):

    def __init__(self, service_ip, service_port, service_name, service_version, openo_services_url):
        self.service_ip = service_ip
        self.service_port = service_port
        self.service_name = service_name
        self.service_version = service_version
        self.openo_services_url = openo_services_url
        self.is_registered = False

    def register(self):
        data = {"serviceName": self.service_name,
                "version": self.service_version,
                "url": '/openoapi/%s/%s' % (self.service_name, self.service_version),
                "protocol": "REST",
                "visualRange": "1",
                "nodes": [{"ip": self.service_ip, "port": "%d" % self.service_port}]}
        json_data = json.dumps(data)
        headers = {"Content-Type": "application/json"}
        resp = requests.post(
            url=self.openo_services_url,
            data=json_data,
            headers=headers)
        if resp.status_code != 201:
            raise RuntimeError('An error occurred while registering the parser service:\n'
                               '%d - %s' % (resp.status_code, resp.reason))
        self.is_registered = True

    def unregister(self):
        url = self.openo_services_url + "/%s/version/%s/nodes/%s/%d" % (
            self.service_name, self.service_version, self.service_ip, self.service_port)
        resp = requests.delete(
            url=url)
        if resp.status_code != 204:
            warnings.warn('Unregistering the parser service failed:\n'
                          '%d - %s' % (resp.status_code, resp.reason))
        self.is_registered = False


def main():
    parser_version = "v%d" % API_VERSION

    with open(CONFIG_FILE_PATH) as stream:
        config_data = yaml.load(stream)

    openo_services_rul = \
        'http://%s:%d/openoapi/microservices/v1/services' % (config_data['msb_server_ip'],
                                                             config_data['msb_server_port'])
    registration = ServiceRegistration(service_ip=config_data['parser_service_ip'],
                                       service_port=DEFAULT_PORT,
                                       service_name=SERVICE_NAME,
                                       service_version=parser_version,
                                       openo_services_url=openo_services_rul)

    try:
        install_aria_extensions()

        arguments, _ = ArgumentParser().parse_known_args()

        rest_server = RestServer()
        rest_server.configuration = Configuration(arguments)
        rest_server.port = arguments.port
        rest_server.routes = ROUTES
        rest_server.static_root = arguments.root or os.path.join(os.path.dirname(__file__), 'web')
        rest_server.json_encoder = JsonAsRawEncoder(ensure_ascii=False, separators=(',', ':'))

        if arguments.command:
            rundir = os.path.abspath(arguments.rundir or os.path.expanduser('~'))
            pidfile_path = os.path.join(rundir, 'open-o-common-tosca-parser-service.pid')

            def start():
                log_path = os.path.join(rundir, 'open-o-common-tosca-parser-service.log')
                context = start_daemon(pidfile_path, log_path)
                if context is not None:
                    with context:
                        rest_server.start(daemon=True)

            if arguments.command == 'start':
                registration.register()
                start()
            elif arguments.command == 'stop':
                stop_daemon(pidfile_path)
                registration.unregister()
            elif arguments.command == 'restart':
                stop_daemon(pidfile_path)
                start()
            elif arguments.command == 'status':
                status_daemon(pidfile_path)
            else:
                puts(colored.red('Unknown command: %s' % arguments.command))
        else:
            rest_server.start()

    except Exception as e:
        print_exception(e)
        if registration.is_registered:
            registration.unregister()

if __name__ == '__main__':
    main()
