"""Bounded deterministic candidate-route discovery."""

from flyin.domain import Connection, ParsedMap, Zone, ZoneType
from flyin.pathfinding.astar import AStarPathfinder, Route
from flyin.pathfinding.graph import (
    NoRouteError,
    ReverseHopDistances,
    TraversableGraph,
)


class CandidateRouteFinder:
    """Find a small deterministic set of simple start-to-end routes."""

    @classmethod
    def find_candidates(
        cls,
        parsed_map: ParsedMap,
        max_routes: int = 8,
    ) -> tuple[Route, ...]:
        """Return bounded simple routes with the exact shortest route first."""
        if max_routes < 1:
            raise ValueError("max_routes must be positive")
        graph = TraversableGraph.from_parsed_map(parsed_map)
        hops = ReverseHopDistances.to_end(graph, parsed_map.end)
        if not hops.can_reach_end(parsed_map.start):
            raise NoRouteError(
                f"{parsed_map.start.name} cannot reach {parsed_map.end.name}"
            )

        routes: list[Route] = []
        cls._collect_routes(
            graph,
            hops,
            parsed_map.start,
            parsed_map.end,
            (parsed_map.start,),
            (),
            routes,
        )
        ordered = tuple(sorted(routes, key=cls._route_key))[:max_routes]
        shortest = AStarPathfinder.shortest_path(parsed_map)
        return cls._with_shortest_first(shortest, ordered, max_routes)

    @classmethod
    def _collect_routes(
        cls,
        graph: TraversableGraph,
        hops: ReverseHopDistances,
        current: Zone,
        end: Zone,
        zones: tuple[Zone, ...],
        connections: tuple[Connection, ...],
        routes: list[Route],
    ) -> None:
        # ponytail: simple DFS is enough for M4 correctness; replace with
        # measured k-shortest search only if M5 benchmarks need it.
        if current.name == end.name:
            routes.append(cls._route(zones, connections))
            return
        seen_names = {zone.name for zone in zones}
        for traversal in graph.neighbors(current):
            destination = traversal.destination
            if destination.name in seen_names:
                continue
            if not hops.can_reach_end(destination):
                continue
            cls._collect_routes(
                graph,
                hops,
                destination,
                end,
                (*zones, destination),
                (*connections, traversal.connection),
                routes,
            )

    @classmethod
    def _route(
        cls,
        zones: tuple[Zone, ...],
        connections: tuple[Connection, ...],
    ) -> Route:
        return Route(
            zones,
            connections,
            sum(cls._movement_cost(zone) for zone in zones[1:]),
            sum(zone.zone_type is ZoneType.PRIORITY for zone in zones[1:]),
        )

    @staticmethod
    def _movement_cost(destination: Zone) -> int:
        if destination.zone_type is ZoneType.RESTRICTED:
            return 2
        return 1

    @staticmethod
    def _route_key(route: Route) -> tuple[int, int, tuple[str, ...]]:
        return (route.cost, -route.priority_score, route.zone_names)

    @classmethod
    def _with_shortest_first(
        cls,
        shortest: Route,
        ordered: tuple[Route, ...],
        max_routes: int,
    ) -> tuple[Route, ...]:
        routes = [shortest]
        for route in ordered:
            if route.zone_names == shortest.zone_names:
                continue
            routes.append(route)
            if len(routes) == max_routes:
                break
        return tuple(routes)
