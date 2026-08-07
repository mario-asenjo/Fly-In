"""Top-level launcher dispatch tests."""

from unittest.mock import patch

from flyin import launcher


def test_launcher_preserves_implicit_cli_mode() -> None:
    """Arguments without a mode continue to use the CLI."""
    with patch.object(
        launcher,
        "cli_main",
        return_value=7,
    ) as cli_main:
        result = launcher.main(("map.txt",))

    assert result == 7
    cli_main.assert_called_once_with(["map.txt"])


def test_launcher_dispatches_explicit_cli_mode() -> None:
    """The cli subcommand is removed before delegation."""
    with patch.object(
        launcher,
        "cli_main",
        return_value=0,
    ) as cli_main:
        result = launcher.main(("cli", "map.txt"))

    assert result == 0
    cli_main.assert_called_once_with(["map.txt"])


def test_launcher_dispatches_api_mode() -> None:
    """The api subcommand is removed before delegation."""
    with patch.object(
        launcher,
        "api_main",
        return_value=0,
    ) as api_main:
        result = launcher.main(
            ("api", "--port", "9000")
        )

    assert result == 0
    api_main.assert_called_once_with(
        ["--port", "9000"]
    )
