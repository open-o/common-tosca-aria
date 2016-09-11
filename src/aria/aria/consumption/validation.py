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

from .consumer import Consumer
from .. import Issue
from ..utils import LockedList, ReadOnlyList, print_exception, puts, colored, indent

class ValidationContext(object):
    def __init__(self):
        self._issues = LockedList()
        self.allow_unknown_fields = False
        self.max_level = Issue.ALL

    def report(self, message=None, exception=None, location=None, line=None, column=None, locator=None, snippet=None, level=Issue.PLATFORM, issue=None):
        if issue is None:
            issue = Issue(message, exception, location, line, column, locator, snippet, level)

        # Avoid duplicate issues
        with self._issues:        
            for i in self._issues:
                if str(i) == str(issue):
                    return
            
            self._issues.append(issue)
    
    @property
    def has_issues(self):
        return len(self._issues) > 0

    @property
    def issues(self):
        issues = [i for i in self._issues if i.level <= self.max_level] 
        issues.sort(key=lambda i: (i.level, i.location, i.line, i.column, i.message))
        return ReadOnlyList(issues)

    def dump_issues(self):
        issues = self.issues
        if issues:
            puts(colored.blue('Validation issues:', bold=True))
            with indent(2):
                for issue in issues:
                    puts(colored.blue(issue.heading_as_str))
                    details = issue.details_as_str
                    if details:
                        with indent(3):
                            puts(details)
                    if issue.exception is not None:
                        with indent(3):
                            print_exception(issue.exception)
            return True
        return False

class Validation(Consumer):
    """
    Validates the presentation.
    """

    def consume(self):
        if self.context.presentation.presenter is None:
            self.context.validation.report('Validation consumer: missing presenter')
            return

        self.context.presentation.presenter._validate(self.context)

    def dump(self):
        self.context.validation.dump_issues()
