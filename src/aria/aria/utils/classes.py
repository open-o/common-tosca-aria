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

from functools32 import lru_cache

class OpenClose(object):
    """
    Wraps an object that has open() and close() methods to support the "with" keyword.
    """
    
    def __init__(self, wrapped):
        self.wrapped = wrapped

    def __enter__(self):
        if hasattr(self.wrapped, 'open'):
            self.wrapped.open()
        return self.wrapped

    def __exit__(self, the_type, value, traceback):
        if hasattr(self.wrapped, 'close'):
            self.wrapped.close()
        return False
        
def classname(o):
    """
    The full class name of an object.
    """
    
    return '%s.%s' % (o.__class__.__module__, o.__class__.__name__)

cachedmethod = lru_cache()

# See also: http://code.activestate.com/recipes/498245-lru-and-lfu-cache-decorators/

class HasCachedMethods(object):
    @property
    def _method_cache_info(self):
        """
        The cache infos of all cached methods.
        
        :rtype: dict of str, CacheInfo
        """
        
        r = {}
        for k in self.__class__.__dict__:
            p = getattr(self, k)
            if hasattr(p, 'cache_info'):
                r[k] = p.cache_info()
        return r

    def _reset_method_cache(self):
        """
        Resets the caches of all cached methods.
        """
        
        for k in self.__class__.__dict__:
            p = getattr(self, k)
            if hasattr(p, 'cache_clear'):
                p.cache_clear()
