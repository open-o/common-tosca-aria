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

from .. import UnimplementedFunctionalityError
from ..utils import OpenClose, classname
from .exceptions import ReaderError, AlreadyReadError

class Reader(object):
    """
    Base class for ARIA readers.
    
    Readers provide agnostic raw data by consuming :class:`aria.loader.Loader` instances.
    """
    
    def __init__(self, context, source, location, loader):
        self.context = context
        self.source = source
        self.location = location
        self.loader = loader

    def load(self):
        with OpenClose(self.loader) as loader:
            if self.context is not None:
                with self.context.locations:
                    if loader.location in self.context.locations:
                        raise AlreadyReadError('already read: %s' % loader.location)
                    else:
                        self.context.locations.append(loader.location)
            
            data = loader.load()
            if data is None:
                raise ReaderError('loader did not provide data: %s' % loader)
            self.location = loader.location # loader may change the location during loading
            return data
    
    def read(self):
        raise UnimplementedFunctionalityError(classname(self) + '.read')
