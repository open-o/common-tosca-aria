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

from ..utils import make_agnostic
from clint.textui import colored, indent

class Style(object):
    def __init__(self, indentation=2):
        self.indentation = 2
    
    @property
    def indent(self):
        return indent(self.indentation)

    def section(self, value):
        return colored.cyan(value, bold=True)
    
    def type(self, value):
        return colored.blue(value, bold=True)

    def node(self, value):
        return colored.red(value, bold=True)
    
    def property(self, value):
        return colored.magenta(value, bold=True)

    def literal(self, value):
        value = make_agnostic(value)
        return colored.yellow(repr(value), bold=True)

    def meta(self, value):
        return colored.green(value)
