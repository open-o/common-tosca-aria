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

from .utils import BaseArgumentParser
from .. import install_aria_extensions, DSL_SPECIFICATION_PACKAGES, DSL_SPECIFICATION, iter_spec
from ..utils import print_exception, import_modules, puts, colored, indent
import csv, sys

class ArgumentParser(BaseArgumentParser):
    def __init__(self):
        super(ArgumentParser, self).__init__(description='Specification Tool', prog='aria-spec')
        self.add_argument('--csv', action='store_true', help='output as CSV')

def main():
    try:
        args, _ = ArgumentParser().parse_known_args()

        install_aria_extensions()
        
        # Make sure that all @dsl_specification decorators are processed
        for p in DSL_SPECIFICATION_PACKAGES:
            import_modules(p)

        if args.csv:
            w = csv.writer(sys.stdout, quoting=csv.QUOTE_ALL)
            w.writerow(('Specification', 'Section', 'Code', 'URL'))
            for spec in sorted(DSL_SPECIFICATION):
                for section, details in iter_spec(spec):
                    w.writerow((spec, section, details['code'], details['url']))
        
        else:
            for spec in sorted(DSL_SPECIFICATION):
                puts(colored.cyan(spec))
                with indent(2):
                    for section, details in iter_spec(spec):
                        puts(colored.blue(section))
                        with indent(2):
                            for k, v in details.iteritems():
                                puts('%s: %s' % (colored.magenta(k), v))
        
    except Exception as e:
        print_exception(e)

if __name__ == '__main__':
    main()
