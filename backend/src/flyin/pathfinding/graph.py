"""Traversable graph projections for parsed Fly-In maps."""

from collections import deque
from dataclasses import dataclass

from flyin.domain import Connection, ParsedMap, Zone, ZoneType


class NoRouteError(ValueError):
    """Raised when a zone cannot reach the parsed end hub."""


@dataclass(frozen=True, slots=True)
class Traversal:
    """A legal one-edge traversal in the Fly-In graph."""

    destination: Zone
    connection: Connection


@dataclass(frozen=True, slots=True)
class TraversableGraph:
    """Undirected adjacency excluding blocked zones."""

    _adjacency: dict[str, tuple[Traversal, ...]]

    @classmethod
    def from_parsed_map(cls, parsed_map: ParsedMap) -> "TraversableGraph":
        """Build traversable adjacency from parsed physical connections."""
        zones = (parsed_map.start, *parsed_map.hubs, parsed_map.end)
        adjacency: dict[str, list[Traversal]] = {
            zone.name: []
            for zone in zones
            if zone.zone_type is not ZoneType.BLOCKED
        }
        for connection in parsed_map.connections:
            left = connection.left
            right = connection.right
            if (
                left.zone_type is ZoneType.BLOCKED
                or right.zone_type is ZoneType.BLOCKED
            ):
                continue
            adjacency[left.name].append(Traversal(right, connection))
            adjacency[right.name].append(Traversal(left, connection))
        ordered = {
            name: tuple(
                sorted(
                    traversals,
                    key=lambda traversal: traversal.destination.name,
                )
            )
            for name, traversals in adjacency.items()
        }
        return cls(ordered)

    def neighbors(self, zone: Zone) -> tuple[Traversal, ...]:
        """Return deterministic legal traversals from a zone."""
        return self._adjacency.get(zone.name, ())

    def neighbor_names(self, zone: Zone) -> tuple[str, ...]:
        """Return deterministic adjacent zone names for tests/callers."""
        return tuple(
            traversal.destination.name for traversal in self.neighbors(zone)
        )

    def connection_between(
        self,
        origin: Zone,
        destination: Zone,
    ) -> Connection | None:
        """Return the physical connection for a legal traversal, if any."""
        for traversal in self.neighbors(origin):
            if traversal.destination.name == destination.name:
                return traversal.connection
        return None


@dataclass(frozen=True, slots=True)
class ReverseHopDistances:
    """Minimum remaining unweighted hops to the end hub."""

    _end_name: str
    _hops_by_zone_name: dict[str, int]

    @classmethod
    def to_end(
        cls,
        graph: TraversableGraph,
        end: Zone,
    ) -> "ReverseHopDistances":
        """Compute the admissible A* hop heuristic with reverse BFS."""
        hops_by_zone_name = {end.name: 0}
        queue: deque[Zone] = deque((end,))
        while queue:
            current = queue.popleft()
            next_hop_count = hops_by_zone_name[current.name] + 1
            for traversal in graph.neighbors(current):
                name = traversal.destination.name
                if name not in hops_by_zone_name:
                    hops_by_zone_name[name] = next_hop_count
                    queue.append(traversal.destination)
        return cls(end.name, hops_by_zone_name)

    def can_reach_end(self, zone: Zone) -> bool:
        """Return whether the zone can reach the end over traversable links."""
        return zone.name in self._hops_by_zone_name

    def hops_from(self, zone: Zone) -> int:
        """Return remaining hops or fail with a clear no-route error."""
        if zone.name not in self._hops_by_zone_name:
            raise NoRouteError(f"{zone.name} cannot reach {self._end_name}")
        return self._hops_by_zone_name[zone.name]
