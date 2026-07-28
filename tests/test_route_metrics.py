from pathlib import Path

from flyin.parsing import MapParser
from flyin.pathfinding import CandidateRouteFinder
from flyin.scheduling import FleetMakespanEstimator, RouteMetrics

PROJECT_ROOT = Path(__file__).parents[1]
OFFICIAL_MAPS = PROJECT_ROOT / "maps" / "maps-v1.5-added-before-m0"


def test_route_metrics_reports_cost_and_bottleneck() -> None:
    parsed_map = MapParser().parse(
        "\n".join(
            (
                "nb_drones: 1",
                "start_hub: start 0 0",
                "hub: wide 1 0 [max_drones=3]",
                "hub: slow 2 0 [zone=restricted max_drones=2]",
                "end_hub: end 3 0",
                "connection: start-wide [max_link_capacity=3]",
                "connection: wide-slow",
                "connection: slow-end [max_link_capacity=2]",
            )
        )
    )
    route = CandidateRouteFinder.find_candidates(parsed_map, max_routes=1)[0]

    metrics = RouteMetrics.from_route(route)

    assert metrics.zone_names == ("start", "wide", "slow", "end")
    assert metrics.cost == 4
    assert metrics.restricted_count == 1
    assert metrics.min_regular_zone_capacity == 2
    assert metrics.min_link_capacity == 1
    assert metrics.bottleneck == "connection:slow-wide"


def test_estimator_prefers_parallel_routes_without_shared_bottleneck() -> None:
    parsed_map = MapParser().parse(
        "\n".join(
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
    )
    candidates = CandidateRouteFinder.find_candidates(parsed_map, max_routes=2)

    estimates = FleetMakespanEstimator.estimate_windows(parsed_map, candidates)

    assert tuple(estimate.route_count for estimate in estimates) == (1, 2)
    assert estimates[1].estimated_turns < estimates[0].estimated_turns
    assert FleetMakespanEstimator.best_route_count(parsed_map, candidates) == 2


def test_estimator_avoids_routes_that_only_share_a_bottleneck() -> None:
    map_path = OFFICIAL_MAPS / "challenger" / "01_the_impossible_dream.txt"
    parsed_map = MapParser().parse(map_path.read_text())
    candidates = CandidateRouteFinder.find_candidates(parsed_map, max_routes=8)

    assert FleetMakespanEstimator.best_route_count(parsed_map, candidates) == 1
