"""Print deterministic Fly-In map benchmark results."""

import argparse
from pathlib import Path

from flyin.benchmarking import (
    DEFAULT_MAPS_ROOT,
    collect_benchmarks,
    format_markdown,
)


def main() -> int:
    """Print a benchmark table for the supplied map suite."""
    parser = argparse.ArgumentParser(
        description="Benchmark Fly-In maps with the current scheduler.",
    )
    parser.add_argument(
        "--maps-root",
        type=Path,
        default=DEFAULT_MAPS_ROOT,
        help="Directory containing category subdirectories with map files.",
    )
    parser.add_argument("--max-routes", type=int, default=8)
    parser.add_argument("--max-turns", type=int, default=1000)
    args = parser.parse_args()
    results = collect_benchmarks(
        args.maps_root,
        max_routes=args.max_routes,
        max_turns=args.max_turns,
    )
    print(format_markdown(results))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
