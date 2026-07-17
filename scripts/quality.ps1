$ErrorActionPreference = "Stop"
$Root = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
Push-Location $Root
try {
    uv run --extra dev python scripts/validate-context.py
    uv run --extra dev flake8 .
    uv run --extra dev mypy .
    uv run --extra dev pytest
} finally {
    Pop-Location
}
