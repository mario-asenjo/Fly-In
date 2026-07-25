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


@dataclass(frozen=True, slots=True)
class ParsedMap:
    """The map data produced by parsing a Fly-In source."""

    drone_count: int
    start: Zone
    end: Zone
    hubs: tuple[Zone, ...]
    connections: tuple[Connection, ...]
