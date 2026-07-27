from flyin.domain import Connection, ParsedMap, Zone, ZoneType
from flyin.parsing import MapParser
from flyin.pathfinding import AStarPathfinder, Route
from flyin.simulation import (
    MovementFact,
    ScheduleValidator,
    TransitFact,
    format_turn,
    simulate_known_routes,
)


def _parse(source: tuple[str, ...]) -> ParsedMap:
    return MapParser().parse("\n".join(source))


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


def _single_route(parsed_map: ParsedMap) -> Route:
    return AStarPathfinder.shortest_path(parsed_map)


def test_valid_known_multi_drone_schedule_validates_and_formats() -> None:
    parsed_map = _parse(
        (
            "nb_drones: 2",
            "start_hub: start 0 0",
            "hub: left 1 0",
            "hub: right 1 1",
            "end_hub: end 2 0",
            "connection: start-left",
            "connection: left-end",
            "connection: start-right",
            "connection: right-end",
        )
    )
    start = _zone(parsed_map, "start")
    left = _zone(parsed_map, "left")
    right = _zone(parsed_map, "right")
    end = _zone(parsed_map, "end")
    turns = (
        (
            MovementFact(1, start, left),
            MovementFact(2, start, right),
        ),
        (
            MovementFact(1, left, end),
            MovementFact(2, right, end),
        ),
    )

    result = ScheduleValidator.validate(parsed_map, turns)

    assert result.is_valid
    assert result.errors == ()
    assert tuple(format_turn(turn) for turn in turns) == (
        "D1-left D2-right",
        "D1-end D2-end",
    )


def test_validator_rejects_non_adjacent_move() -> None:
    parsed_map = _parse(
        (
            "nb_drones: 1",
            "start_hub: start 0 0",
            "hub: middle 1 0",
            "end_hub: end 2 0",
            "connection: start-middle",
            "connection: middle-end",
        )
    )

    result = ScheduleValidator.validate(
        parsed_map,
        (
            (
                MovementFact(
                    1,
                    _zone(parsed_map, "start"),
                    _zone(parsed_map, "end"),
                ),
            ),
        ),
    )

    assert not result.is_valid
    assert result.errors[0].code == "ILLEGAL_MOVE"
    assert result.errors[0].turn == 1
    assert result.errors[0].drone_id == 1


def test_validator_rejects_blocked_destination() -> None:
    parsed_map = _parse(
        (
            "nb_drones: 1",
            "start_hub: start 0 0",
            "hub: blocked 1 0 [zone=blocked]",
            "end_hub: end 2 0",
            "connection: start-blocked",
            "connection: blocked-end",
        )
    )

    result = ScheduleValidator.validate(
        parsed_map,
        (
            (
                MovementFact(
                    1,
                    _zone(parsed_map, "start"),
                    _zone(parsed_map, "blocked"),
                ),
            ),
        ),
    )

    assert not result.is_valid
    assert result.errors[0].code == "BLOCKED_DESTINATION"


def test_validator_rejects_zone_capacity_overflow() -> None:
    parsed_map = _parse(
        (
            "nb_drones: 2",
            "start_hub: start 0 0",
            "hub: middle 1 0",
            "end_hub: end 2 0",
            "connection: start-middle [max_link_capacity=2]",
            "connection: middle-end",
        )
    )

    start = _zone(parsed_map, "start")
    middle = _zone(parsed_map, "middle")

    result = ScheduleValidator.validate(
        parsed_map,
        (
            (
                MovementFact(1, start, middle),
                MovementFact(2, start, middle),
            ),
        ),
    )

    assert not result.is_valid
    assert result.errors[0].code == "ZONE_CAPACITY_EXCEEDED"
    assert result.errors[0].zone_name == "middle"


def test_validator_rejects_link_capacity_overflow() -> None:
    parsed_map = _parse(
        (
            "nb_drones: 2",
            "start_hub: start 0 0",
            "hub: middle 1 0 [max_drones=2]",
            "end_hub: end 2 0",
            "connection: start-middle",
            "connection: middle-end",
        )
    )

    start = _zone(parsed_map, "start")
    middle = _zone(parsed_map, "middle")

    result = ScheduleValidator.validate(
        parsed_map,
        (
            (
                MovementFact(1, start, middle),
                MovementFact(2, start, middle),
            ),
        ),
    )

    assert not result.is_valid
    assert result.errors[0].code == "LINK_CAPACITY_EXCEEDED"
    assert result.errors[0].connection_identity == ("middle", "start")


def test_validator_rejects_missing_restricted_arrival() -> None:
    parsed_map = _parse(
        (
            "nb_drones: 1",
            "start_hub: start 0 0",
            "hub: restricted 1 0 [zone=restricted]",
            "end_hub: end 2 0",
            "connection: start-restricted",
            "connection: restricted-end",
        )
    )
    restricted = _zone(parsed_map, "restricted")

    result = ScheduleValidator.validate(
        parsed_map,
        (
            (
                TransitFact(
                    1,
                    _connection(parsed_map, "start", "restricted"),
                    _zone(parsed_map, "start"),
                    restricted,
                ),
            ),
            (),
        ),
    )

    assert not result.is_valid
    assert result.errors[0].code == "MISSING_RESTRICTED_ARRIVAL"
    assert result.errors[0].turn == 2
    assert result.errors[0].drone_id == 1


def test_validator_uses_map_zone_type_not_fact_zone_object() -> None:
    parsed_map = _parse(
        (
            "nb_drones: 1",
            "start_hub: start 0 0",
            "hub: restricted 1 0 [zone=restricted]",
            "end_hub: end 2 0",
            "connection: start-restricted",
            "connection: restricted-end",
        )
    )
    spoofed_restricted = Zone("restricted", 1, 0, zone_type=ZoneType.NORMAL)

    result = ScheduleValidator.validate(
        parsed_map,
        ((MovementFact(1, _zone(parsed_map, "start"), spoofed_restricted),),),
    )

    assert not result.is_valid
    assert result.errors[0].code == "RESTRICTED_REQUIRES_TRANSIT"


def test_validator_checks_restricted_arrival_origin() -> None:
    parsed_map = _parse(
        (
            "nb_drones: 1",
            "start_hub: start 0 0",
            "hub: decoy 0 1",
            "hub: restricted 1 0 [zone=restricted]",
            "end_hub: end 2 0",
            "connection: start-restricted",
            "connection: restricted-end",
            "connection: decoy-restricted",
        )
    )
    restricted = _zone(parsed_map, "restricted")

    result = ScheduleValidator.validate(
        parsed_map,
        (
            (
                TransitFact(
                    1,
                    _connection(parsed_map, "start", "restricted"),
                    _zone(parsed_map, "start"),
                    restricted,
                ),
            ),
            (
                MovementFact(
                    1,
                    _zone(parsed_map, "decoy"),
                    restricted,
                ),
            ),
        ),
    )

    assert not result.is_valid
    assert result.errors[0].code == "MISSING_RESTRICTED_ARRIVAL"


def test_known_restricted_route_stdout_lines_validate_and_deliver() -> None:
    parsed_map = _parse(
        (
            "nb_drones: 1",
            "start_hub: start 0 0",
            "hub: restricted 1 0 [zone=restricted]",
            "end_hub: end 2 0",
            "connection: start-restricted",
            "connection: restricted-end",
        )
    )
    route = _single_route(parsed_map)

    lines = simulate_known_routes(parsed_map, {1: route})

    assert lines == (
        "D1-start-restricted",
        "D1-restricted",
        "D1-end",
    )
