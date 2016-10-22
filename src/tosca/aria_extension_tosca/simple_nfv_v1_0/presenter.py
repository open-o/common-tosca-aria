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

from ..simple_v1_0 import ToscaSimplePresenter1_0
from aria.utils import FrozenList, EMPTY_READ_ONLY_LIST, cachedmethod

class ToscaSimpleNfvPresenter1_0(ToscaSimplePresenter1_0):
    """
    ARIA presenter for the `TOSCA Simple Profile for NFV v1.0 csd03 <http://docs.oasis-open.org/tosca/tosca-nfv/v1.0/csd03/tosca-nfv-v1.0-csd03.html>`__.
    
    Supported :code:`tosca_definitions_version` values:
    
    * :code:`tosca_simple_profile_for_nfv_1_0`
    """

    DSL_VERSIONS = ('tosca_simple_profile_for_nfv_1_0',)
    ALLOWED_IMPORTED_DSL_VERSIONS = ('tosca_simple_yaml_1_0', 'tosca_simple_profile_for_nfv_1_0')
    SIMPLE_PROFILE_FOR_NFV_LOCATION = 'tosca-simple-nfv-1.0/tosca-simple-nfv-1.0.yaml'

    # Presenter

    @cachedmethod
    def _get_import_locations(self, context):
        import_locations = []
        if context.presentation.import_profile:
            import_locations += (self.SIMPLE_PROFILE_LOCATION, self.SIMPLE_PROFILE_FOR_NFV_LOCATION)
        imports = self._get('service_template', 'imports')
        if imports:
            import_locations += [i.file for i in imports]
        return FrozenList(import_locations) if import_locations else EMPTY_READ_ONLY_LIST
