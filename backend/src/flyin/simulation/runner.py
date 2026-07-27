"""Helpers for deterministic known-route simulation output."""

from typing import Mapping

from flyin.domain import ParsedMap
from flyin.pathfinding import Route
from flyin.simulation.engine import SimulationEngine
from flyin.simulation.formatting import format_turn
from flyin.simulation.model import Delivered, SimulationState


def simulate_known_routes(
    parsed_map: ParsedMap,
    routes_by_drone_id: Mapping[int, Route],
    max_turns: int = 1000,
) -> tuple[str, ...]:
    """Run known routes until delivery and return evaluator-style lines."""
    state = SimulationState.initial(parsed_map)
    lines: list[str] = []
    for _ in range(max_turns):
        delivered = (
            isinstance(drone.location, Delivered)
            for drone in state.drones
        )
        if all(delivered):
            return tuple(lines)
        result = SimulationEngine.advance_one_turn(state, routes_by_drone_id)
        line = format_turn(result.facts)
        if not line:
            raise RuntimeError("known-route simulation made no progress")
        lines.append(line)
        state = result.state
    raise RuntimeError("known-route simulation exceeded max_turns")
