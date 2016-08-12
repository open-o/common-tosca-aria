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

from aria.parsing import DefaultParser

def parse_from_path(dsl_file_path,
                    resources_base_url=None,
                    resolver=None,
                    validate_version=True,
                    additional_resource_sources=()):
    print '!!! parse_from_path'
    print dsl_file_path
    #print resources_base_url
    #print resolver
    #print validate_version
    #print additional_resource_sources
    
    parser = DefaultParser(dsl_file_path)
    #presentation = parser.parse()
    presentation, issues = parser.validate()
    if issues:
        print 'Validation issues:'
        for i in issues:
            print ' ', str(i)
    return presentation
    
def parse(dsl_string,
          resources_base_url=None,
          resolver=None,
          validate_version=True):
    print '!!! parse'
    print dsl_string
    print resources_base_url
    print resolver
    print validate_version
