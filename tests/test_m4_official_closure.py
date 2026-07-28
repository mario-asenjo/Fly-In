from pathlib import Path

import pytest

from flyin.domain import Connection, ParsedMap, Zone
from flyin.parsing import MapParser
from flyin.pathfinding import Route
from flyin.scheduling import (
    KnownRouteScheduler,
    RouteAllocator,
    ScheduleDeadlockError,
)
from flyin.simulation import ScheduleValidator

PROJECT_ROOT = Path(__file__).parents[1]
OFFICIAL_MAPS = PROJECT_ROOT / "maps" / "maps-v1.5-added-before-m0"


def _parse(lines: tuple[str, ...]) -> ParsedMap:
    return MapParser().parse("\n".join(lines))


def _route(parsed_map: ParsedMap, zone_names: tuple[str, ...]) -> Route:
    zones = tuple(_zone(parsed_map, name) for name in zone_names)
    connections = tuple(
        _connection(parsed_map, left, right)
        for left, right in zip(zone_names, zone_names[1:])
    )
    return Route(zones, connections, len(connections), 0)


def _zone(parsed_map: ParsedMap, name: str) -> Zone:
    for zone in (parsed_map.start, *parsed_map.hubs, parsed_map.end):
        if zone.name == name:
            return zone
    raise AssertionError(f"missing zone: {name}")


def _connection(
    parsed_map: ParsedMap,
    left_name: str,
    right_name: str,
) -> Connection:
    identity = tuple(sorted((left_name, right_name)))
    for connection in parsed_map.connections:
        if connection.identity == identity:
            return connection
    raise AssertionError(f"missing connection: {left_name}-{right_name}")


def test_known_route_scheduler_reports_deadlock_without_progress() -> None:
    parsed_map = _parse(
        (
            "nb_drones: 2",
            "start_hub: start 0 0",
            "hub: left 1 0",
            "hub: right 1 1",
            "end_hub: end 2 0",
            "connection: start-left [max_link_capacity=2]",
            "connection: start-right [max_link_capacity=2]",
            "connection: left-right",
            "connection: left-end",
            "connection: right-end",
        )
    )
    routes = {
        1: _route(parsed_map, ("start", "left", "right", "end")),
        2: _route(parsed_map, ("start", "right", "left", "end")),
    }

    with pytest.raises(ScheduleDeadlockError, match="made no progress"):
        KnownRouteScheduler.schedule_known_routes(parsed_map, routes)


def test_route_allocator_falls_back_from_deadlocking_window() -> None:
    parsed_map = MapParser().parse(
        (OFFICIAL_MAPS / "hard" / "02_capacity_hell.txt").read_text()
    )

    schedule = RouteAllocator.schedule(parsed_map, max_routes=8)
    validation = ScheduleValidator.validate(parsed_map, schedule)

    assert validation.is_valid, validation.errors
    assert len(schedule) == 16


@pytest.mark.parametrize("map_path", sorted(OFFICIAL_MAPS.glob("*/*.txt")))
def test_route_allocator_terminates_valid_schedule_for_official_map(
    map_path: Path,
) -> None:
    parsed_map = MapParser().parse(map_path.read_text())

    schedule = RouteAllocator.schedule(parsed_map, max_routes=8)
    validation = ScheduleValidator.validate(parsed_map, schedule)

    assert schedule
    assert validation.is_valid, (map_path, validation.errors)
