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

from .loader import Loader

class LiteralLocation(object):
    def __init__(self, value):
        self.value = value

class LiteralLoader(Loader):
    """
    ARIA literal loader.
    
    This loader is a trivial holder for the provided value.
    """

    def __init__(self, value, location='<literal>'):
        self.value = value
        self.location = location
    
    def load(self):
        return self.value
