from flyin.parsing import MapParser
from flyin.pathfinding import CandidateRouteFinder


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
