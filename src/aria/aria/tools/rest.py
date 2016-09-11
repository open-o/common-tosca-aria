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

from .. import install_aria_extensions
from ..consumption import ConsumerChain, Presentation, Validation, Template, Inputs, Plan
from ..utils import JsonAsRawEncoder, print_exception
from ..loading import LiteralLocation
from .utils import CommonArgumentParser, create_context_from_namespace
from rest_server import Config, start_server
from collections import OrderedDict
from urlparse import urlparse, parse_qs
import urllib

API_VERSION = 1
PATH_PREFIX = 'openoapi/tosca/v%d' % API_VERSION
INDIRECT_VALIDATE_PATH = '%s/indirect/validate' % PATH_PREFIX
VALIDATE_PATH = '%s/validate' % PATH_PREFIX
PLAN_PATH = '%s/plan' % PATH_PREFIX
INDIRECT_PLAN_PATH = '%s/indirect/plan' % PATH_PREFIX

# Utils

def parse_path(handler):
    parsed = urlparse(urllib.unquote(handler.path))
    query = parse_qs(parsed.query, keep_blank_values=True)
    return parsed.path, query

def parse_indirect_payload(handler):
    def error(message):
        handler.send_response(400)
        handler.end_headers()
        handler.wfile.write('%s\n' % message)
        handler.handled = True

    try:
        payload = handler.get_json_payload()
    except:
        error('Payload is not JSON')
        return None, None
    
    for key in payload.iterkeys():
        if key not in ('uri', 'inputs'):
            error('Payload has unsupported field: %s' % key)
            return None, None
    
    try:
        uri = payload['uri']
    except:
        error('Payload does not have required "uri" field')
        return None, None
    
    inputs = payload.get('inputs')
    
    return uri, inputs 

def validate(uri):
    context = create_context_from_namespace(args, uri=uri)
    ConsumerChain(context, (Presentation, Validation)).consume()
    return context

def plan(uri, inputs):
    context = create_context_from_namespace(args, uri=uri)
    if inputs:
        context.args.append('--inputs=%s' % inputs)
    ConsumerChain(context, (Presentation, Validation, Template, Inputs, Plan)).consume()
    return context

def issues(context):
    return {'issues': [i.as_raw for i in context.validation.issues]}

# Handlers

def validate_get(handler):
    path, _ = parse_path(handler)
    uri = path[len(VALIDATE_PATH) + 2:]
    context = validate(uri)
    return issues(context) if context.validation.has_issues else {}

def validate_post(handler):
    payload = handler.get_payload()
    context = validate(LiteralLocation(payload))
    return issues(context) if context.validation.has_issues else {}

def indirect_validate_post(handler):
    uri, _ = parse_indirect_payload(handler)
    if uri is None:
        return None  
    context = validate(uri)
    return issues(context) if context.validation.has_issues else {}

def plan_get(handler):
    path, query = parse_path(handler)
    uri = path[len(PLAN_PATH) + 2:]
    inputs = query.get('inputs')
    if inputs:
        inputs = inputs[0]
    context = plan(uri, inputs)
    return issues(context) if context.validation.has_issues else context.deployment.plan_as_raw

def plan_post(handler):
    _, query = parse_path(handler)
    inputs = query.get('inputs')
    if inputs:
        inputs = inputs[0]
    payload = handler.get_payload()
    context = plan(LiteralLocation(payload), inputs)
    return issues(context) if context.validation.has_issues else context.deployment.plan_as_raw

def indirect_plan_post(handler):
    uri, inputs = parse_indirect_payload(handler)
    if uri is None:
        return None
    if inputs:
        inputs = handler.config.json_encoder.encode(inputs)  
    context = plan(uri, inputs)
    return issues(context) if context.validation.has_issues else context.deployment.plan_as_raw

ROUTES = OrderedDict((
    ('^/$', {'file': 'index.html', 'media_type': 'text/html'}),
    ('^/' + VALIDATE_PATH, {'GET': validate_get, 'POST': validate_post, 'media_type': 'application/json'}),
    ('^/' + PLAN_PATH, {'GET': plan_get, 'POST': plan_post, 'media_type': 'application/json'}),
    ('^/' + INDIRECT_VALIDATE_PATH, {'POST': indirect_validate_post, 'media_type': 'application/json'}),
    ('^/' + INDIRECT_PLAN_PATH, {'POST': indirect_plan_post, 'media_type': 'application/json'})))

class ArgumentParser(CommonArgumentParser):
    def __init__(self):
        super(ArgumentParser, self).__init__(description='REST Server', prog='aria-rest')
        self.add_argument('--port', type=int, default=8204, help='HTTP port')
        self.add_argument('--root', default='.', help='web root directory')

def main():
    try:
        install_aria_extensions()
        
        global args
        args, _ = ArgumentParser().parse_known_args()
            
        config = Config()
        config.port = args.port
        config.routes = ROUTES
        config.static_root = args.root
        config.json_encoder = JsonAsRawEncoder(ensure_ascii=False, separators=(',',':'))
        
        start_server(config)

    except Exception as e:
        print_exception(e)

if __name__ == '__main__':
    main()
