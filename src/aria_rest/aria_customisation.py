import os

from aria.parser.consumption.context import ConsumptionContext
from aria.parser.loading import UriLocation, LiteralLocation
from aria.utils.imports import import_fullname


class ConsumptionContextBuilder(object):
    """
    Builder for ConsumptionContext. Can be used to setup context for different usages.
    It takes dict of parameters describing context,
    passed via constructor and set corresponding context fields.

    Currently supported parameters:

    * :code:`loader_source`
    * :code:`reader_source`
    * :code:`presenter_source`
    * :code:`presenter`
    * :code:`out`
    * :code:`debug`
    * :code:`uri`
    * :code:`literal_location`
    * :code:`prefixes`
    """

    def __init__(self, *args, **kwargs):
        self.parameters = kwargs
        self.args = args

    def _set_when_defined(self,
                          object,
                          object_field_name,
                          parameters_field_name,
                          set_function,
                          instance=True):
        """
        Set `object_field_name` field in `object` using function `set_function`
        when parameter `parameters_field_name` is given.
        It can also create an instance when `set_function` is returning class.

        :param object - object, which field will be set
        :param object_field_name - name of `object` field, which will be set
        :param parameters_field_name - name of parameter,
        which value will be used to set object field
        :param set_function - function used to execute set operation,
        :param instance - if True creates new instance for result of `set_function` invocation.
        Default True
        """

        if parameters_field_name in self.parameters and self.parameters[parameters_field_name]:
            field_value = self.parameters[parameters_field_name]
            value_to_set = set_function(field_value)() if instance else set_function(field_value)

            setattr(object, object_field_name, value_to_set)

    def build(self):
        """
        Builds ConsumptionContext using predefined parameters set.
        """

        def set_uri(uri):
            return UriLocation(uri) if isinstance(uri, basestring) else uri

        def set_literal_location(literal_location):
            return LiteralLocation(literal_location)

        context = ConsumptionContext()
        context.args.extend(list(self.args))

        self._set_when_defined(
            context.loading, 'loader_source', 'loader_source', import_fullname)
        self._set_when_defined(
            context.reading, 'reader_source', 'reader_source', import_fullname)
        self._set_when_defined(
            context.presentation, 'presenter_source', 'presenter_source', import_fullname)
        self._set_when_defined(
            context.presentation, 'presenter_class', 'presenter', import_fullname)
        self._set_when_defined(
            context, 'out', 'out', lambda x: x, False)
        self._set_when_defined(
            context.presentation, 'print_exceptions', 'debug', lambda x: x, False)
        self._set_when_defined(
            context.presentation, 'location', 'uri', set_uri, False)
        self._set_when_defined(
            context.presentation, 'location', 'literal_location', set_literal_location, False)

        if 'inputs' in self.parameters:
            inputs = self.parameters['inputs']

            if inputs:
                if isinstance(inputs, dict):
                    for name, value in inputs.iteritems():
                        context.modeling.set_input(name, value)
                else:
                    context.args.append('--inputs=%s' % inputs)

        if 'prefixes' in self.parameters and self.parameters['prefixes']:
            context.loading.prefixes += [os.path.join(self.parameters['prefixes'], 'definitions')]

        return context
