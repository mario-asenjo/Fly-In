#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"
export UV_PROJECT_ENVIRONMENT="${UV_PROJECT_ENVIRONMENT:-../.flyin-venv}"

uv run --extra dev python scripts/validate-context.py
uv run --extra dev flake8 .
uv run --extra dev mypy .
uv run --extra dev pytest
