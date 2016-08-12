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

from .exceptions import LoaderNotFoundError
from .literal import LiteralLocation, LiteralLoader
from .file import FileTextLoader
from .uri import UriTextLoader
import urlparse, os.path

class LoaderSource(object):
    """
    Base class for ARIA loader sources.
    
    Loader sources provide appropriate :class:`Loader` instances for locations.
    
    A :class:`LiteralLocation` is handled specially by wrapping the literal value
    in a :class:`LiteralLoader`.
    """
    
    def get_loader(self, location, origin_location):
        if isinstance(location, LiteralLocation):
            return LiteralLoader(location.value)
        raise LoaderNotFoundError('location: %s' % location)

class DefaultLoaderSource(LoaderSource):
    """
    The default ARIA loader source will generate a :class:`UriTextLoader` for
    locations that are non-file URIs, and a :class:`FileTextLoader` for file
    URIs and other strings.
    
    If :class:`FileTextLoader` is used, a base path will be extracted from
    origin_location.
    """
    
    def get_loader(self, location, origin_location):
        if isinstance(location, basestring):
            url = urlparse.urlparse(location)
            if (not url.scheme) or (url.scheme == 'file'):
                # It's a file
                if url.scheme == 'file':
                    location = url.path
                paths = []

                # Check origin_location
                if isinstance(origin_location, basestring):
                    url = urlparse.urlparse(origin_location)
                    if (not url.scheme) or (url.scheme == 'file'):
                        # It's a file, so include its base path
                        base_path = os.path.dirname(url.path)
                        paths = [base_path]
                
                return FileTextLoader(self, location, paths=paths)
            else:
                # It's a URL
                return UriTextLoader(self, location)
            
        return super(DefaultLoaderSource, self).get_loader(location, origin_location)
