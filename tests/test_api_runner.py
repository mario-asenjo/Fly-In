"""API server runner tests."""

from unittest.mock import patch

from flyin.adapters.api.runner import main


def test_api_runner_passes_options_to_uvicorn() -> None:
    """Typed server options are forwarded to Uvicorn."""
    with patch("uvicorn.run") as uvicorn_run:
        result = main(
            (
                "--host",
                "0.0.0.0",
                "--port",
                "9000",
                "--reload",
            )
        )

    assert result == 0
    uvicorn_run.assert_called_once_with(
        "flyin.adapters.api.app:create_app",
        factory=True,
        host="0.0.0.0",
        port=9000,
        reload=True,
    )


def test_api_runner_rejects_invalid_port() -> None:
    """Argparse rejects ports that are not integers."""
    assert main(("--port", "invalid")) == 2
