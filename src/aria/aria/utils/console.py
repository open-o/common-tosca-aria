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

from .formatting import safe_str
from clint.textui import puts as _puts
from clint.textui.core import STDOUT
from clint.textui.colored import ColoredString as _ColoredString
from clint.textui import indent # @UnusedImport

class ColoredString(_ColoredString):
    def __init__(self, color, s, always_color=False, bold=False):
        super(ColoredString, self).__init__(color, safe_str(s), always_color, bold)

def puts(s='', newline=True, stream=STDOUT):
    _puts(safe_str(s), newline, stream)

class colored():
    @staticmethod
    def black(string, always=False, bold=False):
        return ColoredString('BLACK', string, always_color=always, bold=bold)
    
    @staticmethod
    def red(string, always=False, bold=False):
        return ColoredString('RED', string, always_color=always, bold=bold)
    
    @staticmethod
    def green(string, always=False, bold=False):
        return ColoredString('GREEN', string, always_color=always, bold=bold)
    
    @staticmethod
    def yellow(string, always=False, bold=False):
        return ColoredString('YELLOW', string, always_color=always, bold=bold)
    
    @staticmethod
    def blue(string, always=False, bold=False):
        return ColoredString('BLUE', string, always_color=always, bold=bold)
    
    @staticmethod
    def magenta(string, always=False, bold=False):
        return ColoredString('MAGENTA', string, always_color=always, bold=bold)
    
    @staticmethod
    def cyan(string, always=False, bold=False):
        return ColoredString('CYAN', string, always_color=always, bold=bold)
    
    @staticmethod
    def white(string, always=False, bold=False):
        return ColoredString('WHITE', string, always_color=always, bold=bold)
