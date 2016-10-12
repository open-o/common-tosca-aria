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

from .modeling.data_types import coerce_to_data_type_class, report_issue_for_bad_format, coerce_value
from aria import dsl_specification
from aria.utils import StrictDict, safe_repr
from functools import total_ordering
from datetime import datetime, tzinfo, timedelta
from collections import OrderedDict
import re

class Timezone(tzinfo):
    """
    Timezone as fixed offset in hours and minutes east of UTC.
    """

    def __init__(self, hours=0, minutes=0):
        self._offset = timedelta(hours=hours, minutes=minutes)

    def utcoffset(self, dt):
        return self._offset

    def tzname(self, dt):
        return str(self._offset)

    def dst(self, dt):
        return Timezone._ZERO

    _ZERO = timedelta(0)

UTC = Timezone()

@total_ordering
@dsl_specification('timestamp', 'yaml-1.1')
class Timestamp(object):
    '''
    TOSCA timestamps follow the YAML specification, which in turn is a variant of ISO8601.
    
    Long forms and short forms (without time of day and assuming UTC timezone) are supported for parsing.
    The canonical form (for rendering) matches the long form at the UTC timezone. 
    
    See the `Timestamp Language-Independent Type for YAML Version 1.1 (Working Draft 2005-01-18) <http://yaml.org/type/timestamp.html>`__
    '''
    
    RE_SHORT = r'^(?P<year>[0-9][0-9][0-9][0-9])-(?P<month>[0-9][0-9])-(?P<day>[0-9][0-9])$'
    RE_LONG = r'^(?P<year>[0-9][0-9][0-9][0-9])-(?P<month>[0-9][0-9]?)-(?P<day>[0-9][0-9]?)([Tt]|[ \t]+)(?P<hour>[0-9][0-9]?):(?P<minute>[0-9][0-9]):(?P<second>[0-9][0-9])(?P<fraction>\.[0-9]*)?(([ \t]*)Z|(?P<tzhour>[-+][0-9][0-9])?(:(?P<tzminute>[0-9][0-9])?)?)?$'
    CANONICAL = '%Y-%m-%dT%H:%M:%S'
    
    def __init__(self, entry_schema, constraints, value, aspect):
        value = str(value)
        match = re.match(Timestamp.RE_SHORT, value)
        if match is not None:
            # Parse short form
            year = int(match.group('year'))
            month = int(match.group('month'))
            day = int(match.group('day'))
            self.value = datetime(year, month, day, tzinfo=UTC)
        else:
            match = re.match(Timestamp.RE_LONG, value)
            if match is not None:
                # Parse long form
                year = int(match.group('year'))
                month = int(match.group('month'))
                day = int(match.group('day'))
                hour = match.group('hour')
                if hour is not None:
                    hour = int(hour)
                minute = match.group('minute')
                if minute is not None:
                    minute = int(minute)
                second = match.group('second')
                if second is not None:
                    second = int(second)
                fraction = match.group('fraction')
                if fraction is not None:
                    fraction = int(float(fraction) * 1000000.0) # convert to microseconds
                tzhour = match.group('tzhour')
                if tzhour is not None:
                    tzhour = int(tzhour)
                else:
                    tzhour = 0
                tzminute = match.group('tzminute')
                if tzminute is not None:
                    tzminute = int(tzminute)
                else:
                    tzminute = 0
                self.value = datetime(year, month, day, hour, minute, second, fraction, Timezone(tzhour, tzminute))
            else:
                raise ValueError('timestamp must be formatted as YAML ISO8601 variant or "YYYY-MM-DD"')
    
    @property
    def as_datetime_utc(self):
        return self.value.astimezone(UTC)
    
    @property
    def as_raw(self):
        return self.value
    
    def __str__(self):
        dt = self.as_datetime_utc
        return '%s%sZ' % (dt.strftime(Timestamp.CANONICAL), Timestamp._fraction_as_str(dt))
    
    def __repr__(self):
        return repr(self.__str__())

    def __eq__(self, timestamp):
        if not isinstance(timestamp, Timestamp):
            return False
        return self.value == timestamp.value

    def __lt__(self, timestamp):
        return self.value < timestamp.value
    
    @staticmethod
    def _fraction_as_str(dt):
        return '{0:g}'.format_heading(dt.microsecond / 1000000.0).lstrip('0')
    
