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

from .api import AriaRestApi
from .argparser import AriaRestArgumentParser
from .daemon import (BackgroundTaskContext, start_daemon, status_daemon, stop_daemon)

APP_NAME = 'aria-rest'


def main():
    def start():
        install_aria_extensions()

        aria = AriaRestApi(port=arguments.port) if arguments.port else AriaRestApi()
        start_daemon(context, aria.run)

    arguments, _ = AriaRestArgumentParser().parse_known_args()
    context = BackgroundTaskContext(APP_NAME, arguments.rundir)

    if arguments.command == 'start':
        start()
    elif arguments.command == 'stop':
        stop_daemon(context)
    elif arguments.command == 'restart':
        stop_daemon(context)
        start()
    elif arguments.command == 'status':
        status_daemon(context)
    else:
        puts(Colored.red('Unknown command: {0}'.format(arguments.command)))

if __name__ == '__main__':
    main()
