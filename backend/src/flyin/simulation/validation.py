"""Independent validation for emitted Fly-In schedules."""

from dataclasses import dataclass

from flyin.domain import CapacityLimit, Connection, ParsedMap, Zone, ZoneType
from flyin.simulation.model import (
    AtZone,
    Delivered,
    DroneLocation,
    InTransit,
    MovementFact,
    TransitFact,
    TurnFact,
)


@dataclass(frozen=True, slots=True)
class ScheduleValidationError:
    """A stable schedule validation failure."""

    code: str
    turn: int
    message: str
    drone_id: int | None = None
    zone_name: str | None = None
    connection_identity: tuple[str, str] | None = None


@dataclass(frozen=True, slots=True)
class ScheduleValidationResult:
    """Validation result for a complete or prefix schedule."""

    errors: tuple[ScheduleValidationError, ...]

    @property
    def is_valid(self) -> bool:
        """Return whether no invariant failed."""
        return not self.errors


class ScheduleValidator:
    """Validate emitted turns independently from the scheduler/engine."""

    @classmethod
    def validate(
        cls,
        parsed_map: ParsedMap,
        turns: tuple[tuple[TurnFact, ...], ...],
        require_complete: bool = True,
    ) -> ScheduleValidationResult:
        """Validate movement legality, restricted arrivals, and capacity."""
        locations: dict[int, DroneLocation] = {
            identifier: AtZone(parsed_map.start)
            for identifier in range(1, parsed_map.drone_count + 1)
        }
        errors: list[ScheduleValidationError] = []

        for turn, facts in enumerate(turns, start=1):
            facts_by_drone = cls._facts_by_drone(turn, facts, errors)
            next_locations, link_usage = cls._apply_turn(
                parsed_map,
                turn,
                locations,
                facts_by_drone,
                errors,
            )
            cls._validate_link_capacity(
                parsed_map,
                turn,
                link_usage,
                errors,
            )
            cls._validate_zone_capacity(
                parsed_map,
                turn,
                next_locations,
                errors,
            )
            locations = next_locations

        if require_complete:
            cls._validate_complete(turns, locations, errors)
        return ScheduleValidationResult(tuple(errors))

    @staticmethod
    def _facts_by_drone(
        turn: int,
        facts: tuple[TurnFact, ...],
        errors: list[ScheduleValidationError],
    ) -> dict[int, TurnFact]:
        facts_by_drone: dict[int, TurnFact] = {}
        for fact in facts:
            if fact.drone_id in facts_by_drone:
                errors.append(
                    ScheduleValidationError(
                        "DUPLICATE_DRONE_FACT",
                        turn,
                        "drone has more than one fact in the same turn",
                        drone_id=fact.drone_id,
                    )
                )
            else:
                facts_by_drone[fact.drone_id] = fact
        return facts_by_drone

    @classmethod
    def _apply_turn(
        cls,
        parsed_map: ParsedMap,
        turn: int,
        locations: dict[int, DroneLocation],
        facts_by_drone: dict[int, TurnFact],
        errors: list[ScheduleValidationError],
    ) -> tuple[dict[int, DroneLocation], dict[tuple[str, str], int]]:
        next_locations: dict[int, DroneLocation] = {}
        link_usage: dict[tuple[str, str], int] = {}
        for drone_id, location in locations.items():
            fact = facts_by_drone.pop(drone_id, None)
            next_locations[drone_id] = cls._apply_drone_fact(
                parsed_map,
                turn,
                drone_id,
                location,
                fact,
                link_usage,
                errors,
            )
        for unknown_id in facts_by_drone:
            errors.append(
                ScheduleValidationError(
                    "UNKNOWN_DRONE",
                    turn,
                    "fact references a drone outside nb_drones",
                    drone_id=unknown_id,
                )
            )
        return next_locations, link_usage

    @classmethod
    def _apply_drone_fact(
        cls,
        parsed_map: ParsedMap,
        turn: int,
        drone_id: int,
        location: DroneLocation,
        fact: TurnFact | None,
        link_usage: dict[tuple[str, str], int],
        errors: list[ScheduleValidationError],
    ) -> DroneLocation:
        if isinstance(location, Delivered):
            if fact is not None:
                errors.append(
                    ScheduleValidationError(
                        "DELIVERED_DRONE_MOVED",
                        turn,
                        "delivered drone cannot move again",
                        drone_id=drone_id,
                    )
                )
            return location
        if isinstance(location, InTransit):
            return cls._apply_transit_arrival(
                parsed_map,
                turn,
                drone_id,
                location,
                fact,
                errors,
            )
        if fact is None:
            return location
        if isinstance(fact, MovementFact):
            return cls._apply_movement_fact(
                parsed_map,
                turn,
                location,
                fact,
                link_usage,
                errors,
            )
        return cls._apply_transit_departure(
            parsed_map,
            turn,
            location,
            fact,
            link_usage,
            errors,
        )

    @classmethod
    def _apply_transit_arrival(
        cls,
        parsed_map: ParsedMap,
        turn: int,
        drone_id: int,
        location: InTransit,
        fact: TurnFact | None,
        errors: list[ScheduleValidationError],
    ) -> DroneLocation:
        if location.arrival_turn != turn:
            if fact is not None:
                errors.append(
                    ScheduleValidationError(
                        "EARLY_RESTRICTED_ARRIVAL",
                        turn,
                        "restricted transit cannot finish before arrival turn",
                        drone_id=drone_id,
                    )
                )
            return location
        exact_arrival = (
            isinstance(fact, MovementFact)
            and fact.origin.name == location.origin.name
            and fact.destination.name == location.destination.name
        )
        if not exact_arrival:
            errors.append(
                ScheduleValidationError(
                    "MISSING_RESTRICTED_ARRIVAL",
                    turn,
                    "restricted transit must arrive on its reserved turn",
                    drone_id=drone_id,
                )
            )
            return location
        return cls._arrival_location(parsed_map, location.destination)

    @classmethod
    def _apply_movement_fact(
        cls,
        parsed_map: ParsedMap,
        turn: int,
        location: AtZone,
        fact: MovementFact,
        link_usage: dict[tuple[str, str], int],
        errors: list[ScheduleValidationError],
    ) -> DroneLocation:
        if fact.origin.name != location.zone.name:
            errors.append(cls._illegal_move(turn, fact))
            return location
        destination = cls._zone_by_name(parsed_map, fact.destination.name)
        if destination is None:
            errors.append(cls._illegal_move(turn, fact))
            return location
        connection = cls._connection_between(
            parsed_map,
            location.zone,
            destination,
        )
        if connection is None:
            errors.append(cls._illegal_move(turn, fact))
            return location
        if destination.zone_type is ZoneType.BLOCKED:
            errors.append(
                ScheduleValidationError(
                    "BLOCKED_DESTINATION",
                    turn,
                    "blocked zones cannot be entered",
                    drone_id=fact.drone_id,
                    zone_name=destination.name,
                )
            )
            return location
        if destination.zone_type is ZoneType.RESTRICTED:
            errors.append(
                ScheduleValidationError(
                    "RESTRICTED_REQUIRES_TRANSIT",
                    turn,
                    "restricted destination requires a transit fact first",
                    drone_id=fact.drone_id,
                    zone_name=destination.name,
                )
            )
            return location
        cls._count_link_use(link_usage, connection)
        return cls._arrival_location(parsed_map, destination)

    @classmethod
    def _apply_transit_departure(
        cls,
        parsed_map: ParsedMap,
        turn: int,
        location: AtZone,
        fact: TransitFact,
        link_usage: dict[tuple[str, str], int],
        errors: list[ScheduleValidationError],
    ) -> DroneLocation:
        if fact.origin.name != location.zone.name:
            errors.append(
                ScheduleValidationError(
                    "ILLEGAL_MOVE",
                    turn,
                    "fact origin does not match drone location",
                    drone_id=fact.drone_id,
                )
            )
            return location
        destination = cls._zone_by_name(parsed_map, fact.destination.name)
        if destination is None:
            errors.append(
                ScheduleValidationError(
                    "ILLEGAL_MOVE",
                    turn,
                    "unknown transit destination",
                    drone_id=fact.drone_id,
                )
            )
            return location
        if fact.connection.identity != tuple(
            sorted((location.zone.name, destination.name))
        ):
            errors.append(
                ScheduleValidationError(
                    "ILLEGAL_MOVE",
                    turn,
                    "transit fact connection does not match endpoints",
                    drone_id=fact.drone_id,
                )
            )
            return location
        connection = cls._connection_between(
            parsed_map,
            location.zone,
            destination,
        )
        if connection is None:
            errors.append(
                ScheduleValidationError(
                    "ILLEGAL_MOVE",
                    turn,
                    "transit does not follow a legal physical connection",
                    drone_id=fact.drone_id,
                )
            )
            return location
        if destination.zone_type is not ZoneType.RESTRICTED:
            errors.append(
                ScheduleValidationError(
                    "INVALID_TRANSIT_DESTINATION",
                    turn,
                    "transit facts are only for restricted destinations",
                    drone_id=fact.drone_id,
                    zone_name=destination.name,
                )
            )
            return location
        cls._count_link_use(link_usage, connection)
        return InTransit(connection, location.zone, destination, turn + 1)

    @staticmethod
    def _arrival_location(
        parsed_map: ParsedMap,
        destination: Zone,
    ) -> DroneLocation:
        if destination.name == parsed_map.end.name:
            return Delivered()
        return AtZone(destination)

    @staticmethod
    def _zone_by_name(parsed_map: ParsedMap, name: str) -> Zone | None:
        for zone in (parsed_map.start, *parsed_map.hubs, parsed_map.end):
            if zone.name == name:
                return zone
        return None

    @staticmethod
    def _connection_between(
        parsed_map: ParsedMap,
        origin: Zone,
        destination: Zone,
    ) -> Connection | None:
        identity = tuple(sorted((origin.name, destination.name)))
        for connection in parsed_map.connections:
            if connection.identity == identity:
                return connection
        return None

    @staticmethod
    def _count_link_use(
        link_usage: dict[tuple[str, str], int],
        connection: Connection,
    ) -> None:
        link_usage[connection.identity] = (
            link_usage.get(connection.identity, 0) + 1
        )

    @staticmethod
    def _illegal_move(
        turn: int,
        fact: MovementFact,
    ) -> ScheduleValidationError:
        return ScheduleValidationError(
            "ILLEGAL_MOVE",
            turn,
            "movement does not follow a legal physical connection",
            drone_id=fact.drone_id,
        )

    @staticmethod
    def _validate_link_capacity(
        parsed_map: ParsedMap,
        turn: int,
        link_usage: dict[tuple[str, str], int],
        errors: list[ScheduleValidationError],
    ) -> None:
        capacity_by_identity = {
            connection.identity: connection.capacity
            for connection in parsed_map.connections
        }
        for identity, usage in link_usage.items():
            if usage > capacity_by_identity[identity]:
                errors.append(
                    ScheduleValidationError(
                        "LINK_CAPACITY_EXCEEDED",
                        turn,
                        "undirected connection capacity exceeded",
                        connection_identity=identity,
                    )
                )

    @staticmethod
    def _validate_zone_capacity(
        parsed_map: ParsedMap,
        turn: int,
        locations: dict[int, DroneLocation],
        errors: list[ScheduleValidationError],
    ) -> None:
        occupancy: dict[str, int] = {}
        capacity_by_zone = {
            zone.name: zone.capacity
            for zone in (parsed_map.start, *parsed_map.hubs, parsed_map.end)
        }
        for location in locations.values():
            if not isinstance(location, AtZone):
                continue
            name = location.zone.name
            if name in (parsed_map.start.name, parsed_map.end.name):
                continue
            occupancy[name] = occupancy.get(name, 0) + 1
        for zone_name, count in occupancy.items():
            capacity = capacity_by_zone[zone_name]
            if capacity is not CapacityLimit.UNLIMITED and count > capacity:
                errors.append(
                    ScheduleValidationError(
                        "ZONE_CAPACITY_EXCEEDED",
                        turn,
                        "regular zone capacity exceeded",
                        zone_name=zone_name,
                    )
                )

    @staticmethod
    def _validate_complete(
        turns: tuple[tuple[TurnFact, ...], ...],
        locations: dict[int, DroneLocation],
        errors: list[ScheduleValidationError],
    ) -> None:
        last_turn = len(turns)
        for drone_id, location in locations.items():
            if isinstance(location, Delivered):
                continue
            if isinstance(location, InTransit):
                errors.append(
                    ScheduleValidationError(
                        "MISSING_RESTRICTED_ARRIVAL",
                        location.arrival_turn,
                        "schedule ended before restricted arrival",
                        drone_id=drone_id,
                    )
                )
            else:
                errors.append(
                    ScheduleValidationError(
                        "NOT_DELIVERED",
                        last_turn,
                        "schedule ended before drone reached end",
                        drone_id=drone_id,
                    )
                )