@total_ordering
@dsl_specification('3.2.2', 'tosca-simple-profile-1.0')
class Version(object):
    """
    TOSCA supports the concept of "reuse" of type definitions, as well as template definitions which could be version and change over time. It is important to provide a reliable, normative means to represent a version string which enables the comparison and management of types and templates over time. Therefore, the TOSCA TC intends to provide a normative version type (string) for this purpose in future Working Drafts of this specification.
    
    See the `TOSCA Simple Profile v1.0 cos01 specification <http://docs.oasis-open.org/tosca/TOSCA-Simple-Profile-YAML/v1.0/cos01/TOSCA-Simple-Profile-YAML-v1.0-cos01.html#TYPE_TOSCA_VERSION>`__
    """

    RE = r'^(?P<major>\d+)\.(?P<minor>\d+)(\.(?P<fix>\d+)((\.(?P<qualifier>\d+))(\-(?P<build>\d+))?)?)?$'
    
    @staticmethod
    def key(version):
        """
        Key method for fast sorting.
        """
        return (version.major, version.minor, version.fix, version.qualifier, version.build)
    
    def __init__(self, entry_schema, constraints, value, aspect):
        value = str(value)
        match = re.match(Version.RE, value)
        if match is None:
            raise ValueError('version must be formatted as <major_version>.<minor_version>[.<fix_version>[.<qualifier>[-<build_version]]]')
        
        self.value = value
        
        self.major = match.group('major')
        self.major = int(self.major)
        self.minor = match.group('minor')
        self.minor = int(self.minor)
        self.fix = match.group('fix')
        if self.fix is not None:
            self.fix = int(self.fix)
        self.qualifier = match.group('qualifier')
        if self.qualifier is not None:
            self.qualifier = int(self.qualifier)
        self.build = match.group('build')
        if self.build is not None:
            self.build = int(self.build)

    @property
    def as_raw(self):
        return self.value

    def __str__(self):
        return self.value
    
    def __repr__(self):
        return repr(self.__str__())

    def __eq__(self, version):
        if not isinstance(version, Version):
            return False
        return (self.major, self.minor, self.fix, self.qualifier, self.build) == (version.major, version.minor, version.fix, version.qualifier, version.build)

    def __lt__(self, version):
        if self.major < version.major:
            return True
        elif self.major == version.major:
            if self.minor < version.minor:
                return True
            elif self.minor == version.minor:
                if self.fix < version.fix:
                    return True
                elif self.fix == version.fix:
                    if self.qualifier < version.qualifier:
                        return True
                    elif self.qualifier == version.qualifier:
                        if self.build < version.build:
                            return True
        return False

@dsl_specification('3.2.3', 'tosca-simple-profile-1.0')
class Range(object):
    """
    The range type can be used to define numeric ranges with a lower and upper boundary. For example, this allows for specifying a range of ports to be opened in a firewall.
    
    See the `TOSCA Simple Profile v1.0 cos01 specification <http://docs.oasis-open.org/tosca/TOSCA-Simple-Profile-YAML/v1.0/cos01/TOSCA-Simple-Profile-YAML-v1.0-cos01.html#TYPE_TOSCA_RANGE>`__
    """

    def __init__(self, entry_schema, constraints, value, aspect):
        if not isinstance(value, list):
            raise ValueError('range value is not a list: %s' % safe_repr(value))
        if len(value) != 2:
            raise ValueError('range value does not have exactly 2 elements: %s' % safe_repr(value))
        
        try:
            value[0] = int(value[0])
        except ValueError:
            raise ValueError('lower bound of range is not a valid integer: %s' % safe_repr(value[0]))

        if value[1] != 'UNBOUNDED':
            try:
                value[1] = int(value[1])
            except ValueError:
                raise ValueError('upper bound of range is not a valid integer or "UNBOUNDED": %s' % safe_repr(value[0]))

        if value[0] >= value[1]:
            raise ValueError('upper bound of range is not greater than the lower bound: %s >= %s' % (safe_repr(value[0]), safe_repr(value[1])))
        
        self.value = value
    
    def is_in(self, value):
        if value < self.value[0]:
            return False
        if self.value[1] != 'UNBOUNDED':
            if value > self.value[1]:
                return False
        return True

    @property
    def as_raw(self):
        return self.value

