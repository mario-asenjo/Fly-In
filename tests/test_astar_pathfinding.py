from pathlib import Path

import pytest

from flyin.domain import ParsedMap
from flyin.parsing import MapParser
from flyin.pathfinding import AStarPathfinder, NoRouteError

PROJECT_ROOT = Path(__file__).parents[1]
OFFICIAL_MAPS = PROJECT_ROOT / "maps" / "maps-v1.5-added-before-m0"


def _parse(lines: tuple[str, ...]) -> ParsedMap:
    return MapParser().parse("\n".join(lines))


def test_astar_returns_weighted_route_and_matches_zero_heuristic() -> None:
    parsed_map = _parse(
        (
            "nb_drones: 1",
            "start_hub: start 0 0",
            "hub: restricted_a 1 0 [zone=restricted]",
            "hub: restricted_b 2 0 [zone=restricted]",
            "hub: normal_a 1 1",
            "hub: normal_b 2 1",
            "hub: normal_c 3 1",
            "end_hub: end 4 0",
            "connection: start-restricted_a",
            "connection: restricted_a-restricted_b",
            "connection: restricted_b-end",
            "connection: start-normal_a",
            "connection: normal_a-normal_b",
            "connection: normal_b-normal_c",
            "connection: normal_c-end",
        )
    )

    astar_route = AStarPathfinder.shortest_path(parsed_map)
    zero_route = AStarPathfinder.shortest_path(parsed_map, use_heuristic=False)

    assert astar_route.zone_names == (
        "start",
        "normal_a",
        "normal_b",
        "normal_c",
        "end",
    )
    assert astar_route.cost == 4
    assert astar_route.cost == zero_route.cost
    assert astar_route.zone_names == zero_route.zone_names
    assert len(astar_route.connections) == 4


def test_astar_reports_disconnected_route_before_scheduling() -> None:
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

    with pytest.raises(NoRouteError, match="start cannot reach end"):
        AStarPathfinder.shortest_path(parsed_map)


def test_astar_prefers_priority_only_for_equal_total_cost() -> None:
    parsed_map = _parse(
        (
            "nb_drones: 1",
            "start_hub: start 0 0",
            "hub: normal 1 0",
            "hub: priority 1 1 [zone=priority]",
            "hub: restricted 1 2 [zone=restricted]",
            "end_hub: end 2 0",
            "connection: start-normal",
            "connection: normal-end",
            "connection: start-priority",
            "connection: priority-end",
            "connection: start-restricted",
            "connection: restricted-end",
        )
    )

    first = AStarPathfinder.shortest_path(parsed_map)
    second = AStarPathfinder.shortest_path(parsed_map)

    assert first.zone_names == ("start", "priority", "end")
    assert first.cost == 2
    assert first.priority_score == 1
    assert first.zone_names == second.zone_names
    assert first.cost == second.cost
    assert first.priority_score == second.priority_score


def test_astar_does_not_let_priority_override_lower_cost() -> None:
    parsed_map = _parse(
        (
            "nb_drones: 1",
            "start_hub: start 0 0",
            "hub: normal 1 0",
            "hub: priority 1 1 [zone=priority]",
            "hub: restricted 2 1 [zone=restricted]",
            "end_hub: end 3 0",
            "connection: start-normal",
            "connection: normal-end",
            "connection: start-priority",
            "connection: priority-restricted",
            "connection: restricted-end",
        )
    )

    route = AStarPathfinder.shortest_path(parsed_map)

    assert route.zone_names == ("start", "normal", "end")
    assert route.cost == 2
    assert route.priority_score == 0


def test_astar_routes_the_actual_official_linear_map() -> None:
    source = (OFFICIAL_MAPS / "easy" / "01_linear_path.txt").read_text(
        encoding="utf-8"
    )
    parsed_map = MapParser().parse(source)

    route = AStarPathfinder.shortest_path(parsed_map)

    assert route.zone_names == (
        "start",
        "waypoint1",
        "waypoint2",
        "goal",
    )
    assert route.cost == 3
