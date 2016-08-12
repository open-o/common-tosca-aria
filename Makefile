SRC=src
DOCS=docs

ARIA_SRC=$(SRC)/aria
SPHINX_SRC=$(SRC)/sphinx

.PHONY: clean aria-requirements docs-requirements docs
.DEFAULT_GOAL = test

clean:
	rm -rf $(DOCS) out .tox .coverage
	find . -type d -name '*.egg-info' -exec rm -rf {} \;
	find . -type d -name '.coverage' -exec rm -rf {} \;
	find . -type f -name '.coverage' -delete

aria-requirements:
	pip install --upgrade --requirement $(ARIA_SRC)/requirements.txt

docs-requirements:
	pip install --upgrade --requirement $(SPHINX_SRC)/requirements.txt

docs: docs-requirements aria-requirements
	rm -rf $(DOCS)
	sphinx-build -b html -c $(SPHINX_SRC) $(ARIA_SRC) $(DOCS)

test-requirements:
	pip install --upgrade tox==1.6.1

test: test-requirements
	tox
