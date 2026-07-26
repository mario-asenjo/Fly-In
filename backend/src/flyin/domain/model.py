"""Core map types for the Fly-In domain."""

from dataclasses import dataclass

Metadata = tuple[tuple[str, str], ...]


@dataclass(frozen=True, slots=True)
class Zone:
    """A named position in a Fly-In map."""

    name: str
    x: int
    y: int
    metadata: Metadata = ()


@dataclass(frozen=True, slots=True)
class Connection:
    """A connection between two zones."""

    left: Zone
    right: Zone
    metadata: Metadata = ()

    @property
    def identity(self) -> tuple[str, str]:
        """Return an order-independent identity while preserving traversal endpoints."""
        names = (self.left.name, self.right.name)
        return names if names[0] <= names[1] else (names[1], names[0])


@dataclass(frozen=True, slots=True)
class ParsedMap:
    """The map data produced by parsing a Fly-In source."""

    drone_count: int
    start: Zone
    end: Zone
    hubs: tuple[Zone, ...]
    connections: tuple[Connection, ...]
