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
