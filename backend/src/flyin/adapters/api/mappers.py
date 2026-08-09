"""Map application projections to HTTP response DTOs."""

from ...application.solver import (
    ConnectionView,
    MapView,
    MetricsView,
    MovementView,
    SolveResult,
    SolveWarning,
    TurnView,
    ZoneView,
)
from .schemas import (
    ConnectionResponse,
    MapResponse,
    MetricsResponse,
    MovementResponse,
    SolveResponse,
    TurnResponse,
    WarningResponse,
    ZoneResponse,
)


def zone_views_to_responses(
    zones: tuple[ZoneView, ...],
) -> list[ZoneResponse]:
    """Map application zone projections to HTTP DTOs."""
    return [
        ZoneResponse(
            name=zone.name,
            x=zone.x,
            y=zone.y,
            kind=zone.kind,
            color=zone.color,
            capacity=zone.capacity,
        )
        for zone in zones
    ]


def connections_to_responses(
    connections: tuple[ConnectionView, ...],
) -> list[ConnectionResponse]:
    """Map application connection projections to HTTP DTOs."""
    return [
        ConnectionResponse(
            left=connection.left,
            right=connection.right,
            capacity=connection.capacity,
        )
        for connection in connections
    ]


def map_view_to_response(map_view: MapView) -> MapResponse:
    """Map the solved map projection to an HTTP DTO."""
    return MapResponse(
        drone_count=map_view.drone_count,
        start=map_view.start,
        end=map_view.end,
        zones=zone_views_to_responses(map_view.zones),
        connections=connections_to_responses(map_view.connections),
    )


def movement_views_to_responses(
    movements: tuple[MovementView, ...],
) -> list[MovementResponse]:
    """Map application movement projections to HTTP DTOs."""
    return [
        MovementResponse(
            drone_id=movement.drone_id,
            token=movement.token,
            origin=movement.origin,
            origin_color=movement.origin_color,
            destination=movement.destination,
            destination_color=movement.destination_color,
            path_cost=movement.path_cost,
        )
        for movement in movements
    ]


def turn_views_to_responses(
    turns: tuple[TurnView, ...],
) -> list[TurnResponse]:
    """Map completed turn projections to HTTP DTOs."""
    return [
        TurnResponse(
            number=turn.number,
            line=turn.line,
            movements=movement_views_to_responses(turn.movements),
        )
        for turn in turns
    ]


def metrics_view_to_response(metrics: MetricsView) -> MetricsResponse:
    """Map solver metrics to an HTTP DTO."""
    return MetricsResponse(
        moved_drones_per_turn=list(metrics.moved_drones_per_turn),
        average_turns_per_drone=metrics.average_turns_per_drone,
        total_path_cost=metrics.total_path_cost,
    )


def warnings_to_responses(
    warnings: tuple[SolveWarning, ...],
) -> list[WarningResponse]:
    """Map non-fatal solver warnings to HTTP DTOs."""
    return [
        WarningResponse(
            code=warning.code,
            message=warning.message,
            zone_name=warning.zone_name,
        )
        for warning in warnings
    ]


def result_to_solve_response(result: SolveResult) -> SolveResponse:
    """Map an adapter-neutral solve result to its HTTP response."""
    return SolveResponse(
        turn_count=result.turn_count,
        map=map_view_to_response(result.map_view),
        turns=turn_views_to_responses(result.turns),
        metrics=metrics_view_to_response(result.metrics),
        movement_lines=list(result.movement_lines),
        warnings=warnings_to_responses(result.warnings),
    )
