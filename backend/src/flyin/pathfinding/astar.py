"""Exact A* pathfinding for one Fly-In drone."""

from dataclasses import dataclass, field
from heapq import heappop, heappush
from itertools import count
from typing import ClassVar

from flyin.domain import Connection, ParsedMap, Zone, ZoneType
from flyin.pathfinding.graph import (
    NoRouteError,
    ReverseHopDistances,
    TraversableGraph,
)


@dataclass(frozen=True, slots=True)
class Route:
    """A deterministic weighted route from start to end."""

    zones: tuple[Zone, ...]
    connections: tuple[Connection, ...]
    cost: int
    priority_score: int

    @property
    def zone_names(self) -> tuple[str, ...]:
        """Return route zone names for tests, teaching, and later adapters."""
        return tuple(zone.name for zone in self.zones)


@dataclass(order=True, slots=True)
class _QueueItem:
    """Heap entry for exact A* ordering."""

    estimated_total: int
    cost: int
    negative_priority_score: int
    path_key: tuple[str, ...]
    sequence: int
    zone: Zone = field(compare=False)
    zones: tuple[Zone, ...] = field(compare=False)
    connections: tuple[Connection, ...] = field(compare=False)
    priority_score: int = field(compare=False)


class AStarPathfinder:
    """Find one exact destination-weighted route with stdlib heapq."""

    _DESTINATION_COST: ClassVar[dict[ZoneType, int]] = {
        ZoneType.NORMAL: 1,
        ZoneType.PRIORITY: 1,
        ZoneType.RESTRICTED: 2,
    }

    @classmethod
    def shortest_path(
        cls,
        parsed_map: ParsedMap,
        use_heuristic: bool = True,
    ) -> Route:
        """Return the best one-drone route from start to end."""
        graph = TraversableGraph.from_parsed_map(parsed_map)
        hops = ReverseHopDistances.to_end(graph, parsed_map.end)
        if not hops.can_reach_end(parsed_map.start):
            raise NoRouteError(
                f"{parsed_map.start.name} cannot reach {parsed_map.end.name}"
            )

        best_cost_by_zone = {parsed_map.start.name: 0}
        queue: list[_QueueItem] = []
        sequence = count()
        start_path_key = (parsed_map.start.name,)
        heappush(
            queue,
            _QueueItem(
                cls._estimated_total(
                    0,
                    hops,
                    parsed_map.start,
                    use_heuristic,
                ),
                0,
                0,
                start_path_key,
                next(sequence),
                parsed_map.start,
                (parsed_map.start,),
                (),
                0,
            ),
        )
        best_route: Route | None = None

        while queue:
            current = heappop(queue)
            if (
                best_route is not None
                and current.estimated_total > best_route.cost
            ):
                break
            if current.cost > best_cost_by_zone[current.zone.name]:
                continue
            if current.zone.name == parsed_map.end.name:
                candidate = Route(
                    current.zones,
                    current.connections,
                    current.cost,
                    current.priority_score,
                )
                best_route = cls._better_route(best_route, candidate)
                continue

            for traversal in graph.neighbors(current.zone):
                destination = traversal.destination
                movement_cost = cls._movement_cost(destination)
                new_cost = current.cost + movement_cost
                known_cost = best_cost_by_zone.get(destination.name)
                if known_cost is not None and new_cost > known_cost:
                    continue
                best_cost_by_zone[destination.name] = new_cost
                new_priority = current.priority_score + int(
                    destination.zone_type is ZoneType.PRIORITY
                )
                new_zones = (*current.zones, destination)
                new_connections = (*current.connections, traversal.connection)
                path_key = tuple(zone.name for zone in new_zones)
                heappush(
                    queue,
                    _QueueItem(
                        cls._estimated_total(
                            new_cost,
                            hops,
                            destination,
                            use_heuristic,
                        ),
                        new_cost,
                        -new_priority,
                        path_key,
                        next(sequence),
                        destination,
                        new_zones,
                        new_connections,
                        new_priority,
                    ),
                )

        if best_route is None:
            raise NoRouteError(
                f"{parsed_map.start.name} cannot reach {parsed_map.end.name}"
            )
        return best_route

    @classmethod
    def _movement_cost(cls, destination: Zone) -> int:
        return cls._DESTINATION_COST[destination.zone_type]

    @staticmethod
    def _estimated_total(
        cost: int,
        hops: ReverseHopDistances,
        zone: Zone,
        use_heuristic: bool,
    ) -> int:
        if not use_heuristic:
            return cost
        return cost + hops.hops_from(zone)

    @staticmethod
    def _better_route(
        current: Route | None,
        candidate: Route,
    ) -> Route:
        if current is None:
            return candidate
        current_key = (
            current.cost,
            -current.priority_score,
            current.zone_names,
        )
        candidate_key = (
            candidate.cost,
            -candidate.priority_score,
            candidate.zone_names,
        )
        return candidate if candidate_key < current_key else current
