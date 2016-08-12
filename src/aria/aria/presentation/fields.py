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

from ..issue import Issue
from ..exceptions import InvalidValueError, AriaError
from ..utils import ReadOnlyList, ReadOnlyDict, print_exception, deepclone, merge, cachedmethod
from functools import wraps
from types import MethodType
from collections import OrderedDict
from clint.textui import puts

class Field(object):
    def __init__(self, field_variant, fn, cls=None, default=None, allowed=None, required=False):
        self.container_cls = None
        self.name = None
        self.field_variant = field_variant
        self.fn = fn
        self.cls = cls
        self.default = default
        self.allowed = allowed
        self.required = required
    
    def get(self, presentation):
        return self._get(presentation)
    
    def _get(self, presentation):
        default_raw = presentation._get_default_raw() if hasattr(presentation, '_get_default_raw') else None

        if default_raw is None:
            raw = presentation._raw
        else:
            raw = deepclone(default_raw)
            merge(raw, presentation._raw)
        
        if self.field_variant == 'object_dict_unknown_fields':
            if isinstance(raw, dict):
                return ReadOnlyDict(((k, self.cls(name=k, raw=v, container=presentation)) for k, v in raw.iteritems() if k not in presentation.FIELDS))
            return None

        is_short_form_field = (self.container_cls.SHORT_FORM_FIELD == self.name) if hasattr(self.container_cls, 'SHORT_FORM_FIELD') else False
        is_dict = isinstance(raw, dict)

        value = None
        if is_short_form_field and not is_dict:
            value = raw
        elif is_dict:
            value = raw.get(self.name, self.default)

        if value is None:
            if self.required:
                raise InvalidValueError('required %s does not have a value' % self.fullname, locator=self.get_locator(raw))
            else:
                return None
        
        if self.allowed is not None:
            if value not in self.allowed:
                raise InvalidValueError('%s is not %s' % (self.fullname, ' or '.join([repr(v) for v in self.allowed])), locator=self.get_locator(raw))

        if self.field_variant == 'primitive':
            if (self.cls is not None) and not isinstance(value, self.cls):
                try:
                    return self.cls(value)
                except ValueError:
                    raise InvalidValueError('%s is not a valid "%s": %s' % (self.fullname, self.fullclass, repr(value)), locator=self.get_locator(raw))
            return value

        elif self.field_variant == 'primitive_list':
            if not isinstance(value, list):
                raise InvalidValueError('%s is not a list: %s' % (self.fullname, repr(value)), locator=self.get_locator(raw))
            if self.cls is not None:
                value = deepclone(value)
                for i in range(len(value)):
                    if not isinstance(value[i], self.cls):
                        try:
                            value[i] = self.cls(value[i])
                        except ValueError:
                            raise InvalidValueError('%s is not a list of "%s": element %d is %s' % (self.fullname, self.fullclass, i, repr(value[i])), locator=self.get_locator(raw))
            return ReadOnlyList(value)

        elif self.field_variant == 'object':
            try:
                return self.cls(raw=value, container=presentation)
            except TypeError as e:
                raise InvalidValueError('%s cannot not be initialized to an instance of "%s": %s' % (self.fullname, self.fullclass, repr(value)), cause=e, locator=self.get_locator(raw))

        elif self.field_variant == 'object_list':
            if not isinstance(value, list):
                raise InvalidValueError('%s is not a list: %s' % (self.fullname, repr(value)), locator=self.get_locator(raw))
            return ReadOnlyList((self.cls(raw=v, container=presentation) for v in value))

        elif self.field_variant == 'object_dict':
            if not isinstance(value, dict):
                raise InvalidValueError('%s is not a dict: %s' % (self.fullname, repr(value)), locator=self.get_locator(raw))
            return ReadOnlyDict(((k, self.cls(name=k, raw=v, container=presentation)) for k, v in value.iteritems()))

        elif self.field_variant == 'sequenced_object_list':
            if not isinstance(value, list):
                raise InvalidValueError('%s is not a sequenced list (a list of dicts, each with exactly one key): %s' % (self.fullname, repr(value)), locator=self.get_locator(raw))
            sequence = []
            for v in value:
                if not isinstance(v, dict):
                    raise InvalidValueError('%s list elements are not all dicts with exactly one key: %s' % (self.fullname, repr(value)), locator=self.get_locator(raw))
                if len(v) != 1:
                    raise InvalidValueError('%s list elements do not all have exactly one key: %s' % (self.fullname, repr(value)), locator=self.get_locator(raw))
                k, vv = v.items()[0]
                sequence.append((k, self.cls(name=k, raw=vv, container=presentation)))
            return ReadOnlyList(sequence)

        else:
            locator = self.get_locator(raw)
            location = (', at %s' % locator) if locator is not None else ''
            raise AttributeError('%s has unsupported field variant: "%s"%s' % (self.fullname, self.field_variant, location))

    def set(self, presentation, value):
        return self._set(presentation, value)

    def _set(self, presentation, value):
        raw = presentation._raw
        old = self.get(presentation)
        raw[self.name] = value
        try:
            # Validates our value
            self.get(presentation)
        except Exception as e:
            raw[self.name] = old
            raise e
        return old

    def validate(self, presentation, context):
        self._validate(presentation, context)
    
    def _validate(self, presentation, context):
        value = None
        
        try:
            value = getattr(presentation, self.name)
        except Exception as e:
            if hasattr(e, 'issue') and isinstance(e.issue, Issue):
                context.validation.report(issue=e.issue)
            else:
                context.validation.report(exception=e)
                if not isinstance(e, AriaError):
                    print_exception(e)
        
        if isinstance(value, list):
            if self.field_variant == 'object_list':
                for v in value:
                    if hasattr(v, '_validate'):
                        v._validate(context)
            elif self.field_variant == 'sequenced_object_list':
                for _, v in value:
                    if hasattr(v, '_validate'):
                        v._validate(context)
        elif isinstance(value, dict):
            if (self.field_variant == 'object_dict') or (self.field_variant == 'object_dict_unknown_fields'):
                for v in value.itervalues():
                    if hasattr(v, '_validate'):
                        v._validate(context)
        
        if hasattr(value, '_validate'):
            value._validate(context)

    @property
    def fullname(self):
        return 'field "%s" in %s.%s' % (self.name, self.container_cls.__module__, self.container_cls.__name__)

    @property
    def fullclass(self):
        return '%s.%s' % (self.cls.__module__, self.cls.__name__)

    def get_locator(self, raw):
        if hasattr(raw, '_locator'):
            if isinstance(raw._locator.children, dict):
                return raw._locator.children.get(self.name, raw._locator)
            return raw._locator
        return None
    
    def dump(self, presentation, context):
        value = getattr(presentation, self.name)
        if value is None:
            return

        if self.field_variant == 'primitive':
            puts('%s: %s' % (self.name, context.style.literal(value)))

        if self.field_variant == 'primitive_list':
            puts('%s:' % self.name)
            with context.style.indent:
                for v in value:
                    puts(context.style.literal(v))

        if self.field_variant == 'object':
            puts('%s:' % self.name)
            with context.style.indent:
                if hasattr(value, '_dump'):
                    value._dump(context)
    
        if self.field_variant == 'object_list':
            puts('%s:' % self.name)
            with context.style.indent:
                for v in value:
                    if hasattr(v, '_dump'):
                        v._dump(context)

        elif self.field_variant == 'sequenced_object_list':
            puts('%s:' % self.name)
            for _, v in value:
                if hasattr(v, '_dump'):
                    v._dump(context)
        
        elif (self.field_variant == 'object_dict') or (self.field_variant == 'object_dict_unknown_fields'):
            puts('%s:' % self.name)
            with context.style.indent:
                for v in value.itervalues():
                    if hasattr(v, '_dump'):
                        v._dump(context)
    
