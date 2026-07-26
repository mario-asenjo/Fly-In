"""Deterministic simulation primitives for known Fly-In routes."""

from dataclasses import dataclass

from flyin.domain import Connection, ParsedMap, Zone, ZoneType
from flyin.pathfinding import Route


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
class MovementFact:
    """One evaluator-visible drone movement in a completed turn."""

    drone_id: int
    origin: Zone
    destination: Zone

    @property
    def token(self) -> str:
        """Return the mandatory stdout token for a zone arrival."""
        return f"D{self.drone_id}-{self.destination.name}"


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
class TurnResult:
    """The next state plus facts emitted by the applied atomic turn."""

    state: SimulationState
    facts: tuple[MovementFact, ...]


class SimulationEngine:
    """Apply deterministic turns for precomputed non-restricted routes."""

    @classmethod
    def advance_one_turn(
        cls,
        state: SimulationState,
        routes_by_drone_id: dict[int, Route],
    ) -> TurnResult:
        """Plan every drone move from the input state, then apply together."""
        next_drones: list[Drone] = []
        facts: list[MovementFact] = []
        next_turn = state.turn + 1

        for drone in state.drones:
            planned = cls._planned_drone(drone, routes_by_drone_id, state.end)
            next_drones.append(planned)
            if isinstance(drone.location, AtZone):
                fact = cls._movement_fact(drone, planned, state.end)
                if fact is not None:
                    facts.append(fact)

        return TurnResult(
            SimulationState(
                next_turn,
                tuple(next_drones),
                state.start,
                state.end,
            ),
            tuple(sorted(facts, key=lambda fact: fact.drone_id)),
        )

    @classmethod
    def _planned_drone(
        cls,
        drone: Drone,
        routes_by_drone_id: dict[int, Route],
        end: Zone,
    ) -> Drone:
        if isinstance(drone.location, Delivered | InTransit):
            return drone

        route = routes_by_drone_id.get(drone.identifier)
        if route is None:
            return drone

        next_zone = cls._next_zone(route, drone.location.zone)
        if next_zone is None:
            return drone
        if next_zone.zone_type is ZoneType.RESTRICTED:
            raise NotImplementedError("restricted transit starts in M3.4")
        if next_zone.name == end.name:
            return Drone(drone.identifier, Delivered())
        return Drone(drone.identifier, AtZone(next_zone))

    @staticmethod
    def _next_zone(route: Route, current_zone: Zone) -> Zone | None:
        for index, zone in enumerate(route.zones[:-1]):
            if zone.name == current_zone.name:
                return route.zones[index + 1]
        return None

    @staticmethod
    def _movement_fact(
        before: Drone,
        after: Drone,
        end: Zone,
    ) -> MovementFact | None:
        if not isinstance(before.location, AtZone):
            return None
        if isinstance(after.location, AtZone):
            if after.location.zone.name == before.location.zone.name:
                return None
            return MovementFact(
                before.identifier,
                before.location.zone,
                after.location.zone,
            )
        if isinstance(after.location, Delivered):
            return MovementFact(
                before.identifier,
                before.location.zone,
                end,
            )
        return None


def format_turn(facts: tuple[MovementFact, ...]) -> str:
    """Format one evaluator-safe output line from movement facts."""
    return " ".join(
        fact.token for fact in sorted(facts, key=lambda fact: fact.drone_id)
    )


__all__ = [
    "AtZone",
    "Delivered",
    "Drone",
    "DroneLocation",
    "InTransit",
    "MovementFact",
    "SimulationEngine",
    "SimulationState",
    "TurnResult",
    "format_turn",
]
