"""Route allocation over bounded candidate paths."""

from flyin.domain import ParsedMap
from flyin.pathfinding import CandidateRouteFinder, Route
from flyin.simulation import TurnFact

from flyin.scheduling.known_routes import KnownRouteScheduler


class RouteAllocator:
    """Assign drones to candidate routes before capacity-aware scheduling."""

    @classmethod
    def schedule(
        cls,
        parsed_map: ParsedMap,
        max_routes: int = 8,
        max_turns: int = 1000,
    ) -> tuple[tuple[TurnFact, ...], ...]:
        """Return a deterministic validator-clean schedule."""
        candidates = CandidateRouteFinder.find_candidates(
            parsed_map,
            max_routes,
        )
        routes_by_drone_id = cls.allocate(parsed_map, candidates)
        return KnownRouteScheduler.schedule_known_routes(
            parsed_map,
            routes_by_drone_id,
            max_turns,
        )

    @staticmethod
    def allocate(
        parsed_map: ParsedMap,
        candidates: tuple[Route, ...],
    ) -> dict[int, Route]:
        """Distribute drones round-robin across discovered routes."""
        if not candidates:
            raise ValueError("at least one candidate route is required")
        return {
            drone_id: candidates[(drone_id - 1) % len(candidates)]
            for drone_id in range(1, parsed_map.drone_count + 1)
        }
