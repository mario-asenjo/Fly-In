"""Benchmark helpers for deterministic Fly-In schedules."""

import hashlib
from dataclasses import dataclass
from pathlib import Path
from time import perf_counter

from flyin.parsing import MapParser
from flyin.scheduling import RouteAllocator
from flyin.simulation import ScheduleValidator

PROJECT_ROOT = Path(__file__).resolve().parents[3]
DEFAULT_MAPS_ROOT = PROJECT_ROOT / "maps" / "maps-v1.5-added-before-m0"


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
    source = source_bytes.decode("utf-8")
    map_hash = hashlib.sha256(source_bytes).hexdigest()
    start_time = perf_counter()
    parsed_map = MapParser().parse(source)
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


def format_markdown(results: tuple[BenchmarkResult, ...]) -> str:
    """Format benchmark results as a compact Markdown table."""
    lines = [
        "| Map | Drones | Turns | Valid | Duration ms | SHA-256 |",
        "| --- | ---: | ---: | --- | ---: | --- |",
    ]
    for result in results:
        valid = "Yes" if result.valid else "No"
        lines.append(
            f"| {result.map_path} | {result.drone_count} | "
            f"{result.turn_count} | {valid} | "
            f"{result.duration_ms:.2f} | {result.map_hash} |"
        )
    return "\n".join(lines)
