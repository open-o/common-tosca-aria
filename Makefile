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

SRC=src
DOCS=docs

ARIA_SRC=$(SRC)/aria
TOSCA_SRC=$(SRC)/tosca
CLOUDIFY_SRC=$(SRC)/cloudify
SPHINX_SRC=$(SRC)/sphinx
TESTS_SRC=$(SRC)/tests

.PHONY: clean aria-requirements docs-requirements docs
.DEFAULT_GOAL = test

clean:
	rm -rf "$(DOCS)" out .tox .coverage
	find . -type d -name '*.egg-info' -exec rm -rf {} \;
	find . -type d -name '.coverage' -exec rm -rf {} \;
	find . -type f -name '.coverage' -delete

requirements:
	pip install --upgrade --requirement "$(ARIA_SRC)/requirements.txt"

docs-requirements:
	pip install --upgrade --requirement "$(SPHINX_SRC)/requirements.txt"

test-requirements:
	pip install --upgrade --requirement "$(TESTS_SRC)/requirements.txt"

docs: docs-requirements requirements
	rm -rf "$(DOCS)"
	sphinx-build -b html "$(SPHINX_SRC)" "$(DOCS)"

test: test-requirements requirements
	PYTHONPATH="$(ARIA_SRC):$(TOSCA_SRC):$(CLOUDIFY_SRC):$(PYTHONPATH)" nosetests -v -s "$(TESTS_SRC)"