def has_fields_iter_field_names(self):
    for name in self.__class__.FIELDS:
        yield name

def has_fields_iter_fields(self):
    return self.FIELDS.iteritems()

def has_fields_len(self):
    return len(self.__class__.FIELDS)

def has_fields_getitem(self, key):
    if not isinstance(key, basestring):
        raise TypeError('key must be a string')
    if key not in self.__class__.FIELDS:
        raise KeyError('no \'%s\' property' % key)
    return getattr(self, key)

def has_fields_setitem(self, key, value):
    if not isinstance(key, basestring):
        raise TypeError('key must be a string')
    if key not in self.__class__.FIELDS:
        raise KeyError('no \'%s\' property' % key)
    return setattr(self, key, value)

def has_fields_delitem(self, key):
    if not isinstance(key, basestring):
        raise TypeError('key must be a string')
    if key not in self.__class__.FIELDS:
        raise KeyError('no \'%s\' property' % key)
    return setattr(self, key, None)

def has_fields_iter(self):
    return self.__class__.FIELDS.iterkeys()

def has_fields_contains(self, key):
    if not isinstance(key, basestring):
        raise TypeError('key must be a string')
    return key in self.__class__.FIELDS

def has_fields(cls):
    """
    Class decorator for validated field support.
    
    1. Adds a :code:`FIELDS` class property that is a dict of all the fields.
       Will inherit and merge :code:`FIELDS` properties from base classes if
       they have them.
    
    2. Generates automatic :code:`@property` implementations for the fields
       with the help of a set of special function decorators.

    The class also works with the Python dict protocol, so that
    fields can be accessed via dict semantics. The functionality is
    identical to that of using attribute access.

    The class will also gain two utility methods, :code:`_iter_field_names`
    and :code:`_iter_fields`.
    """
    
    # Make sure we have FIELDS
    if 'FIELDS' not in cls.__dict__:
        setattr(cls, 'FIELDS', OrderedDict())
    
    # Inherit FIELDS from base classes 
    for base in cls.__bases__:
        if hasattr(base, 'FIELDS'):
            cls.FIELDS.update(base.FIELDS)
    
    # We could do this:
    #  for name, field in cls.__dict__.iteritems():
    # But dir() is better because it has a deterministic order (alphabetical)
    
    for name in dir(cls):
        field = getattr(cls, name)
        
        if isinstance(field, Field):
            # Accumulate
            cls.FIELDS[name] = field
            
            field.name = name
            field.container_cls = cls
            
            # This function is here just to create an enclosed scope for "field"
            def closure(field):
                
                # By convention, we have the getter wrap the original function.
                # (It is, for example, where the Python help() function will look for
                # docstrings when encountering a property.)
                @cachedmethod
                @wraps(field.fn)
                def getter(self):
                    return field.get(self)
                    
                def setter(self, value):
                    field.set(self, value)

                # Convert to Python property
                return property(fget=getter, fset=setter)

            setattr(cls, name, closure(field))

    # Bind methods
    setattr(cls, '_iter_field_names', MethodType(has_fields_iter_field_names, None, cls))
    setattr(cls, '_iter_fields', MethodType(has_fields_iter_fields, None, cls))
    
    # Behave like a dict
    setattr(cls, '__len__', MethodType(has_fields_len, None, cls))
    setattr(cls, '__getitem__', MethodType(has_fields_getitem, None, cls))
    setattr(cls, '__setitem__', MethodType(has_fields_setitem, None, cls))
    setattr(cls, '__delitem__', MethodType(has_fields_delitem, None, cls))
    setattr(cls, '__iter__', MethodType(has_fields_iter, None, cls))
    setattr(cls, '__contains__', MethodType(has_fields_contains, None, cls))
    
    return cls

