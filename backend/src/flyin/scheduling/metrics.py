"""Route metrics and fleet makespan estimates."""

from dataclasses import dataclass
from itertools import combinations
from math import ceil

from flyin.domain import CapacityLimit, ParsedMap, Zone
from flyin.pathfinding import Route


@dataclass(frozen=True, slots=True)
class RouteMetrics:
    """Deterministic capacity and cost facts for a candidate route."""

    zone_names: tuple[str, ...]
    cost: int
    priority_score: int
    restricted_count: int
    min_regular_zone_capacity: int
    min_link_capacity: int
    bottleneck: str

    @classmethod
    def from_route(cls, route: Route) -> "RouteMetrics":
        """Calculate local route metrics without scheduling drones."""
        zone_capacities = tuple(
            zone.capacity
            for zone in route.zones[1:-1]
            if isinstance(zone.capacity, int)
        )
        min_zone_capacity = min(zone_capacities, default=1)
        min_link_capacity = min(
            (connection.capacity for connection in route.connections),
            default=1,
        )
        return cls(
            zone_names=route.zone_names,
            cost=route.cost,
            priority_score=route.priority_score,
            restricted_count=sum(
                zone.zone_type == "restricted" for zone in route.zones[1:]
            ),
            min_regular_zone_capacity=min_zone_capacity,
            min_link_capacity=min_link_capacity,
            bottleneck=cls._bottleneck(
                route,
                min_zone_capacity,
                min_link_capacity,
            ),
        )

    @staticmethod
    def _bottleneck(
        route: Route,
        min_zone_capacity: int,
        min_link_capacity: int,
    ) -> str:
        if min_link_capacity <= min_zone_capacity:
            for connection in route.connections:
                if connection.capacity == min_link_capacity:
                    return f"connection:{'-'.join(connection.identity)}"
        for zone in route.zones[1:-1]:
            if zone.capacity == min_zone_capacity:
                return f"zone:{zone.name}"
        return "none"


@dataclass(frozen=True, slots=True)
class RouteWindowEstimate:
    """Estimated turns for using the first N candidate routes."""

    route_count: int
    estimated_turns: int


@dataclass(frozen=True, slots=True)
class RouteSelectionEstimate:
    """Estimated turns for a concrete candidate-route selection."""

    route_indices: tuple[int, ...]
    estimated_turns: int


class FleetMakespanEstimator:
    """Estimate useful candidate-route windows for a drone fleet."""

    @classmethod
    def estimate_windows(
        cls,
        parsed_map: ParsedMap,
        candidates: tuple[Route, ...],
    ) -> tuple[RouteWindowEstimate, ...]:
        """Return deterministic estimates for every candidate prefix."""
        return tuple(
            RouteWindowEstimate(
                route_count,
                cls._estimate_prefix(parsed_map, candidates[:route_count]),
            )
            for route_count in range(1, len(candidates) + 1)
        )

    @classmethod
    def best_route_count(
        cls,
        parsed_map: ParsedMap,
        candidates: tuple[Route, ...],
    ) -> int:
        """Return the lowest estimated candidate prefix size."""
        estimates = cls.estimate_windows(parsed_map, candidates)
        if not estimates:
            raise ValueError("at least one candidate route is required")
        best = min(
            estimates,
            key=lambda item: (item.estimated_turns, item.route_count),
        )
        return best.route_count

    @classmethod
    def ranked_route_counts(
        cls,
        parsed_map: ParsedMap,
        candidates: tuple[Route, ...],
    ) -> tuple[int, ...]:
        """Return candidate prefix sizes from most to least promising."""
        estimates = cls.estimate_windows(parsed_map, candidates)
        return tuple(
            estimate.route_count
            for estimate in sorted(
                estimates,
                key=lambda item: (item.estimated_turns, item.route_count),
            )
        )

    @classmethod
    def ranked_route_selections(
        cls,
        parsed_map: ParsedMap,
        candidates: tuple[Route, ...],
        max_selection_size: int = 4,
    ) -> tuple[tuple[Route, ...], ...]:
        """Return non-prefix candidate selections ranked by estimate."""
        estimates = tuple(
            RouteSelectionEstimate(
                route_indices,
                cls._estimate_prefix(
                    parsed_map,
                    tuple(candidates[index] for index in route_indices),
                ),
            )
            for route_indices in cls._route_index_selections(
                len(candidates),
                max_selection_size,
            )
        )
        return tuple(
            tuple(candidates[index] for index in estimate.route_indices)
            for estimate in sorted(
                estimates,
                key=lambda item: (
                    item.estimated_turns,
                    len(item.route_indices),
                    item.route_indices,
                ),
            )
        )

    @staticmethod
    def _route_index_selections(
        route_count: int,
        max_selection_size: int,
    ) -> tuple[tuple[int, ...], ...]:
        limited_size = min(route_count, max_selection_size)
        selections: list[tuple[int, ...]] = []
        for size in range(1, limited_size + 1):
            selections.extend(combinations(range(route_count), size))
        return tuple(selections)

    @classmethod
    def _estimate_prefix(
        cls,
        parsed_map: ParsedMap,
        routes: tuple[Route, ...],
    ) -> int:
        route_loads = cls._route_loads(parsed_map.drone_count, len(routes))
        route_bounds = tuple(
            route.cost + load - 1
            for route, load in zip(routes, route_loads)
            if load > 0
        )
        resource_bounds = cls._resource_bounds(routes, route_loads)
        return max((*route_bounds, *resource_bounds), default=0)

    @staticmethod
    def _route_loads(drone_count: int, route_count: int) -> tuple[int, ...]:
        loads = [0 for _ in range(route_count)]
        for drone_index in range(drone_count):
            loads[drone_index % route_count] += 1
        return tuple(loads)

    @classmethod
    def _resource_bounds(
        cls,
        routes: tuple[Route, ...],
        route_loads: tuple[int, ...],
    ) -> tuple[int, ...]:
        loads: dict[str, int] = {}
        capacities: dict[str, int] = {}
        costs: dict[str, int] = {}
        for route, route_load in zip(routes, route_loads):
            if route_load == 0:
                continue
            for key, capacity in cls._route_resources(route):
                loads[key] = loads.get(key, 0) + route_load
                capacities[key] = min(capacities.get(key, capacity), capacity)
                costs[key] = max(costs.get(key, 0), route.cost)
        return tuple(
            ceil(loads[key] / capacities[key]) - 1 + costs[key]
            for key in loads
        )

    @staticmethod
    def _route_resources(route: Route) -> tuple[tuple[str, int], ...]:
        resources: list[tuple[str, int]] = []
        for zone in route.zones[1:-1]:
            resources.append((f"zone:{zone.name}", _capacity(zone)))
        for connection in route.connections:
            key = f"connection:{'-'.join(connection.identity)}"
            resources.append(
                (key, connection.capacity)
            )
        return tuple(resources)


def _capacity(zone: Zone) -> int:
    if zone.capacity is CapacityLimit.UNLIMITED:
        return 1
    return zone.capacity
