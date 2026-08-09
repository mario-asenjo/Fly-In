"""FastAPI application factory for Fly-In."""

from fastapi import FastAPI

from .errors import register_error_handlers
from .router import api_v1_router


def create_app() -> FastAPI:
    """Build and configure a fresh Fly-In HTTP application."""
    app = FastAPI(
        title="Fly-In API",
        version="0.1.0",
        description="HTTP adapter for the Fly-In drone simulator.",
    )
    register_error_handlers(app)
    app.include_router(api_v1_router)
    return app
