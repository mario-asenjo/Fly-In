.PHONY: install quality test type lint context

UV_RUN = uv run --extra dev

install:
	uv sync --extra dev

test:
	$(UV_RUN) pytest

type:
	$(UV_RUN) mypy .

lint:
	$(UV_RUN) flake8 .

context:
	$(UV_RUN) python scripts/validate-context.py

quality: context lint type test
