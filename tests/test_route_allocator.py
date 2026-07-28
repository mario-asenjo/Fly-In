from pathlib import Path

import pytest

from flyin.parsing import MapParser
from flyin.pathfinding import NoRouteError
from flyin.scheduling import RouteAllocator
from flyin.simulation import ScheduleValidator, format_turn


def _allocated_lines(source: tuple[str, ...]) -> tuple[str, ...]:
    parsed_map = MapParser().parse("\n".join(source))
    schedule = RouteAllocator.schedule(parsed_map)
    validation = ScheduleValidator.validate(parsed_map, schedule)

    assert validation.is_valid, validation.errors
    return tuple(format_turn(turn) for turn in schedule)


def test_route_allocator_splits_drones_across_two_beneficial_paths() -> None:
    lines = _allocated_lines(
        (
            "nb_drones: 4",
            "start_hub: start 0 0",
            "hub: alpha 1 0",
            "hub: beta 1 1",
            "end_hub: end 2 0",
            "connection: start-alpha",
            "connection: alpha-end",
            "connection: start-beta",
            "connection: beta-end",
        )
    )

    assert lines == (
        "D1-alpha D2-beta",
        "D1-end D2-end D3-alpha D4-beta",
        "D3-end D4-end",
    )


def test_route_allocator_waits_for_single_route_bottleneck() -> None:
    lines = _allocated_lines(
        (
            "nb_drones: 3",
            "start_hub: start 0 0",
            "hub: middle 1 0",
            "end_hub: end 2 0",
            "connection: start-middle",
            "connection: middle-end",
        )
    )

    assert lines == (
        "D1-middle",
        "D1-end D2-middle",
        "D2-end D3-middle",
        "D3-end",
    )


def test_route_allocator_reports_unsolvable_maps() -> None:
    parsed_map = MapParser().parse(
        "\n".join(
            (
                "nb_drones: 1",
                "start_hub: start 0 0",
                "hub: blocked 1 0 [zone=blocked]",
                "end_hub: end 2 0",
                "connection: start-blocked",
                "connection: blocked-end",
            )
        )
    )

    with pytest.raises(NoRouteError, match="start cannot reach end"):
        RouteAllocator.schedule(parsed_map)


def test_route_allocator_uses_shortest_valid_candidate_window() -> None:
    project_root = Path(__file__).parents[1]
    map_path = (
        project_root
        / "maps"
        / "maps-v1.5-added-before-m0"
        / "challenger"
        / "01_the_impossible_dream.txt"
    )
    parsed_map = MapParser().parse(map_path.read_text())

    schedule = RouteAllocator.schedule(parsed_map, max_routes=8)
    validation = ScheduleValidator.validate(parsed_map, schedule)

    assert validation.is_valid, validation.errors
    assert len(schedule) == 43
