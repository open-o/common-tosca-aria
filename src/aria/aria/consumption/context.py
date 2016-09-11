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

from .validation import ValidationContext
from ..loading import LoadingContext
from ..reading import ReadingContext
from ..presentation import PresentationContext
from ..deployment import DeploymentContext
from .style import Style
import sys

class ConsumptionContext(object):
    """
    Properties:
    
    * :code:`args`: The runtime arguments (usually provided on the command line)
    * :code:`out`: Message output stream
    * :code:`style`: Message output style
    * :code:`validation`: :class:`ValidationContext`
    * :code:`loading`: :class:`aria.loading.LoadingContext`
    * :code:`reading`: :class:`aria.reading.ReadingContext`
    * :code:`presentation`: :class:`aria.presentation.PresentationContext`
    * :code:`deployment`: :class:`aria.deployment.DeploymentContext`
    """
    
    def __init__(self):
        self.args = [] #: The runtime arguments (usually provided on the command line)
        self.out = sys.stdout
        self.style = Style()
        self.validation = ValidationContext()
        self.loading = LoadingContext()
        self.reading = ReadingContext()
        self.presentation = PresentationContext()
        self.deployment = DeploymentContext()