def short_form_field(name):
    """
    Class decorator for specifying the short form field.
    
    The class must be decorated with :func:`has_fields`.
    """
    def decorator(cls):
        if hasattr(cls, name) and hasattr(cls, 'FIELDS') and (name in cls.FIELDS):
            setattr(cls, 'SHORT_FORM_FIELD', name)
            return cls
        else:
            raise AttributeError('@short_form_field must be used with a Field name in @has_fields class')
    return decorator

def allow_unknown_fields(cls):
    """
    Class decorator specifying that the class allows unknown fields.
    
    The class must be decorated with :func:`has_fields`.
    """
    if hasattr(cls, 'FIELDS'):
        setattr(cls, 'ALLOW_UNKNOWN_FIELDS', True)
        return cls
    else:
        raise AttributeError('@allow_unknown_fields must be used with a @has_fields class')


def primitive_field(cls=None, default=None, allowed=None, required=False):
    """
    Function decorator for primitive fields.
    
    The function must be a method in a class decorated with :func:`has_fields`.
    """
    def decorator(fn):
        return Field(field_variant='primitive', fn=fn, cls=cls, default=default, allowed=allowed, required=required)
    return decorator

def primitive_list_field(cls=None, default=None, allowed=None, required=False):
    """
    Function decorator for list of primitive fields.
    
    The function must be a method in a class decorated with :func:`has_fields`.
    """
    def decorator(fn):
        return Field(field_variant='primitive_list', fn=fn, cls=cls, default=default, allowed=allowed, required=required)
    return decorator

