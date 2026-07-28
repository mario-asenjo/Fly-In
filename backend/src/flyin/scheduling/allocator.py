"""Route allocation over bounded candidate paths."""

from flyin.domain import ParsedMap
from flyin.pathfinding import CandidateRouteFinder, Route
from flyin.simulation import TurnFact

from flyin.scheduling.known_routes import (
    KnownRouteScheduler,
    ScheduleDeadlockError,
)


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
        last_error: ScheduleDeadlockError | None = None
        for route_count in range(len(candidates), 0, -1):
            routes_by_drone_id = cls.allocate(
                parsed_map,
                candidates[:route_count],
            )
            try:
                return KnownRouteScheduler.schedule_known_routes(
                    parsed_map,
                    routes_by_drone_id,
                    max_turns,
                )
            except ScheduleDeadlockError as exc:
                last_error = exc
        if last_error is not None:
            raise last_error
        raise ValueError("at least one candidate route is required")

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
