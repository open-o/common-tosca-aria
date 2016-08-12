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
from ..consumption import ConsumptionContext, Plan
from ..utils import JSONValueEncoder, print_exception
from ..loading import FILE_LOADER_PATHS, LiteralLocation
from .utils import CommonArgumentParser, create_parser_ns
from rest_server import Config, start_server
from collections import OrderedDict
import urllib

def parse(uri):
    parser = create_parser_ns(args, uri=uri)
    context = ConsumptionContext()
    parser.parse_and_validate(context)
    return context

def issues(context):
    return {'issues': [str(i) for i in context.validation.issues]}

def validate_get(handler):
    path = urllib.unquote(handler.path[10:])
    context = parse(path)
    return issues(context) if context.validation.has_issues else {}

def validate_post(handler):
    payload = handler.get_payload()
    context = parse(LiteralLocation(payload))
    return issues(context) if context.validation.has_issues else {}

def plan_get(handler):
    path = urllib.unquote(handler.path[6:])
    context = parse(path)
    if context.validation.has_issues:
        return issues(context)
    Plan(context).create_deployment_plan()
    return context.deployment.plan_as_raw

def plan_post(handler):
    payload = handler.get_payload()
    _, issues = parse(LiteralLocation(payload))
    if issues:
        return {'issues': issues}

ROUTES = OrderedDict((
    (r'^/$', {'file': 'index.html', 'media_type': 'text/html'}),
    (r'^/validate/', {'GET': validate_get, 'POST': validate_post, 'media_type': 'application/json'}),
    (r'^/plan/', {'GET': plan_get, 'POST': plan_post, 'media_type': 'application/json'})))

class ArgumentParser(CommonArgumentParser):
    def __init__(self):
        super(ArgumentParser, self).__init__(description='REST Server', prog='aria-rest')
        self.add_argument('--port', type=int, default=8080, help='HTTP port')
        self.add_argument('--root', default='.', help='web root directory')
        self.add_argument('--path', help='path for imports')

def main():
    try:
        install_aria_extensions()
        
        global args
        args, _ = ArgumentParser().parse_known_args()
        if args.path:
            FILE_LOADER_PATHS.append(args.path)
            
        config = Config()
        config.port = args.port
        config.routes = ROUTES
        config.static_root = args.root
        config.json_encoder = JSONValueEncoder
        
        start_server(config)

    except Exception as e:
        print_exception(e)

if __name__ == '__main__':
    main()
