"""Command-line adapter for Fly-In."""

import argparse
import sys
from pathlib import Path
from typing import Sequence, TextIO

from flyin.application import FlyInSolver, SolveError
from flyin.adapters.terminal_visual import (
    format_capacity_info,
    format_visual_result,
)


def main(
    argv: Sequence[str] | None = None,
    stdout: TextIO | None = None,
    stderr: TextIO | None = None,
) -> int:
    """Run the evaluator-safe CLI adapter."""
    out = sys.stdout if stdout is None else stdout
    err = sys.stderr if stderr is None else stderr
    parser = argparse.ArgumentParser(
        prog="flyin",
        description="Solve a Fly-In map and print evaluator movement lines.",
    )
    parser.add_argument("map_path", help="path to a Fly-In map text file")
    parser.add_argument(
        "--visual",
        action="store_true",
        help="print colored human visualization instead of evaluator output",
    )
    parser.add_argument(
        "--capacity-info",
        action="store_true",
        help="append per-turn capacity diagnostics to explicit debug output",
    )
    try:
        args = parser.parse_args(argv)
    except SystemExit as exc:
        return exc.code if isinstance(exc.code, int) else 2

    path = Path(args.map_path)
    try:
        source = path.read_text(encoding="utf-8")
    except OSError as exc:
        print(f"INPUT_ERROR: {exc}", file=err)
        return 2

    try:
        result = FlyInSolver.solve_text(source)
    except SolveError as exc:
        if exc.line is None:
            print(f"{exc.code}: {exc.message}", file=err)
        else:
            print(f"{exc.code}: line {exc.line}: {exc.message}", file=err)
        if exc.code == "NO_ROUTE":
            return 3
        return 2

    output_lines = list(
        format_visual_result(result) if args.visual else result.movement_lines
    )
    if args.capacity_info:
        output_lines.extend(format_capacity_info(result))
    for line in output_lines:
        print(line, file=out)
    return 0
