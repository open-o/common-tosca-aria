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

from aria import DSL_SPECIFICATION_PACKAGES
from aria.presentation import PRESENTER_CLASSES
from .v1_3 import CloudifyPresenter1_3

def install_aria_extension():
    # v1.3 presenter
    PRESENTER_CLASSES.append(CloudifyPresenter1_3)
    
    # DSL specification
    DSL_SPECIFICATION_PACKAGES.append('aria_extension_cloudify')

MODULES = (
    'v1_2',
    'v1_3')

__all__ = (
    'MODULES',
    'install_aria_extension')
