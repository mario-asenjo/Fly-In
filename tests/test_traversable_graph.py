import pytest

from flyin.domain import ParsedMap
from flyin.parsing import MapParser
from flyin.pathfinding import (
    NoRouteError,
    ReverseHopDistances,
    TraversableGraph,
)


def _parse(lines: tuple[str, ...]) -> ParsedMap:
    return MapParser().parse("\n".join(lines))


def test_builds_bidirectional_traversable_adjacency() -> None:
    parsed_map = _parse(
        (
            "nb_drones: 1",
            "start_hub: start 0 0",
            "hub: alpha 1 0",
            "end_hub: end 2 0",
            "connection: start-alpha",
            "connection: alpha-end",
        )
    )

    graph = TraversableGraph.from_parsed_map(parsed_map)
    first, second = parsed_map.connections

    assert graph.neighbor_names(parsed_map.start) == ("alpha",)
    assert graph.neighbor_names(parsed_map.hubs[0]) == ("end", "start")
    assert graph.neighbor_names(parsed_map.end) == ("alpha",)
    alpha = parsed_map.hubs[0]

    assert graph.connection_between(parsed_map.start, alpha) is first
    assert graph.connection_between(alpha, parsed_map.start) is first
    assert graph.connection_between(alpha, parsed_map.end) is second


def test_excludes_blocked_zones_from_traversable_adjacency() -> None:
    parsed_map = _parse(
        (
            "nb_drones: 1",
            "start_hub: start 0 0",
            "hub: blocked 1 0 [zone=blocked]",
            "hub: safe 1 1",
            "end_hub: end 2 0",
            "connection: start-blocked",
            "connection: blocked-end",
            "connection: start-safe",
            "connection: safe-end",
        )
    )

    graph = TraversableGraph.from_parsed_map(parsed_map)

    assert parsed_map.hubs[0].name == "blocked"
    assert graph.neighbor_names(parsed_map.start) == ("safe",)
    assert graph.neighbor_names(parsed_map.hubs[0]) == ()
    blocked = parsed_map.hubs[0]

    assert graph.connection_between(parsed_map.start, blocked) is None


def test_reverse_hops_prove_reachability_to_end() -> None:
    parsed_map = _parse(
        (
            "nb_drones: 1",
            "start_hub: start 0 0",
            "hub: alpha 1 0",
            "hub: beta 2 0",
            "end_hub: end 3 0",
            "connection: start-alpha",
            "connection: alpha-beta",
            "connection: beta-end",
        )
    )

    graph = TraversableGraph.from_parsed_map(parsed_map)
    hops = ReverseHopDistances.to_end(graph, parsed_map.end)

    assert hops.can_reach_end(parsed_map.start)
    assert hops.hops_from(parsed_map.start) == 3
    assert hops.hops_from(parsed_map.hubs[0]) == 2
    assert hops.hops_from(parsed_map.hubs[1]) == 1
    assert hops.hops_from(parsed_map.end) == 0


def test_reverse_hops_report_blocked_and_dead_end_no_route() -> None:
    parsed_map = _parse(
        (
            "nb_drones: 1",
            "start_hub: start 0 0",
            "hub: blocked 1 0 [zone=blocked]",
            "hub: dead 5 0",
            "end_hub: end 2 0",
            "connection: start-blocked",
            "connection: blocked-end",
            "connection: start-dead",
        )
    )

    graph = TraversableGraph.from_parsed_map(parsed_map)
    hops = ReverseHopDistances.to_end(graph, parsed_map.end)

    assert not hops.can_reach_end(parsed_map.start)
    assert not hops.can_reach_end(parsed_map.hubs[0])
    assert not hops.can_reach_end(parsed_map.hubs[1])
    with pytest.raises(NoRouteError, match="start cannot reach end"):
        hops.hops_from(parsed_map.start)
