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

from .utils import instantiate_properties, coerce_dict_values, dump_dict_values, dump_properties
from .. import UnimplementedFunctionalityError, classname
from ..utils import StrictList, StrictDict, make_agnostic
from collections import OrderedDict
from clint.textui import puts

class Element(object):
    def validate(self, context):
        pass

    def coerce_values(self, context, container, report_issues):
        pass
    
    @property
    def as_raw(self):
        raise UnimplementedFunctionalityError(classname(self) + '.as_raw')

    def dump(self, context):
        pass

class Template(Element):
    def instantiate(self, context, container):
        pass

class Function(object):
    def _evaluate(self, context, container):
        raise UnimplementedFunctionalityError(classname(self) + '._evaluate')

class Interface(Template):
    def __init__(self, name):
        if not isinstance(name, basestring):
            raise ValueError('must set name (string)')
        
        self.name = name
        self.inputs = StrictDict(str)
        self.operations = StrictDict(str, Operation)

    def instantiate(self, context, container):
        r = Interface(self.name)
        instantiate_properties(context, container, r.inputs, self.inputs)
        for operation_name, operation in self.operations.iteritems():
            r.operations[operation_name] = operation.instantiate(context, container)
        return r
                
    def validate(self, context):
        for operation in self.operations.itervalues():
            operation.validate(context)

    def coerce_values(self, context, container, report_issues):
        coerce_dict_values(context, container, self.inputs, report_issues)
        for operation in self.operations.itervalues():
            operation.coerce_values(context, container, report_issues)
    
    @property
    def as_raw(self):
        return OrderedDict((
            ('name', self.name),
            ('inputs', self.inputs),
            ('operations', [v.as_raw for v in self.operations.itervalues()])))

    def dump(self, context):
        puts(context.style.node(self.name))
        with context.style.indent:
            dump_properties(context, self.inputs, 'Inputs')
            dump_dict_values(context, self.operations, 'Operations')

class Operation(Template):
    def __init__(self, name):
        if not isinstance(name, basestring):
            raise ValueError('must set name (string)')
        
        self.name = name
        self.implementation = None
        self.dependencies = StrictList(str)
        self.executor = None # Cloudify
        self.max_retries = None # Cloudify
        self.retry_interval = None # Cloudify
        self.inputs = StrictDict(str)

    def instantiate(self, context, container):
        r = Operation(self.name)
        r.implementation = self.implementation
        r.dependencies = self.dependencies
        r.executor = self.executor
        r.max_retries = self.max_retries
        r.retry_interval = self.retry_interval
        instantiate_properties(context, container, r.inputs, self.inputs)
        return r

    def coerce_values(self, context, container, report_issues):
        coerce_dict_values(context, container, self.inputs, report_issues)

    @property
    def as_raw(self):
        return OrderedDict((
            ('name', self.name),
            ('implementation', self.implementation),
            ('dependencies', self.dependencies),
            ('executor', self.executor),
            ('max_retries', self.max_retries),
            ('retry_interval', self.retry_interval),
            ('inputs', self.inputs)))

    def dump(self, context):
        puts(context.style.node(self.name))
        with context.style.indent:
            if self.implementation is not None:
                puts('Implementation: %s' % context.style.literal(self.implementation))
            if self.dependencies:
                puts('Dependencies: %s' % ', '.join((str(context.style.literal(v)) for v in self.dependencies)))
            if self.executor is not None:
                puts('Executor: %s' % context.style.literal(self.executor))
            if self.max_retries is not None:
                puts('Max retries: %s' % context.style.literal(self.max_retries))
            if self.retry_interval is not None:
                puts('Retry interval: %s' % context.style.literal(self.retry_interval))
            dump_properties(context, self.inputs, 'Inputs')

class Artifact(Template):
    def __init__(self, name, type_name, source_path):
        if not isinstance(name, basestring):
            raise ValueError('must set name (string)')
        if not isinstance(type_name, basestring):
            raise ValueError('must set type_name (string)')
        if not isinstance(source_path, basestring):
            raise ValueError('must set source_path (string)')
        
        self.name = name
        self.type_name = type_name
        self.source_path = source_path
        self.target_path = None
        self.repository_url = None
        self.repository_credential = StrictDict(str, str)
        self.properties = StrictDict(str)

    def instantiate(self, context, container):
        r = Artifact(self.name, self.type_name, self.source_path)
        r.target_path = self.target_path
        r.repository_url = self.repository_url
        r.repository_credential = self.repository_credential
        instantiate_properties(context, container, r.properties, self.properties)
        return r

    def coerce_values(self, context, container, report_issues):
        coerce_dict_values(context, container, self.properties, report_issues)

    @property
    def as_raw(self):
        return OrderedDict((
            ('name', self.name),
            ('type_name', self.type_name),
            ('source_path', self.source_path),
            ('target_path', self.target_path),
            ('repository_url', self.repository_url),
            ('repository_credential', make_agnostic(self.repository_credential)),
            ('properties', self.properties)))

    def dump(self, context):
        puts(context.style.node(self.name))
        with context.style.indent:
            puts('Artifact type: %s' % context.style.type(self.type_name))
            puts('Source path: %s' % context.style.literal(self.source_path))
            if self.target_path is not None:
                puts('Target path: %s' % context.style.literal(self.target_path))
            if self.repository_url is not None:
                puts('Repository URL: %s' % context.style.literal(self.repository_url))
            if self.repository_credential:
                puts('Repository credential: %s' % context.style.literal(self.repository_credential))
            dump_properties(context, self.properties)