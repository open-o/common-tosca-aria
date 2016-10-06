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

from .source import DefaultLoaderSource 
from ..utils import StrictList

class LoadingContext(object):
    """
    Properties:
    
    * :code:`loader_source`: For finding loader instances
    * :code:`file_search_paths`: List of additional search paths for :class:`FileTextLoader`
    * :code:`uri_search_paths`: List of additional search paths for :class:`UriLoader`
    """
    
    def __init__(self):
        self.loader_source = DefaultLoaderSource()
        self.file_search_paths = StrictList(value_class=basestring)
        self.uri_search_paths = StrictList(value_class=basestring)
