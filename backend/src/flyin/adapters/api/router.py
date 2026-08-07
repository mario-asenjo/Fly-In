"""Versioned HTTP router composition."""

from fastapi import APIRouter

from .routers.health import health_router


api_v1_router = APIRouter(prefix="/api/v1")
api_v1_router.include_router(health_router)
