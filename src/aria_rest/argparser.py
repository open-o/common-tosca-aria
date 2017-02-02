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

from argparse import ArgumentParser


class AriaRestArgumentParser(ArgumentParser):

    def __init__(self):
        super(AriaRestArgumentParser, self).__init__(description='Aria REST server', prog='aria-rest')
        self.add_argument('command',
                          nargs='?',
                          help='daemon command: start, stop, restart, or status',
                          default='status')
        self.add_argument('--port',
                          type=int,
                          help='HTTP port')
        self.add_argument('--rundir',
                          help='pid and log files directory for daemons (defaults to user home)')
