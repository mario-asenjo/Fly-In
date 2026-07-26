"""Core map types for the Fly-In domain."""

from dataclasses import dataclass
from enum import StrEnum

Metadata = tuple[tuple[str, str], ...]


class ZoneType(StrEnum):
    """The effective routing behavior of a zone."""

    NORMAL = "normal"
    BLOCKED = "blocked"
    RESTRICTED = "restricted"
    PRIORITY = "priority"


class CapacityLimit(StrEnum):
    """A non-numeric effective capacity state."""

    UNLIMITED = "unlimited"


EffectiveCapacity = int | CapacityLimit


@dataclass(frozen=True, slots=True)
class Zone:
    """A named position in a Fly-In map."""

    name: str
    x: int
    y: int
    metadata: Metadata = ()
    zone_type: ZoneType = ZoneType.NORMAL
    color: str | None = None
    capacity: EffectiveCapacity = 1


@dataclass(frozen=True, slots=True)
class Connection:
    """A connection between two zones."""

    left: Zone
    right: Zone
    metadata: Metadata = ()
    capacity: int = 1

    @property
    def identity(self) -> tuple[str, str]:
        """Return sorted endpoint names for use as an undirected key."""
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
