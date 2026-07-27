from flyin.domain import ParsedMap
from flyin.parsing import MapParser
from flyin.pathfinding import AStarPathfinder
from flyin.simulation import (
    AtZone,
    Delivered,
    MovementFact,
    SimulationEngine,
    SimulationState,
    format_turn,
)


def _parse(source: tuple[str, ...]) -> ParsedMap:
    return MapParser().parse("\n".join(source))


def test_initial_state_places_drones_at_start_with_stable_ids() -> None:
    parsed_map = _parse(
        (
            "nb_drones: 3",
            "start_hub: start 0 0",
            "end_hub: end 1 0",
            "connection: start-end",
        )
    )

    state = SimulationState.initial(parsed_map)

    assert state.turn == 0
    assert tuple(drone.identifier for drone in state.drones) == (1, 2, 3)
    assert all(isinstance(drone.location, AtZone) for drone in state.drones)
    assert tuple(
        drone.location.zone.name
        for drone in state.drones
        if isinstance(drone.location, AtZone)
    ) == ("start", "start", "start")


def test_normal_turn_is_atomic_and_orders_facts_by_drone_id() -> None:
    parsed_map = _parse(
        (
            "nb_drones: 2",
            "start_hub: start 0 0",
            "hub: first 1 0",
            "hub: second 1 1",
            "end_hub: end 2 0",
            "connection: start-first",
            "connection: first-end",
            "connection: start-second",
            "connection: second-end",
        )
    )
    first_route = AStarPathfinder.shortest_path(
        _parse(
            (
                "nb_drones: 1",
                "start_hub: start 0 0",
                "hub: first 1 0",
                "end_hub: end 2 0",
                "connection: start-first",
                "connection: first-end",
            )
        )
    )
    second_route = AStarPathfinder.shortest_path(
        _parse(
            (
                "nb_drones: 1",
                "start_hub: start 0 0",
                "hub: second 1 1",
                "end_hub: end 2 0",
                "connection: start-second",
                "connection: second-end",
            )
        )
    )
    initial = SimulationState.initial(parsed_map)

    result = SimulationEngine.advance_one_turn(
        initial,
        {2: second_route, 1: first_route},
    )

    assert initial.turn == 0
    assert tuple(
        drone.location.zone.name
        for drone in initial.drones
        if isinstance(drone.location, AtZone)
    ) == ("start", "start")
    assert result.state.turn == 1
    assert tuple(fact.drone_id for fact in result.facts) == (1, 2)
    assert tuple(fact.destination.name for fact in result.facts) == (
        "first",
        "second",
    )
    assert tuple(
        drone.location.zone.name
        for drone in result.state.drones
        if isinstance(drone.location, AtZone)
    ) == ("first", "second")


def test_priority_destination_advances_in_one_turn() -> None:
    parsed_map = _parse(
        (
            "nb_drones: 1",
            "start_hub: start 0 0",
            "hub: priority 1 0 [zone=priority]",
            "end_hub: end 2 0",
            "connection: start-priority",
            "connection: priority-end",
        )
    )
    route = AStarPathfinder.shortest_path(parsed_map)
    state = SimulationState.initial(parsed_map)

    result = SimulationEngine.advance_one_turn(state, {1: route})

    assert format_turn(result.facts) == "D1-priority"
    drone = result.state.drone_by_id(1)
    assert isinstance(drone.location, AtZone)
    assert drone.location.zone.name == "priority"


def test_delivered_drones_are_removed_from_future_turn_facts() -> None:
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
    route = AStarPathfinder.shortest_path(parsed_map)
    state = SimulationState.initial(parsed_map)

    first = SimulationEngine.advance_one_turn(state, {1: route})
    second = SimulationEngine.advance_one_turn(first.state, {1: route})
    third = SimulationEngine.advance_one_turn(second.state, {1: route})

    assert isinstance(second.state.drone_by_id(1).location, Delivered)
    assert format_turn(first.facts) == "D1-middle"
    assert format_turn(second.facts) == "D1-end"
    assert third.facts == ()
    assert format_turn(third.facts) == ""


def test_formatter_outputs_only_movement_tokens_in_drone_id_order() -> None:
    parsed_map = _parse(
        (
            "nb_drones: 2",
            "start_hub: start 0 0",
            "hub: first 1 0",
            "hub: second 1 1",
            "end_hub: end 2 0",
            "connection: start-first",
            "connection: first-end",
            "connection: start-second",
            "connection: second-end",
        )
    )
    first = parsed_map.hubs[0]
    second = parsed_map.hubs[1]
    facts = (
        MovementFact(2, parsed_map.start, second),
        MovementFact(1, parsed_map.start, first),
    )

    assert format_turn(facts) == "D1-first D2-second"
