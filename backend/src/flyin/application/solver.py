"""Adapter-neutral map solving use case."""

from dataclasses import dataclass

from flyin.domain import CapacityLimit, ParsedMap, Zone
from flyin.parsing import MapParseError, MapParser
from flyin.pathfinding import NoRouteError
from flyin.scheduling import RouteAllocator, ScheduleDeadlockError
from flyin.simulation import (
    AtZone,
    Delivered,
    DroneLocation,
    InTransit,
    MovementFact,
    ScheduleValidator,
    TransitFact,
    TurnFact,
    format_turn,
)


@dataclass(frozen=True, slots=True)
class SolveWarning:
    """Non-fatal application diagnostic for adapters to present safely."""

    code: str
    message: str
    zone_name: str | None = None


@dataclass(frozen=True, slots=True)
class ZoneView:
    """Adapter-safe zone projection for terminal/API visualization."""

    name: str
    x: int
    y: int
    kind: str
    color: str | None
    capacity: int | str


@dataclass(frozen=True, slots=True)
class ConnectionView:
    """Adapter-safe physical connection projection."""

    left: str
    right: str
    capacity: int


@dataclass(frozen=True, slots=True)
class MapView:
    """Adapter-safe parsed map projection."""

    drone_count: int
    start: str
    end: str
    zones: tuple[ZoneView, ...]
    connections: tuple[ConnectionView, ...]


@dataclass(frozen=True, slots=True)
class MovementView:
    """Adapter-safe movement projection with visual metadata."""

    drone_id: int
    token: str
    origin: str
    origin_color: str | None
    destination: str
    destination_color: str | None
    connection: tuple[str, str]
    path_cost: int


@dataclass(frozen=True, slots=True)
class MetricsView:
    """Optional subject metrics derived from the completed schedule."""

    moved_drones_per_turn: tuple[int, ...]
    average_turns_per_drone: float
    total_path_cost: int


@dataclass(frozen=True, slots=True)
class TurnView:
    """Adapter-safe turn projection."""

    number: int
    line: str
    movements: tuple[MovementView, ...]


CapacityValue = int | str
ZoneCapacityRow = tuple[str, int, CapacityValue]
ConnectionCapacityRow = tuple[str, str, int, int]


@dataclass(frozen=True, slots=True)
class TurnCapacityView:
    """Adapter-safe capacity usage after one completed turn."""

    number: int
    zones: tuple[ZoneCapacityRow, ...]
    connections: tuple[ConnectionCapacityRow, ...]


@dataclass(frozen=True, slots=True)
class SolveResult:
    """Completed adapter-neutral solve result."""

    parsed_map: ParsedMap
    schedule: tuple[tuple[TurnFact, ...], ...]
    map_view: MapView
    turns: tuple[TurnView, ...]
    capacity_turns: tuple[TurnCapacityView, ...]
    metrics: MetricsView
    movement_lines: tuple[str, ...]
    warnings: tuple[SolveWarning, ...] = ()

    @property
    def turn_count(self) -> int:
        """Return completed makespan in turns."""
        return len(self.schedule)


class SolveError(RuntimeError):
    """Stable application-level error for CLI/API adapters."""

    def __init__(
        self,
        code: str,
        message: str,
        line: int | None = None,
    ) -> None:
        super().__init__(message)
        self.code = code
        self.message = message
        self.line = line


