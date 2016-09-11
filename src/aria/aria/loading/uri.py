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
from .exceptions import LoaderError, DocumentNotFoundError
from requests import Session
from requests.exceptions import ConnectionError
from cachecontrol import CacheControl
from cachecontrol.caches import FileCache

SESSION = None
SESSION_CACHE_PATH = '/tmp'

class UriLoader(Loader):
    """
    Base class for ARIA URI loaders.
    
    Extracts a document from a URI.
    
    Note that the "file:" schema is not supported: :class:`FileTextLoader` should
    be used instead.
    """

    def __init__(self, location, headers={}):
        self.location = location
        self.headers = headers
        self.response = None
    
    def open(self):
        global SESSION
        if SESSION is None:
            SESSION = CacheControl(Session(), cache=FileCache(SESSION_CACHE_PATH))
            
        try:
            self.response = SESSION.get(self.location.uri, headers=self.headers)
            status = self.response.status_code
            if status == 404:
                self.response = None
                raise DocumentNotFoundError('URI not found: "%s"' % self.location)
            elif status != 200:
                self.response = None
                raise LoaderError('URI request error %d: "%s"' % (status, self.location))
        except ConnectionError as e:
            raise LoaderError('URI connection error: "%s"' % self.location, cause=e)
        except Exception as e:
            raise LoaderError('URI error: "%s"' % self.location, cause=e)

class UriTextLoader(UriLoader):
    """
    ARIA URI text loader.
    """

    def load(self):
        if self.response is not None:
            try:
                return self.response.text
            except Exception as e:
                raise LoaderError('URI: %s' % self.location, cause=e)
        return None
