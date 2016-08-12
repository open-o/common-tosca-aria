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

from .reader import Reader
from .exceptions import ReaderSyntaxError
from .locator import Locator
import ruamel.yaml as yaml # @UnresolvedImport

class YamlLocator(Locator):
    """
    Map for agnostic raw data read from YAML.
    """
    
    def parse(self, node, location):
        if isinstance(node, yaml.SequenceNode):
            self.children = []
            for n in node.value:
                m = YamlLocator(location, n.start_mark.line + 1, n.start_mark.column + 1)
                self.children.append(m)
                m.parse(n, location)
        elif isinstance(node, yaml.MappingNode):
            self.children = {}
            for key, n in node.value:
                m = YamlLocator(location, key.start_mark.line + 1, key.start_mark.column + 1)
                self.children[key.value] = m
                m.parse(n, location)

class YamlReader(Reader):
    """
    ARIA YAML reader.
    """
    
    def read(self):
        data = self.load()
        try:
            data = str(data)
            yaml_loader = yaml.RoundTripLoader(data)
            node = yaml_loader.get_single_node()
            if node is None:
                return {}
            locator = YamlLocator(self.loader.location, 0, 0)
            locator.parse(node, self.loader.location)
            #locator.dump()
            raw = yaml_loader.construct_document(node)
            setattr(raw, '_locator', locator)
            return raw
            
            #return yaml.load(data, yaml.RoundTripLoader)
        except Exception as e:
            if isinstance(e, yaml.parser.MarkedYAMLError):
                context = e.context or 'while parsing'
                problem = e.problem
                line = e.problem_mark.line
                column = e.problem_mark.column
                snippet = e.problem_mark.get_snippet()
                raise ReaderSyntaxError('YAML %s: %s %s' % (e.__class__.__name__, problem, context), location=self.loader.location, line=line, column=column, snippet=snippet, cause=e)
            else:
                raise ReaderSyntaxError('YAML: %s' % e, cause=e)
