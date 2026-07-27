from flyin.domain import Connection, ParsedMap, Zone
from flyin.parsing import MapParser
from flyin.pathfinding import AStarPathfinder, Route
from flyin.scheduling import KnownRouteScheduler
from flyin.simulation import ScheduleValidator, format_turn


def _turn_lines(source: tuple[str, ...]) -> tuple[str, ...]:
    parsed_map = MapParser().parse("\n".join(source))
    route = AStarPathfinder.shortest_path(parsed_map)
    schedule = KnownRouteScheduler.schedule_known_routes(
        parsed_map,
        {
            drone_id: route
            for drone_id in range(1, parsed_map.drone_count + 1)
        },
    )

    validation = ScheduleValidator.validate(parsed_map, schedule)

    assert validation.is_valid, validation.errors
    return tuple(format_turn(turn) for turn in schedule)


def _scheduled_lines(
    source: tuple[str, ...],
    route_names_by_drone_id: dict[int, tuple[str, ...]],
) -> tuple[str, ...]:
    parsed_map = MapParser().parse("\n".join(source))
    routes = {
        drone_id: _route(parsed_map, zone_names)
        for drone_id, zone_names in route_names_by_drone_id.items()
    }
    schedule = KnownRouteScheduler.schedule_known_routes(parsed_map, routes)
    validation = ScheduleValidator.validate(parsed_map, schedule)

    assert validation.is_valid, validation.errors
    return tuple(format_turn(turn) for turn in schedule)


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


def test_scheduler_queues_default_single_capacity_zone() -> None:
    lines = _turn_lines(
        (
            "nb_drones: 2",
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
        "D2-end",
    )


def test_scheduler_allows_same_turn_release_before_incoming_drone() -> None:
    lines = _turn_lines(
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


def test_scheduler_respects_explicit_zone_capacity_above_one() -> None:
    lines = _turn_lines(
        (
            "nb_drones: 3",
            "start_hub: start 0 0",
            "hub: middle 1 0 [max_drones=2]",
            "end_hub: end 2 0",
            "connection: start-middle [max_link_capacity=2]",
            "connection: middle-end [max_link_capacity=2]",
        )
    )

    assert lines == (
        "D1-middle D2-middle",
        "D1-end D2-end D3-middle",
        "D3-end",
    )


def test_scheduler_queues_default_link_capacity_with_roomy_zone() -> None:
    lines = _turn_lines(
        (
            "nb_drones: 2",
            "start_hub: start 0 0",
            "hub: middle 1 0 [max_drones=2]",
            "end_hub: end 2 0",
            "connection: start-middle",
            "connection: middle-end [max_link_capacity=2]",
        )
    )

    assert lines == (
        "D1-middle",
        "D1-end D2-middle",
        "D2-end",
    )


def test_scheduler_shares_link_capacity_across_opposite_directions() -> None:
    lines = _scheduled_lines(
        (
            "nb_drones: 2",
            "start_hub: start 0 0",
            "hub: left 1 0 [max_drones=2]",
            "hub: right 1 1 [max_drones=2]",
            "end_hub: end 2 0",
            "connection: start-left [max_link_capacity=2]",
            "connection: start-right [max_link_capacity=2]",
            "connection: left-right",
            "connection: left-end [max_link_capacity=2]",
            "connection: right-end [max_link_capacity=2]",
        ),
        {
            1: ("start", "left", "right", "end"),
            2: ("start", "right", "left", "end"),
        },
    )

    assert lines == (
        "D1-left D2-right",
        "D1-right",
        "D1-end D2-left",
        "D2-end",
    )


def test_scheduler_reserves_restricted_arrival_capacity() -> None:
    lines = _turn_lines(
        (
            "nb_drones: 2",
            "start_hub: start 0 0",
            "hub: restricted 1 0 [zone=restricted]",
            "end_hub: end 2 0",
            "connection: start-restricted [max_link_capacity=2]",
            "connection: restricted-end [max_link_capacity=2]",
        )
    )

    assert lines == (
        "D1-start-restricted",
        "D1-restricted D2-start-restricted",
        "D1-end D2-restricted",
        "D2-end",
    )
