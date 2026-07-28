"""Print deterministic Fly-In map benchmark results."""

import argparse
import csv
import hashlib
import io
from dataclasses import dataclass
from pathlib import Path
from time import perf_counter

from flyin.parsing import MapParser
from flyin.scheduling import RouteAllocator
from flyin.simulation import ScheduleValidator

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_MAPS_ROOT = PROJECT_ROOT / "maps" / "maps-v1.5-added-before-m0"
BenchmarkRecord = dict[str, str | int | float | bool]


@dataclass(frozen=True, slots=True)
class BenchmarkResult:
    """A measured schedule result for one map file."""

    map_path: str
    drone_count: int
    turn_count: int
    valid: bool
    duration_ms: float
    map_hash: str


def collect_benchmarks(
    maps_root: Path = DEFAULT_MAPS_ROOT,
    max_routes: int = 8,
    max_turns: int = 1000,
) -> tuple[BenchmarkResult, ...]:
    """Benchmark every map under the supplied suite root."""
    return tuple(
        benchmark_map(map_path, maps_root, max_routes, max_turns)
        for map_path in sorted(maps_root.glob("*/*.txt"))
    )


def benchmark_map(
    map_path: Path,
    maps_root: Path = DEFAULT_MAPS_ROOT,
    max_routes: int = 8,
    max_turns: int = 1000,
) -> BenchmarkResult:
    """Parse, schedule, validate, and time one map."""
    source_bytes = map_path.read_bytes()
    map_hash = hashlib.sha256(source_bytes).hexdigest()
    start_time = perf_counter()
    parsed_map = MapParser().parse(source_bytes.decode("utf-8"))
    schedule = RouteAllocator.schedule(
        parsed_map,
        max_routes=max_routes,
        max_turns=max_turns,
    )
    validation = ScheduleValidator.validate(parsed_map, schedule)
    duration_ms = (perf_counter() - start_time) * 1000
    return BenchmarkResult(
        map_path=map_path.relative_to(maps_root).as_posix(),
        drone_count=parsed_map.drone_count,
        turn_count=len(schedule),
        valid=validation.is_valid,
        duration_ms=duration_ms,
        map_hash=map_hash,
    )


def to_records(
    results: tuple[BenchmarkResult, ...],
) -> tuple[BenchmarkRecord, ...]:
    """Convert measured results to plain records for any renderer."""
    return tuple(
        {
            "map": result.map_path,
            "drones": result.drone_count,
            "turns": result.turn_count,
            "valid": result.valid,
            "duration_ms": round(result.duration_ms, 2),
            "sha256": result.map_hash,
        }
        for result in results
    )


def format_csv(records: tuple[BenchmarkRecord, ...]) -> str:
    """Format benchmark records as CSV for docs, CI, or notebooks."""
    output = io.StringIO()
    fieldnames = ("map", "drones", "turns", "valid", "duration_ms", "sha256")
    writer = csv.DictWriter(output, fieldnames=fieldnames, lineterminator="\n")
    writer.writeheader()
    writer.writerows(records)
    return output.getvalue().rstrip("\n")


def main(argv: list[str] | None = None) -> int:
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
    args = parser.parse_args(argv)
    results = collect_benchmarks(
        args.maps_root,
        max_routes=args.max_routes,
        max_turns=args.max_turns,
    )
    print(format_csv(to_records(results)))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
