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

from aria import install_aria_extensions
from aria.utils.console import (Colored, puts)
from aria_rest.api import AriaRestApi
from aria_rest.daemon import (BackgroundTaskContext, start_daemon, status_daemon, stop_daemon)

from .argparser import AriaOpenOArgumentParser
from .registration import ServiceRegistration

APP_NAME = 'aria-openo'
OPENO_SERVICE_NAME = 'tosca'
OPENO_SERVICE_VERSION = 'v1'
OPENO_SERVICE_PORT = 8204
OPENO_BASE_PATH = '/openoapi/{0}/{1}/'.format(OPENO_SERVICE_NAME, OPENO_SERVICE_VERSION)
OPENO_REGISTRATION_PATH = '/openoapi/microservices/v1/services'


def main():
    def start():
        install_aria_extensions()

        aria = AriaRestApi(name=OPENO_SERVICE_NAME,
                           port=arguments.port or OPENO_SERVICE_PORT,
                           base_path=OPENO_BASE_PATH)

        registration.register()
        start_daemon(context, aria.run)

    def stop():
        stop_daemon(context)
        registration.unregister()

    arguments, _ = AriaOpenOArgumentParser().parse_known_args()
    openo_msb_url = 'http://{0}:{1}{2}'.format(arguments.msb_ip, arguments.msb_port, OPENO_REGISTRATION_PATH)
    context = BackgroundTaskContext(APP_NAME, arguments.rundir)

    registration = ServiceRegistration(arguments.ip,
                                       OPENO_SERVICE_PORT,
                                       OPENO_SERVICE_NAME,
                                       OPENO_SERVICE_VERSION,
                                       openo_msb_url)

    if arguments.command == 'start':
        start()
    elif arguments.command == 'stop':
        stop()
    elif arguments.command == 'restart':
        stop()
        start()
    elif arguments.command == 'status':
        status_daemon(context)
    else:
        puts(Colored.red('Unknown command: {0}'.format(arguments.command)))

if __name__ == '__main__':
    main()
