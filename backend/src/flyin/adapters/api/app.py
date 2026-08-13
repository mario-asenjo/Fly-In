"""FastAPI application factory for Fly-In."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .errors import register_error_handlers
from .router import api_v1_router

FRONTEND_ORIGINS = [
    "http://127.0.0.1:8080",
    "http://localhost:8080",
]


def create_app() -> FastAPI:
    """Build and configure a fresh Fly-In HTTP application."""
    app = FastAPI(
        title="Fly-In API",
        version="0.1.0",
        description="HTTP adapter for the Fly-In drone simulator.",
    )
    app.add_middleware(
        CORSMiddleware,
        allow_origins=FRONTEND_ORIGINS,
        allow_methods=["GET", "POST"],
        allow_headers=["Accept", "Content-Type"],
    )
    register_error_handlers(app)
    app.include_router(api_v1_router)
    return app
