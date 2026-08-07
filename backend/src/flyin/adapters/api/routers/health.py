"""Health-check HTTP routes."""

from fastapi import APIRouter

from ..schemas import HealthResponse


health_router = APIRouter(
    prefix="/health",
    tags=["health"]
)


@health_router.get("", response_model=HealthResponse)
def health() -> HealthResponse:
    """Report that the HTTP adapter is available."""
    return HealthResponse(status="ok")
