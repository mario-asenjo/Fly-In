from pathlib import Path

from flyin.benchmarking import (
    BenchmarkResult,
    collect_benchmarks,
    format_markdown,
)

PROJECT_ROOT = Path(__file__).parents[1]
OFFICIAL_MAPS = PROJECT_ROOT / "maps" / "maps-v1.5-added-before-m0"


def test_benchmark_runner_covers_every_official_map() -> None:
    expected_paths = tuple(
        path.relative_to(OFFICIAL_MAPS).as_posix()
        for path in sorted(OFFICIAL_MAPS.glob("*/*.txt"))
    )

    results = collect_benchmarks(OFFICIAL_MAPS)

    assert tuple(result.map_path for result in results) == expected_paths
    assert all(result.valid for result in results)
    assert all(result.drone_count > 0 for result in results)
    assert all(result.turn_count > 0 for result in results)
    assert all(len(result.map_hash) == 64 for result in results)


def test_benchmark_markdown_contains_required_columns() -> None:
    rows = (
        BenchmarkResult(
            map_path="easy/example.txt",
            drone_count=2,
            turn_count=4,
            valid=True,
            duration_ms=1.25,
            map_hash="a" * 64,
        ),
    )

    markdown = format_markdown(rows)

    assert (
        "| Map | Drones | Turns | Valid | Duration ms | SHA-256 |"
        in markdown
    )
    assert "| easy/example.txt | 2 | 4 | Yes | 1.25 | " in markdown
