.PHONY: format
format:
	./scripts/format.sh

.PHONY: lint
lint:
	./scripts/lint.sh

.PHONY: unit_test
unit_test: 
	pytest -v --cov --cov-report=xml -m "not integration_test"

.PHONY: integration_test
integration_test: 
	pytest -vs --cov --cov-report=xml -m "integration_test"

.PHONY: all_test
all_test: 
	pytest -vs --cov --cov-report=xml

.PHONY: annotate-license
annotate-license:
	find . -path ./.venv -prune -o -name "*.py" -exec reuse annotate --license Apache-2.0 --copyright "Copyright 2024 Gaudiy Inc." {} +
