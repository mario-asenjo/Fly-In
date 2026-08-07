"""Dispatch Fly-In commands to the selected external adapter."""

import sys
from typing import Sequence

from flyin.adapters.cli import main as cli_main
from flyin.adapters.api.runner import main as api_main

def main(
    argv: Sequence[str] | None = None
) -> int:
    """Dispatch modes while preserving the historical CLI syntax."""

    argv = list(sys.argv[1:] if argv is None else argv)

    if argv and argv[0] == "cli":
        return cli_main(argv[1:])
    if argv and argv[0] == "api":
        return api_main(argv[1:])

    return cli_main(argv)
