from pathlib import Path
import importlib.util
from types import ModuleType

PROJECT_ROOT = Path(__file__).parents[1]
SCRIPT_PATH = PROJECT_ROOT / "scripts" / "benchmark_official_maps.py"
OFFICIAL_MAPS = PROJECT_ROOT / "maps" / "maps-v1.5-added-before-m0"


def _benchmark_module() -> ModuleType:
    spec = importlib.util.spec_from_file_location(
        "benchmark_official_maps",
        SCRIPT_PATH,
    )
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_benchmark_runner_covers_every_official_map() -> None:
    module = _benchmark_module()
    expected_paths = tuple(
        path.relative_to(OFFICIAL_MAPS).as_posix()
        for path in sorted(OFFICIAL_MAPS.glob("*/*.txt"))
    )

    results = module.collect_benchmarks(OFFICIAL_MAPS)

    assert tuple(result.map_path for result in results) == expected_paths
    assert all(result.valid for result in results)
    assert all(result.drone_count > 0 for result in results)
    assert all(result.turn_count > 0 for result in results)
    assert all(len(result.map_hash) == 64 for result in results)


def test_benchmark_data_can_be_serialized_without_app_coupling() -> None:
    module = _benchmark_module()
    rows = (
        module.BenchmarkResult(
            map_path="easy/example.txt",
            drone_count=2,
            turn_count=4,
            valid=True,
            duration_ms=1.25,
            map_hash="a" * 64,
        ),
    )

    records = module.to_records(rows)
    output = module.format_csv(records)

    assert records == (
        {
            "map": "easy/example.txt",
            "drones": 2,
            "turns": 4,
            "valid": True,
            "duration_ms": 1.25,
            "sha256": "a" * 64,
        },
    )
    assert tuple(output.splitlines()) == (
        "map,drones,turns,valid,duration_ms,sha256",
        "easy/example.txt,2,4,True,1.25," + "a" * 64,
    )
