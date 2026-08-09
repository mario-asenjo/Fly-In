"""HTTP request and response schemas for the Fly-In API."""

from typing import Literal

from pydantic import BaseModel


class HealthResponse(BaseModel):
    """Successful health-check response."""

    status: Literal["ok"]


class ErrorBody(BaseModel):
    """Stable API error payload."""

    code: str
    message: str
    details: dict[str, int | str]


class ErrorResponse(BaseModel):
    """Stable API error envelope."""

    error: ErrorBody


class MapCatalogOptionResponse(BaseModel):
    """One selectable map exposed by the HTTP catalog."""

    index: int
    display_path: str


class MapCatalogResponse(BaseModel):
    """Available official maps exposed to API clients."""

    maps: list[MapCatalogOptionResponse]


class ZoneResponse(BaseModel):
    """One zone in the solved map projection."""

    name: str
    x: int
    y: int
    kind: str
    color: str | None
    capacity: int | str


class ConnectionResponse(BaseModel):
    """One bidirectional physical map connection."""

    left: str
    right: str
    capacity: int


class MapResponse(BaseModel):
    """Solved map projection for HTTP clients."""

    drone_count: int
    start: str
    end: str
    zones: list[ZoneResponse]
    connections: list[ConnectionResponse]


class MovementResponse(BaseModel):
    """One drone movement within a completed turn."""

    drone_id: int
    token: str
    origin: str
    origin_color: str | None
    destination: str
    destination_color: str | None
    path_cost: int


class TurnResponse(BaseModel):
    """One completed simulation turn."""

    number: int
    line: str
    movements: list[MovementResponse]


class MetricsResponse(BaseModel):
    """Subject-level metrics for a solved schedule."""

    moved_drones_per_turn: list[int]
    average_turns_per_drone: float
    total_path_cost: int


class WarningResponse(BaseModel):
    """Non-fatal solver warning."""

    code: str
    message: str
    zone_name: str | None


class SolveResponse(BaseModel):
    """Synchronous simulation response."""

    turn_count: int
    map: MapResponse
    turns: list[TurnResponse]
    metrics: MetricsResponse
    movement_lines: list[str]
    warnings: list[WarningResponse]
