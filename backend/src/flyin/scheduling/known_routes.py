"""Capacity-aware scheduling for already-selected Fly-In routes."""

from typing import Mapping

from flyin.domain import CapacityLimit, ParsedMap, Zone
from flyin.pathfinding import Route
from flyin.simulation import (
    AtZone,
    Delivered,
    Drone,
    InTransit,
    SimulationEngine,
    SimulationState,
    TurnFact,
)


class KnownRouteScheduler:
    """Schedule known routes while respecting regular-zone capacity."""

    @classmethod
    def schedule_known_routes(
        cls,
        parsed_map: ParsedMap,
        routes_by_drone_id: Mapping[int, Route],
        max_turns: int = 1000,
    ) -> tuple[tuple[TurnFact, ...], ...]:
        """Return a terminating schedule for precomputed routes."""
        state = SimulationState.initial(parsed_map)
        turns: list[tuple[TurnFact, ...]] = []
        for _ in range(max_turns):
            if cls._all_delivered(state.drones):
                return tuple(turns)
            selected_routes = cls._selected_routes(state, routes_by_drone_id)
            result = SimulationEngine.advance_one_turn(state, selected_routes)
            if not result.facts:
                raise RuntimeError("capacity-aware scheduler made no progress")
            turns.append(result.facts)
            state = result.state
        raise RuntimeError("capacity-aware scheduler exceeded max_turns")

    @classmethod
    def _selected_routes(
        cls,
        state: SimulationState,
        routes_by_drone_id: Mapping[int, Route],
    ) -> dict[int, Route]:
        occupancy = cls._regular_zone_occupancy(state)
        selected: dict[int, Route] = {}
        for drone in cls._departure_order(state, routes_by_drone_id):
            if not isinstance(drone.location, AtZone):
                route = routes_by_drone_id[drone.identifier]
                selected[drone.identifier] = route
                continue
            route = routes_by_drone_id[drone.identifier]
            next_zone = cls._next_zone(route, drone.location.zone)
            if next_zone is None:
                continue
            if not cls._has_destination_capacity(state, next_zone, occupancy):
                continue
            cls._release_origin_capacity(state, drone.location.zone, occupancy)
            cls._reserve_destination_capacity(state, next_zone, occupancy)
            selected[drone.identifier] = route
        return selected

    @staticmethod
    def _all_delivered(drones: tuple[Drone, ...]) -> bool:
        return all(isinstance(drone.location, Delivered) for drone in drones)

    @classmethod
    def _departure_order(
        cls,
        state: SimulationState,
        routes_by_drone_id: Mapping[int, Route],
    ) -> tuple[Drone, ...]:
        movable = (
            drone
            for drone in state.drones
            if drone.identifier in routes_by_drone_id
            and not isinstance(drone.location, Delivered)
        )
        return tuple(
            sorted(
                movable,
                key=lambda drone: (
                    cls._route_position(drone, routes_by_drone_id),
                    drone.identifier,
                ),
            )
        )

    @staticmethod
    def _route_position(
        drone: Drone,
        routes_by_drone_id: Mapping[int, Route],
    ) -> int:
        if isinstance(drone.location, InTransit):
            return -10_000
        if not isinstance(drone.location, AtZone):
            return 0
        route = routes_by_drone_id[drone.identifier]
        for index, zone in enumerate(route.zones):
            if zone.name == drone.location.zone.name:
                return -index
        return 0

    @staticmethod
    def _next_zone(route: Route, current_zone: Zone) -> Zone | None:
        for index, zone in enumerate(route.zones[:-1]):
            if zone.name == current_zone.name:
                return route.zones[index + 1]
        return None

    @staticmethod
    def _regular_zone_occupancy(
        state: SimulationState,
    ) -> dict[str, int]:
        occupancy: dict[str, int] = {}
        for drone in state.drones:
            if not isinstance(drone.location, AtZone):
                continue
            zone = drone.location.zone
            if zone.name in (state.start.name, state.end.name):
                continue
            occupancy[zone.name] = occupancy.get(zone.name, 0) + 1
        return occupancy

    @staticmethod
    def _has_destination_capacity(
        state: SimulationState,
        destination: Zone,
        occupancy: Mapping[str, int],
    ) -> bool:
        if destination.name in (state.start.name, state.end.name):
            return True
        if destination.capacity is CapacityLimit.UNLIMITED:
            return True
        return occupancy.get(destination.name, 0) < destination.capacity

    @staticmethod
    def _release_origin_capacity(
        state: SimulationState,
        origin: Zone,
        occupancy: dict[str, int],
    ) -> None:
        if origin.name in (state.start.name, state.end.name):
            return
        occupancy[origin.name] = occupancy.get(origin.name, 0) - 1

    @staticmethod
    def _reserve_destination_capacity(
        state: SimulationState,
        destination: Zone,
        occupancy: dict[str, int],
    ) -> None:
        if destination.name in (state.start.name, state.end.name):
            return
        occupancy[destination.name] = occupancy.get(destination.name, 0) + 1