def object_field(cls, default=None, allowed=None, required=False):
    """
    Function decorator for object fields.
    
    The function must be a method in a class decorated with :func:`has_fields`.
    """
    def decorator(fn):
        return Field(field_variant='object', fn=fn, cls=cls, default=default, allowed=allowed, required=required)
    return decorator

def object_list_field(cls, default=None, allowed=None, required=False):
    """
    Function decorator for list of object fields.
    
    The function must be a method in a class decorated with :func:`has_fields`.
    """
    def decorator(fn):
        return Field(field_variant='object_list', fn=fn, cls=cls, default=default, allowed=allowed, required=required)
    return decorator

def object_dict_field(cls, default=None, allowed=None, required=False):
    """
    Function decorator for dict of object fields.
    
    The function must be a method in a class decorated with :func:`has_fields`.
    """
    def decorator(fn):
        return Field(field_variant='object_dict', fn=fn, cls=cls, default=default, allowed=allowed, required=required)
    return decorator

def object_sequenced_list_field(cls, default=None, allowed=None, required=False):
    """
    Function decorator for sequenced list of object fields.
    
    The function must be a method in a class decorated with :func:`has_fields`.
    """
    def decorator(fn):
        return Field(field_variant='sequenced_object_list', fn=fn, cls=cls, default=default, allowed=allowed, required=required)
    return decorator

def object_dict_unknown_fields(cls, default=None, allowed=None, required=False):
    """
    Function decorator for dict of object fields, for all the fields that are not already decorated.
    
    The function must be a method in a class decorated with :func:`has_fields`.
    """
    def decorator(fn):
        return Field(field_variant='object_dict_unknown_fields', fn=fn, cls=cls, default=default, allowed=allowed, required=required)
    return decorator

def field_getter(getter_fn):
    """
    Function decorator for overriding the getter function of a field.
    
    The signature of the getter function must be: :code:`f(field, presentation)`.
    The default getter can be accessed as :code:`field._get(presentation)`.
    
    The function must already be decorated with a field decorator.
    """
    def decorator(field):
        if isinstance(field, Field):
            field.get = MethodType(getter_fn, field, Field)
            return field
        else:
            raise AttributeError('@field_getter must be used with a Field')
    return decorator

def field_setter(setter_fn):
    """
    Function decorator for overriding the setter function of a field.
    
    The signature of the setter function must be: :code:`f(field, presentation, value)`.
    The default setter can be accessed as :code:`field._set(presentation, value)`.
    
    The function must already be decorated with a field decorator.
    """
    def decorator(field):
        if isinstance(field, Field):
            field.set = MethodType(setter_fn, field, Field)
            return field
        else:
            raise AttributeError('@field_setter must be used with a Field')
    return decorator

def field_validator(validator_fn):
    """
    Function decorator for overriding the validator function of a field.
    
    The signature of the validator function must be: :code:f(field, presentation, context)`.
    The default validator can be accessed as :code:`field._validate(presentation, context)`.
    
    The function must already be decorated with a field decorator.
    """
    def decorator(field):
        if isinstance(field, Field):
            field.validate = MethodType(validator_fn, field, Field)
            return field
        else:
            raise AttributeError('@field_validator must be used with a Field')
    return decorator
