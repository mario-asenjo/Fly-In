"""FastAPI application factory for Fly-In."""

from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from .errors import register_error_handlers
from .router import api_v1_router


def frontend_root() -> Path:
    """Return the repository frontend directory."""
    return Path(__file__).parents[5] / "frontend"


def create_app() -> FastAPI:
    """Build and configure a fresh Fly-In HTTP application."""
    app = FastAPI(
        title="Fly-In API",
        version="0.1.0",
        description="HTTP adapter for the Fly-In drone simulator.",
    )
    register_error_handlers(app)
    app.include_router(api_v1_router)

    root = frontend_root()
    app.mount(
        "/img",
        StaticFiles(directory=root / "img"),
        name="frontend-images",
    )

    @app.get("/", include_in_schema=False, response_class=FileResponse)
    def frontend_index() -> FileResponse:
        """Serve the native Fly-In browser client."""
        return FileResponse(root / "index.html")

    @app.get(
        "/style.css",
        include_in_schema=False,
        response_class=FileResponse,
    )
    def frontend_styles() -> FileResponse:
        """Serve the native client stylesheet."""
        return FileResponse(root / "style.css", media_type="text/css")

    @app.get(
        "/app.js",
        include_in_schema=False,
        response_class=FileResponse,
    )
    def frontend_script() -> FileResponse:
        """Serve the native client JavaScript."""
        return FileResponse(root / "app.js", media_type="text/javascript")

    return app
