"""Uvicorn runner used by the Fly-In launcher."""

import sys
import argparse
from typing import Sequence


def main(argv: Sequence[str] | None = None) -> int:
    """Parse API server options and run the FastAPI application."""

    parser = argparse.ArgumentParser(
        prog="flyin api",
        description="Solve a Fly-In map and print evaluator movement lines.",
    )
    parser.add_argument(
        "--host",
        help="interface on which the API server listens.",
        default="127.0.0.1"
    )
    parser.add_argument(
        "--port",
        type=int,
        help="TCP port on which the API server listens.",
        default=8000
    )
    parser.add_argument(
        "--reload",
        action="store_true",
        help="reload the server when source files change.",
        default=False
    )

    try:
        parsed_args = parser.parse_args(argv)
    except SystemExit as exc:
        return exc.code if isinstance(exc.code, int) else 2

    try:
        import uvicorn
    except ModuleNotFoundError:
        print(
            "API dependencies are not installed. "
            "Run: uv sync --extra api",
            file=sys.stderr
        )

    uvicorn.run(
        "flyin.adapters.api.app:create_app",
        factory=True,
        host=parsed_args.host,
        port=parsed_args.port,
        reload=parsed_args.reload
    )

    return 0