@dsl_specification('3.2.4', 'tosca-simple-profile-1.0')
class List(list):
    """
    The list type allows for specifying multiple values for a parameter of property. For example, if an application allows for being configured to listen on multiple ports, a list of ports could be configured using the list data type.
    
    See the `TOSCA Simple Profile v1.0 cos01 specification <http://docs.oasis-open.org/tosca/TOSCA-Simple-Profile-YAML/v1.0/cos01/TOSCA-Simple-Profile-YAML-v1.0-cos01.html#TYPE_TOSCA_LIST>`__
    """
    
    @staticmethod
    def _create(context, presentation, entry_schema, constraints, value, aspect):
        if not isinstance(value, list):
            raise ValueError('"list" data type value is not a list: %s' % safe_repr(value))

        entry_schema_type = entry_schema._get_type(context)
        entry_schema_constraints = entry_schema.constraints

        r = List()
        for v in value:
            v = coerce_value(context, presentation, entry_schema_type, None, entry_schema_constraints, v, aspect)
            if v is not None:
                r.append(v)

        return r

    # Can't define as property because it's old-style Python class
    def as_raw(self):
        return list(self)

@dsl_specification('3.2.5', 'tosca-simple-profile-1.0')
class Map(StrictDict):
    """
    The map type allows for specifying multiple values for a parameter of property as a map. In contrast to the list type, where each entry can only be addressed by its index in the list, entries in a map are named elements that can be addressed by their keys.
    
    See the `TOSCA Simple Profile v1.0 cos01 specification <http://docs.oasis-open.org/tosca/TOSCA-Simple-Profile-YAML/v1.0/cos01/TOSCA-Simple-Profile-YAML-v1.0-cos01.html#TYPE_TOSCA_MAP>`__
    """
    
    @staticmethod
    def _create(context, presentation, entry_schema, constraints, value, aspect):
        if not isinstance(value, dict):
            raise ValueError('"map" data type value is not a dict: %s' % safe_repr(value))

        if entry_schema is None:
            raise ValueError('"map" data type does not define "entry_schema"')

        entry_schema_type = entry_schema._get_type(context)
        entry_schema_constraints = entry_schema.constraints

        r = Map()
        for k, v in value.iteritems():
            v = coerce_value(context, presentation, entry_schema_type, None, entry_schema_constraints, v, aspect)
            if v is not None:
                r[k] = v

        return r

    def __init__(self, items=None):
        super(Map, self).__init__(items, key_class=str)

    # Can't define as property because it's old-style Python class
    def as_raw(self):
        return OrderedDict(self)

@total_ordering
@dsl_specification('3.2.6', 'tosca-simple-profile-1.0')
class Scalar(object):
    """
    The scalar-unit type can be used to define scalar values along with a unit from the list of recognized units.
    
    See the `TOSCA Simple Profile v1.0 cos01 specification <http://docs.oasis-open.org/tosca/TOSCA-Simple-Profile-YAML/v1.0/cos01/TOSCA-Simple-Profile-YAML-v1.0-cos01.html#TYPE_TOSCA_SCALAR_UNIT>`__
    """

    @staticmethod
    def key(scalar):
        """
        Key method for fast sorting.
        """
        return scalar.value
    
    def __init__(self, entry_schema, constraints, value, aspect):
        value = str(value)
        match = re.match(self.RE, value)
        if match is None:
            raise ValueError('scalar must be formatted as <scalar> <unit>')

        scalar = float(match.group('scalar'))
        unit = match.group('unit')

        unit_lower = unit.lower() 
        units_lower = {k.lower(): v for k, v in self.UNITS.iteritems()}
        factor = units_lower.get(unit_lower)
        if factor is None:
            raise ValueError('scalar specified with unsupported unit: %s' % safe_repr(unit))
        
        self.value = self.TYPE(scalar * factor)
    
    @property
    def as_raw(self):
        return self.value

    def __str__(self):
        return '%s %s' % (self.value, self.UNIT)

    def __repr__(self):
        return repr(self.__str__())
    
    def __eq__(self, scalar):
        if isinstance(scalar, Scalar):
            value = scalar.value
        else:
            value = self.TYPE(scalar)
        return self.value == value

    def __lt__(self, scalar):
        if isinstance(scalar, Scalar):
            value = scalar.value
        else:
            value = self.TYPE(scalar)
        return self.value < value

@dsl_specification('3.2.6.4', 'tosca-simple-profile-1.0')
class ScalarSize(Scalar):
    """
    Integer scalar for counting bytes.
    
    See the `TOSCA Simple Profile v1.0 cos01 specification <http://docs.oasis-open.org/tosca/TOSCA-Simple-Profile-YAML/v1.0/cos01/TOSCA-Simple-Profile-YAML-v1.0-cos01.html#TYPE_TOSCA_SCALAR_UNIT_SIZE>`__
    """

    # See: http://www.regular-expressions.info/floatingpoint.html
    RE = r'^(?P<scalar>[0-9]*\.?[0-9]+([eE][-+]?[0-9]+)?)\s*(?P<unit>B|kB|KiB|MB|MiB|GB|GiB|TB|TiB)$'
    
    UNITS = {
        'B':               1,
        'kB':           1000,
        'KiB':          1024,
        'MB':        1000000,
        'MiB':       1048576,
        'GB':     1000000000,
        'GiB':    1073741824,
        'TB':  1000000000000,
        'TiB': 1099511627776}

    TYPE = int
    UNIT = 'bytes'

