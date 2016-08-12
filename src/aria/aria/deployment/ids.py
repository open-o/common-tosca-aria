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

import random
from shortuuid import ShortUUID

# See: https://github.com/stochastic-technologies/shortuuid
UUID = ShortUUID(alphabet='01234567890ABCDEF')

def generate_id():
    return UUID.uuid()

GENERATED_IDS = set()

def generate_classic_id():
    def gen():
        return '%05x' % random.randrange(16 ** 5)
    the_id = gen()
    
    # TODO: a bad way to make sure our IDs are unique (they won't be unique across
    # multiple running instances of ARIA), but better than nothing
    while the_id in GENERATED_IDS:
        the_id = gen()
    GENERATED_IDS.add(the_id)

    return the_id
