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

from .exceptions import LoaderError, LoaderNotFoundError, DocumentNotFoundError
from .context import LoadingContext
from .loader import Loader
from .source import LoaderSource, DefaultLoaderSource
from .location import Location, UriLocation, LiteralLocation
from .literal import LiteralLoader
from .uri import URI_LOADER_PREFIXES, UriTextLoader
from .request import SESSION, SESSION_CACHE_PATH, RequestLoader, RequestTextLoader
from .file import FileTextLoader

__all__ = (
    'LoaderError',
    'LoaderNotFoundError',
    'DocumentNotFoundError',
    'LoadingContext',
    'Loader',
    'LoaderSource',
    'DefaultLoaderSource',
    'Location',
    'UriLocation',
    'LiteralLocation',
    'LiteralLoader',
    'URI_LOADER_PREFIXES',
    'UriTextLoader'
    'SESSION',
    'SESSION_CACHE_PATH',
    'RequestLoader',
    'RequestTextLoader',
    'FileTextLoader')
