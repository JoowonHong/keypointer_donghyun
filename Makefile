.PHONY: typehint
typehint:
	mypy --ignore-missing-imports keypointer.py

.PHONY: lint
lint:
	pylint keypointer.py

.PHONY: checklist
checklist: lint typehint 

.PHONY: black
black:
	black keypointer.py

.PHONY: clean
clean:
	find . -type f -name "*.pyc" | xargs rm -fr
	find . -type d -name __pycache__ | xargs rm -fr