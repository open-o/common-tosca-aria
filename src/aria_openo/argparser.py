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

from aria_rest.argparser import AriaRestArgumentParser


class AriaOpenOArgumentParser(AriaRestArgumentParser):

    def __init__(self):
        super(AriaOpenOArgumentParser, self).__init__()
        self.add_argument('--ip',
                          type=str,
                          help='IP address to be used by aria-openo service',
                          required=True)
        self.add_argument('--msb_ip',
                          type=str,
                          help='Open-O Message Service Bus IP address',
                          required=True)
        self.add_argument('--msb_port',
                          type=int,
                          help='Open-O Message Service Bus port',
                          default=80)
