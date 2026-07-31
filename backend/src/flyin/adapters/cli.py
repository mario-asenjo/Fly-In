"""Command-line adapter for Fly-In."""

import argparse
import sys
from pathlib import Path
from typing import Sequence, TextIO

from flyin.adapters.files import FileReader, MapCatalog, MapFileOption
from flyin.application import FlyInSolver, SolveError
from flyin.adapters.terminal_visual import (
    format_capacity_info,
    format_visual_result,
)


def main(
    argv: Sequence[str] | None = None,
    stdout: TextIO | None = None,
    stderr: TextIO | None = None,
    stdin: TextIO | None = None,
) -> int:
    """Run the evaluator-safe CLI adapter."""
    out = sys.stdout if stdout is None else stdout
    err = sys.stderr if stderr is None else stderr
    input_stream = sys.stdin if stdin is None else stdin
    parser = argparse.ArgumentParser(
        prog="flyin",
        description="Solve a Fly-In map and print evaluator movement lines.",
    )
    parser.add_argument(
        "map_path",
        nargs="?",
        help="path to a Fly-In map text file",
    )
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

    selected_map = (
        _prompt_for_map(input_stream, out, err)
        if args.map_path is None
        else MapFileOption(0, Path(args.map_path), args.map_path)
    )
    if selected_map is None:
        return 2

    try:
        source = FileReader(selected_map.path).retrieve_text()
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


def _default_map_root() -> Path:
    """Return the repository map folder for interactive runs."""
    return Path(__file__).parents[4] / "maps"


def _prompt_for_map(
    input_stream: TextIO,
    out: TextIO,
    err: TextIO,
) -> MapFileOption | None:
    """Let a human choose a known map before solving."""
    catalog = MapCatalog(_default_map_root())
    options = catalog.available_maps()
    if not options:
        print(
            f"INPUT_ERROR: no .txt maps found under {catalog.root}",
            file=err,
        )
        return None

    print("Available maps:", file=out)
    for option in options:
        print(f"{option.index}. {option.display_path}", file=out)
    print("Choose map number: ", end="", file=out, flush=True)

    raw_selection = input_stream.readline().strip()
    try:
        selected_index = int(raw_selection)
    except ValueError:
        print(
            f"INPUT_ERROR: invalid map selection '{raw_selection}'",
            file=err,
        )
        return None

    selected = catalog.option_for_index(selected_index)
    if selected is None:
        print(
            f"INPUT_ERROR: map selection {selected_index} is out of range",
            file=err,
        )
        return None
    return selected