@dsl_specification('3.2.6.5', 'tosca-simple-profile-1.0')
class ScalarTime(Scalar):
    """
    Floating point scalar for counting seconds.
    
    See the `TOSCA Simple Profile v1.0 cos01 specification <http://docs.oasis-open.org/tosca/TOSCA-Simple-Profile-YAML/v1.0/cos01/TOSCA-Simple-Profile-YAML-v1.0-cos01.html#TYPE_TOSCA_SCALAR_UNIT_TIME>`__
    """
    
    # See: http://www.regular-expressions.info/floatingpoint.html
    RE = r'^(?P<scalar>[0-9]*\.?[0-9]+([eE][-+]?[0-9]+)?)\s*(?P<unit>ns|us|ms|s|m|h|d)$'

    UNITS = {
        'ns':     0.000000001,
        'us':     0.000001,
        'ms':     0.001,
        's':      1.0,
        'm':     60.0,
        'h':   3600.0,
        'd':  86400.0}

    TYPE = float
    UNIT = 'seconds'

@dsl_specification('3.2.6.6', 'tosca-simple-profile-1.0')
class ScalarFrequency(Scalar):
    """
    Floating point scalar for counting cycles per second (Hz).

    See the `TOSCA Simple Profile v1.0 cos01 specification <http://docs.oasis-open.org/tosca/TOSCA-Simple-Profile-YAML/v1.0/cos01/TOSCA-Simple-Profile-YAML-v1.0-cos01.html#TYPE_TOSCA_SCALAR_UNIT_FREQUENCY>`__
    """
    
    # See: http://www.regular-expressions.info/floatingpoint.html
    RE = r'^(?P<scalar>[0-9]*\.?[0-9]+([eE][-+]?[0-9]+)?)\s*(?P<unit>Hz|kHz|MHz|GHz)$'

    UNITS = {
        'Hz':           1.0,
        'kHz':       1000.0,
        'MHz':    1000000.0,
        'GHz': 1000000000.0}

    TYPE = float
    UNIT = 'Hz'

#
# The following are hooked in the YAML as 'coerce_value' extensions
#

def coerce_timestamp(context, presentation, the_type, entry_schema, constraints, value, aspect):
    return coerce_to_data_type_class(context, presentation, Timestamp, entry_schema, constraints, value, aspect)

def coerce_version(context, presentation, the_type, entry_schema, constraints, value, aspect):
    return coerce_to_data_type_class(context, presentation, Version, entry_schema, constraints, value, aspect)

def coerce_range(context, presentation, the_type, entry_schema, constraints, value, aspect):
    if aspect == 'in_range':
        # When we're in a "in_range" constraint, the values are *not* themselves ranges, but numbers
        try:
            return float(value)
        except ValueError as e:
            report_issue_for_bad_format(context, presentation, the_type, value, aspect, e)
        except TypeError as e:
            report_issue_for_bad_format(context, presentation, the_type, value, aspect, e)
    else:
        return coerce_to_data_type_class(context, presentation, Range, entry_schema, constraints, value, aspect)

def coerce_list(context, presentation, the_type, entry_schema, constraints, value, aspect):
    return coerce_to_data_type_class(context, presentation, List, entry_schema, constraints, value, aspect)
    
def coerce_map_value(context, presentation, the_type, entry_schema, constraints, value, aspect):
    return coerce_to_data_type_class(context, presentation, Map, entry_schema, constraints, value, aspect)

def coerce_scalar_unit_size(context, presentation, the_type, entry_schema, constraints, value, aspect):
    return coerce_to_data_type_class(context, presentation, ScalarSize, entry_schema, constraints, value, aspect)

def coerce_scalar_unit_time(context, presentation, the_type, entry_schema, constraints, value, aspect):
    return coerce_to_data_type_class(context, presentation, ScalarTime, entry_schema, constraints, value, aspect)
    
def coerce_scalar_unit_frequency(context, presentation, the_type, entry_schema, constraints, value, aspect):
    return coerce_to_data_type_class(context, presentation, ScalarFrequency, entry_schema, constraints, value, aspect)
