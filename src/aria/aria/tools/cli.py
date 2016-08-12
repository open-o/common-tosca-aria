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
from ..utils import print_exception, import_fullname
from ..consumption import ConsumptionContext
from .utils import CommonArgumentParser, create_parser_ns

class ArgumentParser(CommonArgumentParser):
    def __init__(self):
        super(ArgumentParser, self).__init__(description='CLI', prog='aria')
        self.add_argument('uri', help='URI or file path to profile')
        self.add_argument('consumer', nargs='?', default='aria.consumption.Plan', help='consumer class')

def main():
    try:
        args, unknown_args = ArgumentParser().parse_known_args()
        
        consumer_class_name = args.consumer
        if '.' not in consumer_class_name:
            consumer_class_name = consumer_class_name.title()
        
        install_aria_extensions()

        consumer_class = import_fullname(consumer_class_name, ['aria.consumption'])
        parser = create_parser_ns(args)

        context = ConsumptionContext()
        context.args = unknown_args
        
        parser.parse_and_validate(context)
        
        if context.validation.dump_issues():
            exit(0)

        consumer_class(context).consume()
        
        context.validation.dump_issues()
    except Exception as e:
        print_exception(e)

if __name__ == '__main__':
    main()
