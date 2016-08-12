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

from .. import Issue, AriaError, UnimplementedFunctionalityError
from ..utils import FixedThreadPoolExecutor, print_exception, classname
from ..consumption import Validate
from ..loading import DefaultLoaderSource
from ..reading import DefaultReaderSource, AlreadyReadError
from ..presentation import DefaultPresenterSource

class Parser(object):
    """
    Base class for ARIA parsers.
    
    Parsers generate presentations by consuming a data source via appropriate
    :class:`aria.loader.Loader`, :class:`aria.reader.Reader`, and :class:`aria.presenter.Presenter`
    instances.
    
    Note that parsing may internally trigger more than one loading/reading/presentation cycle,
    for example if the agnostic raw data has dependencies that must also be parsed.
    """
    
    def __init__(self, location, reader=None, presenter_class=None, loader_source=DefaultLoaderSource(), reader_source=DefaultReaderSource(), presenter_source=DefaultPresenterSource()):
        self.location = location
        self.reader = reader
        self.presenter_class = presenter_class
        self.loader_source = loader_source
        self.reader_source = reader_source
        self.presenter_source = presenter_source

    def parse(self, location):
        raise UnimplementedFunctionalityError(classname(self) + '.parse')

class DefaultParser(Parser):
    """
    The default ARIA parser supports agnostic raw data composition for presenters
    that have `\_get\_import\_locations` and `\_merge\_import`.
    
    To improve performance, loaders are called asynchronously on separate threads.
    """
    
    def parse(self, context=None):
        """
        :rtype: :class:`aria.presenter.Presenter`
        """
        
        presentation = None
        imported_presentations = None
        
        executor = FixedThreadPoolExecutor(timeout=10)
        try:
            presentation = self._parse_all(context, self.location, None, self.presenter_class, executor)
            executor.drain()
            
            # Handle exceptions
            if context is not None:
                for e in executor.exceptions:
                    self._handle_exception(context, e)
            else:
                executor.raise_first()
                
            imported_presentations = executor.returns
        except Exception as e:
            if context is not None:
                self._handle_exception(context, e)
            else:
                raise e
        except:
            executor.close()

        # Merge imports
        if imported_presentations is not None:
            for imported_presentation in imported_presentations:
                if hasattr(presentation, '_merge_import'):
                    presentation._merge_import(imported_presentation)
                    
        return presentation
    
    def parse_and_validate(self, context):
        try:
            context.presentation = self.parse(context)
            if context.presentation is not None:
                Validate(context).consume()
        except Exception as e:
            self._handle_exception(context, e)

    def _parse_all(self, context, location, origin_location, presenter_class, executor):
        raw, location = self._parse_one(context, location, origin_location)
        
        if presenter_class is None:
            presenter_class = self.presenter_source.get_presenter(raw)
        
        presentation = presenter_class(raw=raw)

        if presentation is not None and hasattr(presentation, '_link'):
            presentation._link()
        
        # Submit imports to executor
        if hasattr(presentation, '_get_import_locations'):
            import_locations = presentation._get_import_locations()
            if import_locations:
                for import_location in import_locations:
                    # The imports inherit the parent presenter class and use the current location as their origin location
                    executor.submit(self._parse_all, context, import_location, location, presenter_class, executor)

        return presentation
    
    def _parse_one(self, context, location, origin_location):
        if self.reader is not None:
            return self.reader.read(), self.reader.location
        loader = self.loader_source.get_loader(location, origin_location)
        reader = self.reader_source.get_reader(context.reading, location, loader)
        return reader.read(), reader.location

    def _handle_exception(self, context, e):
        if isinstance(e, AlreadyReadError):
            return
        if hasattr(e, 'issue') and isinstance(e.issue, Issue):
            context.validation.report(issue=e.issue)
        else:
            context.validation.report(exception=e)
        if not isinstance(e, AriaError):
            print_exception(e)
