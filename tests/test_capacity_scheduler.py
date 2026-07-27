from flyin.parsing import MapParser
from flyin.pathfinding import AStarPathfinder
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
