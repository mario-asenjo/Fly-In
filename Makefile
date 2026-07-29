.PHONY: install run debug clean lint lint-strict test context quality

UV_ENV = $(abspath ../.flyin-venv)
export UV_PROJECT_ENVIRONMENT = $(UV_ENV)
UV_RUN = uv run --extra dev
PYTHON = $(UV_RUN) python

install:
	uv sync --extra dev

run:
	@$(PYTHON) -m flyin $(ARGS)

debug:
	@$(PYTHON) -m pdb -m flyin $(ARGS)

clean:
	rm -rf .venv .pytest_cache .mypy_cache .coverage htmlcov build dist
	rm -rf backend/src/flyin.egg-info
	find . -type d -name __pycache__ -prune -exec rm -rf {} +

lint:
	$(UV_RUN) flake8 .
	$(UV_RUN) mypy . --warn-return-any --warn-unused-ignores --ignore-missing-imports --disallow-untyped-defs --check-untyped-defs

lint-strict:
	$(UV_RUN) flake8 .
	$(UV_RUN) mypy . --strict

test:
	$(UV_RUN) pytest

context:
	$(PYTHON) scripts/validate-context.py

quality: context lint test
