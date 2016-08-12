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

from .exceptions import *
from .presenter import *
from .presentation import *
from .source import *
from .fields import *
from .field_validators import *
from .utils import *

PRESENTER_CLASSES = []

class DefaultPresenterSource(PresenterSource):
    """
    The default ARIA presenter source supports TOSCA Simple Profile and Cloudify DSLs.
    """
    
    def __init__(self, classes=PRESENTER_CLASSES):
        self.classes = classes
        #from tosca_dsl.v1_0 import ToscaSimplePresenter1_0
        #from cloudify_dsl.v1_3 import CloudifyPresenter1_3
        #self.classes = classes or [
        #    ToscaSimplePresenter1_0,
        #    CloudifyPresenter1_3]

    def get_presenter(self, raw):
        for cls in self.classes:
            if cls.can_present(raw):
                return cls
                
        return super(DefaultPresenterSource, self).get_presenter(raw)

__all__ = (
    'PresenterError',
    'PresenterNotFoundError',
    'Presenter',
    'PresentationBase',
    'Presentation',
    'AsIsPresentation',
    'PresenterSource',
    'PRESENTER_CLASSES',
    'DefaultPresenterSource',
    'Field',
    'has_fields',
    'short_form_field',
    'allow_unknown_fields',
    'primitive_field',
    'primitive_list_field',
    'object_field',
    'object_list_field',
    'object_dict_field',
    'object_sequenced_list_field',
    'object_dict_unknown_fields',
    'field_getter',
    'field_setter',
    'field_validator',
    'type_validator',
    'list_type_validator',
    'list_length_validator',
    'derived_from_validator',
    'validate_no_short_form',
    'validate_no_unknown_fields',
    'validate_known_fields',
    'report_issue_for_unknown_type',
    'report_issue_for_parent_is_self',
    'report_issue_for_circular_type_hierarchy')
