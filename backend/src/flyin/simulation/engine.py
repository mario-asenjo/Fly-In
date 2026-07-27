"""Deterministic turn engine for known Fly-In routes."""

from typing import Mapping

from flyin.domain import Connection, Zone, ZoneType
from flyin.pathfinding import Route
from flyin.simulation.model import (
    AtZone,
    Delivered,
    Drone,
    InTransit,
    MovementFact,
    SimulationState,
    TransitFact,
    TurnFact,
    TurnResult,
)


class SimulationEngine:
    """Apply deterministic turns for precomputed routes."""

    @classmethod
    def advance_one_turn(
        cls,
        state: SimulationState,
        routes_by_drone_id: Mapping[int, Route],
    ) -> TurnResult:
        """Plan every drone move from the input state, then apply together."""
        next_drones: list[Drone] = []
        facts: list[TurnFact] = []
        next_turn = state.turn + 1

        for drone in state.drones:
            planned = cls._planned_drone(
                drone,
                routes_by_drone_id,
                state.end,
                next_turn,
            )
            next_drones.append(planned)
            fact = cls._turn_fact(drone, planned, state.end)
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
        routes_by_drone_id: Mapping[int, Route],
        end: Zone,
        next_turn: int,
    ) -> Drone:
        if isinstance(drone.location, Delivered):
            return drone
        if isinstance(drone.location, InTransit):
            if drone.location.arrival_turn != next_turn:
                return drone
            if drone.location.destination.name == end.name:
                return Drone(drone.identifier, Delivered())
            return Drone(drone.identifier, AtZone(drone.location.destination))

        route = routes_by_drone_id.get(drone.identifier)
        if route is None:
            return drone

        next_step = cls._next_step(route, drone.location.zone)
        if next_step is None:
            return drone
        next_zone, connection = next_step
        if next_zone.zone_type is ZoneType.RESTRICTED:
            return Drone(
                drone.identifier,
                InTransit(
                    connection,
                    drone.location.zone,
                    next_zone,
                    next_turn + 1,
                ),
            )
        if next_zone.name == end.name:
            return Drone(drone.identifier, Delivered())
        return Drone(drone.identifier, AtZone(next_zone))

    @staticmethod
    def _next_step(
        route: Route,
        current_zone: Zone,
    ) -> tuple[Zone, Connection] | None:
        for index, zone in enumerate(route.zones[:-1]):
            if zone.name == current_zone.name:
                return route.zones[index + 1], route.connections[index]
        return None

    @staticmethod
    def _turn_fact(
        before: Drone,
        after: Drone,
        end: Zone,
    ) -> TurnFact | None:
        if isinstance(before.location, InTransit) and isinstance(
            after.location,
            AtZone | Delivered,
        ):
            destination = end if isinstance(after.location, Delivered) else (
                after.location.zone
            )
            return MovementFact(
                before.identifier,
                before.location.origin,
                destination,
            )
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
        if isinstance(after.location, InTransit):
            return TransitFact(
                before.identifier,
                after.location.connection,
                after.location.origin,
                after.location.destination,
            )
        return None
