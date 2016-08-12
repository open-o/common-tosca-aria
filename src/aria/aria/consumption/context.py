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

from .. import Issue
from ..utils import ReadOnlyList, print_exception
from ..reading import ReadingContext
from ..deployment import DeploymentContext
from .style import Style
from clint.textui import puts, colored, indent
import sys

class ValidationContext(object):
    def __init__(self):
        self._issues = []
        self.allow_unknown_fields = False
        self.max_level = Issue.ALL

    def report(self, message=None, exception=None, location=None, line=None, column=None, locator=None, snippet=None, level=Issue.PLATFORM, issue=None):
        if issue is None:
            issue = Issue(message, exception, location, line, column, locator, snippet, level)

        # Avoid duplicate issues        
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
        issues.sort(key=lambda i: (i.level, i.line, i.column))
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

class ConsumptionContext(object):
    def __init__(self):
        self.presentation = None
        self.out = sys.stdout
        self.style = Style()
        self.args = []
        self.validation = ValidationContext()
        self.reading = ReadingContext()
        self.deployment = DeploymentContext()