class FlyInSolver:
    """Coordinate parsing, scheduling, validation, and output facts."""

    @classmethod
    def solve_text(
        cls,
        source: str,
        max_routes: int = 8,
        max_turns: int = 1000,
    ) -> SolveResult:
        """Solve one Fly-In map source without adapter concerns."""
        try:
            parsed_map = MapParser().parse(source)
        except MapParseError as exc:
            raise SolveError(
                "MAP_PARSE_ERROR",
                exc.cause,
                exc.line_number,
            ) from exc

        warnings = cls._warnings(parsed_map)
        try:
            schedule = RouteAllocator.schedule(
                parsed_map,
                max_routes=max_routes,
                max_turns=max_turns,
            )
        except NoRouteError as exc:
            raise SolveError("NO_ROUTE", str(exc)) from exc
        except ScheduleDeadlockError as exc:
            raise SolveError("SCHEDULE_DEADLOCK", str(exc)) from exc
        except ValueError as exc:
            raise SolveError("SOLVE_FAILED", str(exc)) from exc

        validation = ScheduleValidator.validate(parsed_map, schedule)
        if not validation.is_valid:
            first_error = validation.errors[0]
            raise SolveError(
                "INVALID_SCHEDULE",
                first_error.message,
                first_error.turn,
            )
        turns = cls._turn_views(schedule)
        return SolveResult(
            parsed_map=parsed_map,
            schedule=schedule,
            map_view=cls._map_view(parsed_map),
            turns=turns,
            capacity_turns=cls._capacity_turns(parsed_map, schedule),
            metrics=cls._metrics(turns, parsed_map.end.name),
            movement_lines=tuple(format_turn(turn) for turn in schedule),
            warnings=warnings,
        )

    @staticmethod
    def _map_view(parsed_map: ParsedMap) -> MapView:
        zones = (parsed_map.start, *parsed_map.hubs, parsed_map.end)
        return MapView(
            drone_count=parsed_map.drone_count,
            start=parsed_map.start.name,
            end=parsed_map.end.name,
            zones=tuple(
                ZoneView(
                    name=zone.name,
                    x=zone.x,
                    y=zone.y,
                    kind=zone.zone_type.value,
                    color=zone.color,
                    capacity=(
                        zone.capacity.value
                        if zone.capacity is CapacityLimit.UNLIMITED
                        else zone.capacity
                    ),
                )
                for zone in zones
            ),
            connections=tuple(
                ConnectionView(
                    left=connection.left.name,
                    right=connection.right.name,
                    capacity=connection.capacity,
                )
                for connection in parsed_map.connections
            ),
        )

    @classmethod
    def _turn_views(
        cls,
        schedule: tuple[tuple[TurnFact, ...], ...],
    ) -> tuple[TurnView, ...]:
        return tuple(
            TurnView(
                number=number,
                line=format_turn(turn),
                movements=tuple(
                    cls._movement_view(fact)
                    for fact in sorted(turn, key=lambda fact: fact.drone_id)
                ),
            )
            for number, turn in enumerate(schedule, start=1)
        )

    @classmethod
    def _movement_view(cls, fact: TurnFact) -> MovementView:
        if isinstance(fact, MovementFact):
            return MovementView(
                drone_id=fact.drone_id,
                token=f"D{fact.drone_id}-{fact.destination.name}",
                origin=fact.origin.name,
                origin_color=fact.origin.color,
                destination=fact.destination.name,
                destination_color=fact.destination.color,
                connection=(fact.origin.name, fact.destination.name),
                path_cost=cls._movement_path_cost(fact),
            )
        if isinstance(fact, TransitFact):
            return MovementView(
                drone_id=fact.drone_id,
                token=(
                    f"D{fact.drone_id}-{fact.origin.name}-"
                    f"{fact.destination.name}"
                ),
                origin=fact.origin.name,
                origin_color=fact.origin.color,
                destination=fact.destination.name,
                destination_color=fact.destination.color,
                connection=(fact.origin.name, fact.destination.name),
                path_cost=2,
            )
        raise TypeError(f"unsupported turn fact: {type(fact).__name__}")

    @staticmethod
    def _movement_path_cost(fact: MovementFact) -> int:
        if fact.destination.zone_type.value == "restricted":
            return 0
        return 1

    @staticmethod
    def _metrics(
        turns: tuple[TurnView, ...],
        end_name: str,
    ) -> MetricsView:
        delivery_turns: dict[int, int] = {}
        for turn in turns:
            for movement in turn.movements:
                if movement.destination == end_name:
                    delivery_turns[movement.drone_id] = turn.number
        average_turns = (
            sum(delivery_turns.values()) / len(delivery_turns)
            if delivery_turns
            else 0.0
        )
        return MetricsView(
            moved_drones_per_turn=tuple(
                len(turn.movements) for turn in turns
            ),
            average_turns_per_drone=average_turns,
            total_path_cost=sum(
                movement.path_cost
                for turn in turns
                for movement in turn.movements
            ),
        )

    @classmethod
    def _capacity_turns(
        cls,
        parsed_map: ParsedMap,
        schedule: tuple[tuple[TurnFact, ...], ...],
    ) -> tuple[TurnCapacityView, ...]:
        locations: dict[int, DroneLocation] = {
            identifier: AtZone(parsed_map.start)
            for identifier in range(1, parsed_map.drone_count + 1)
        }
        capacity_turns: list[TurnCapacityView] = []
        zones = (parsed_map.start, *parsed_map.hubs, parsed_map.end)

        for number, turn in enumerate(schedule, start=1):
            facts_by_drone = {fact.drone_id: fact for fact in turn}
            locations = {
                drone_id: cls._apply_capacity_fact(
                    parsed_map,
                    number,
                    location,
                    facts_by_drone.get(drone_id),
                )
                for drone_id, location in locations.items()
            }
            zone_usage = {zone.name: 0 for zone in zones}
            for location in locations.values():
                if isinstance(location, AtZone):
                    zone_usage[location.zone.name] += 1
                elif isinstance(location, Delivered):
                    zone_usage[parsed_map.end.name] += 1

            link_usage: dict[tuple[str, str], int] = {}
            for fact in turn:
                if (
                    isinstance(fact, MovementFact)
                    and fact.destination.zone_type.value == "restricted"
                ):
                    continue
                endpoints = (fact.origin.name, fact.destination.name)
                identity = (
                    endpoints
                    if endpoints[0] <= endpoints[1]
                    else (endpoints[1], endpoints[0])
                )
                link_usage[identity] = link_usage.get(identity, 0) + 1

            capacity_turns.append(
                TurnCapacityView(
                    number=number,
                    zones=tuple(
                        (
                            zone.name,
                            zone_usage[zone.name],
                            cls._capacity_value(zone.capacity),
                        )
                        for zone in zones
                    ),
                    connections=tuple(
                        (
                            connection.left.name,
                            connection.right.name,
                            link_usage.get(connection.identity, 0),
                            connection.capacity,
                        )
                        for connection in parsed_map.connections
                    ),
                )
            )
        return tuple(capacity_turns)

    @classmethod
    def _apply_capacity_fact(
        cls,
        parsed_map: ParsedMap,
        turn: int,
        location: DroneLocation,
        fact: TurnFact | None,
    ) -> DroneLocation:
        if isinstance(location, Delivered):
            return location
        if isinstance(location, InTransit):
            if not isinstance(fact, MovementFact):
                return location
            if location.arrival_turn != turn:
                return location
            return cls._capacity_arrival(parsed_map, fact.destination)
        if fact is None:
            return location
        if isinstance(fact, MovementFact):
            return cls._capacity_arrival(parsed_map, fact.destination)
        return InTransit(
            fact.connection,
            fact.origin,
            fact.destination,
            turn + 1,
        )

    @staticmethod
    def _capacity_arrival(
        parsed_map: ParsedMap,
        destination: Zone,
    ) -> DroneLocation:
        if destination.name == parsed_map.end.name:
            return Delivered()
        return AtZone(destination)

    @staticmethod
    def _capacity_value(capacity: int | CapacityLimit) -> CapacityValue:
        if capacity is CapacityLimit.UNLIMITED:
            return capacity.value
        return capacity

    @staticmethod
    def _warnings(parsed_map: ParsedMap) -> tuple[SolveWarning, ...]:
        warnings: list[SolveWarning] = []
        for zone in (parsed_map.start, parsed_map.end):
            raw_zone_type = dict(zone.metadata).get("zone")
            if raw_zone_type is not None and raw_zone_type != "normal":
                warnings.append(
                    SolveWarning(
                        "TERMINAL_ZONE_TYPE_IGNORED",
                        (
                            f"terminal zone '{zone.name}' declares "
                            f"zone={raw_zone_type}; effective type is normal"
                        ),
                        zone.name,
                    )
                )
        return tuple(warnings)
