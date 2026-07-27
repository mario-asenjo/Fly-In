"""Simulation-specific models for deterministic Fly-In turns."""

from dataclasses import dataclass

from flyin.domain import Connection, ParsedMap, Zone


@dataclass(frozen=True, slots=True)
class AtZone:
    """Drone location while it is ready to depart from a zone."""

    zone: Zone


@dataclass(frozen=True, slots=True)
class InTransit:
    """Drone location while crossing toward a restricted destination."""

    connection: Connection
    origin: Zone
    destination: Zone
    arrival_turn: int


@dataclass(frozen=True, slots=True)
class Delivered:
    """Drone location after it reaches the end hub."""


DroneLocation = AtZone | InTransit | Delivered


@dataclass(frozen=True, slots=True)
class Drone:
    """A typed simulation drone with one explicit location state."""

    identifier: int
    location: DroneLocation


@dataclass(frozen=True, slots=True)
class SimulationState:
    """Immutable snapshot of all drones at the end of a turn."""

    turn: int
    drones: tuple[Drone, ...]
    start: Zone
    end: Zone

    @classmethod
    def initial(cls, parsed_map: ParsedMap) -> "SimulationState":
        """Create turn-zero drones at the parsed start hub."""
        drones = tuple(
            Drone(identifier, AtZone(parsed_map.start))
            for identifier in range(1, parsed_map.drone_count + 1)
        )
        return cls(0, drones, parsed_map.start, parsed_map.end)

    def drone_by_id(self, identifier: int) -> Drone:
        """Return one drone by its stable one-based identifier."""
        for drone in self.drones:
            if drone.identifier == identifier:
                return drone
        raise KeyError(identifier)


@dataclass(frozen=True, slots=True)
class MovementFact:
    """One evaluator-visible drone movement in a completed turn."""

    drone_id: int
    origin: Zone
    destination: Zone


@dataclass(frozen=True, slots=True)
class TransitFact:
    """One evaluator-visible drone departure onto a restricted link."""

    drone_id: int
    connection: Connection
    origin: Zone
    destination: Zone


TurnFact = MovementFact | TransitFact


@dataclass(frozen=True, slots=True)
class TurnResult:
    """The next state plus facts emitted by the applied atomic turn."""

    state: SimulationState
    facts: tuple[TurnFact, ...]
