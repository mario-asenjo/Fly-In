from pytest import MonkeyPatch

from flyin.domain import Connection, Zone
from flyin.parsing import MapParser
from flyin.pathfinding import CandidateRouteFinder
from flyin.pathfinding.astar import Route


def _dense_layered_map(layer_count: int, layer_width: int) -> str:
    lines = ["nb_drones: 12", "start_hub: start 0 0"]
    for layer in range(layer_count):
        for index in range(layer_width):
            lines.append(f"hub: l{layer}_{index} {layer + 1} {index}")
    lines.append(f"end_hub: end {layer_count + 1} 0")
    for index in range(layer_width):
        lines.append(f"connection: start-l0_{index}")
    for layer in range(layer_count - 1):
        for left in range(layer_width):
            for right in range(layer_width):
                lines.append(
                    f"connection: l{layer}_{left}-l{layer + 1}_{right}"
                )
    for index in range(layer_width):
        lines.append(f"connection: l{layer_count - 1}_{index}-end")
    return "\n".join(lines)


def test_candidate_routes_include_bounded_deterministic_forks() -> None:
    parsed_map = MapParser().parse(
        "\n".join(
            (
                "nb_drones: 1",
                "start_hub: start 0 0",
                "hub: alpha 1 0",
                "hub: beta 1 1",
                "hub: dead 1 2",
                "hub: blocked 1 3 [zone=blocked]",
                "end_hub: end 2 0",
                "connection: start-beta",
                "connection: beta-end",
                "connection: start-dead",
                "connection: start-blocked",
                "connection: blocked-end",
                "connection: start-alpha",
                "connection: alpha-end",
            )
        )
    )

    candidates = CandidateRouteFinder.find_candidates(parsed_map, max_routes=3)

    assert tuple(route.zone_names for route in candidates) == (
        ("start", "alpha", "end"),
        ("start", "beta", "end"),
    )
    assert candidates[0].zone_names == ("start", "alpha", "end")


def test_candidate_routes_can_limit_without_losing_default() -> None:
    parsed_map = MapParser().parse(
        "\n".join(
            (
                "nb_drones: 1",
                "start_hub: start 0 0",
                "hub: alpha 1 0",
                "hub: beta 1 1",
                "end_hub: end 2 0",
                "connection: start-beta",
                "connection: beta-end",
                "connection: start-alpha",
                "connection: alpha-end",
            )
        )
    )

    candidates = CandidateRouteFinder.find_candidates(parsed_map, max_routes=1)

    assert tuple(route.zone_names for route in candidates) == (
        ("start", "alpha", "end"),
    )


def test_candidate_route_search_stops_after_bounded_results(
    monkeypatch: MonkeyPatch,
) -> None:
    parsed_map = MapParser().parse(_dense_layered_map(3, 3))
    route_calls = 0
    original_route = CandidateRouteFinder._route

    def counted_route(
        zones: tuple[Zone, ...],
        connections: tuple[Connection, ...],
    ) -> Route:
        nonlocal route_calls
        route_calls += 1
        return original_route(zones, connections)

    monkeypatch.setattr(CandidateRouteFinder, "_route", counted_route)

    candidates = CandidateRouteFinder.find_candidates(parsed_map, max_routes=8)

    assert len(candidates) == 8
    assert route_calls <= 8
