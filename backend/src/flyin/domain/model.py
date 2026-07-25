"""Core map types for the Fly-In domain."""

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class Zone:
    """A named position in a Fly-In map."""

    name: str
    x: int
    y: int


@dataclass(frozen=True, slots=True)
class Connection:
    """A connection between two zones."""

    left: Zone
    right: Zone


@dataclass(frozen=True, slots=True)
class ParsedMap:
    """The map data produced by parsing a Fly-In source."""

    drone_count: int
    start: Zone
    end: Zone
    connections: tuple[Connection, ...]
