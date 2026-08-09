"""Stable HTTP error handling for the Fly-In API adapter."""

from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from ...application import SolveError

ErrorDetails = dict[str, int | str]

_SOLVE_STATUS = {
    "MAP_PARSE_ERROR": 422,
    "NO_ROUTE": 422,
    "SCHEDULE_DEADLOCK": 422,
    "INVALID_SCHEDULE": 422,
    "SOLVE_FAILED": 422,
}


class ApiError(RuntimeError):
    """Expected API-boundary failure with a public status and payload."""

    def __init__(
        self,
        status_code: int,
        code: str,
        message: str,
        details: ErrorDetails | None = None,
    ) -> None:
        super().__init__(message)
        self.status_code = status_code
        self.code = code
        self.message = message
        self.details = details or {}


def register_error_handlers(app: FastAPI) -> None:
    """Register the API adapter's stable error envelope handlers."""
    app.add_exception_handler(ApiError, api_error_handler)
    app.add_exception_handler(SolveError, solve_error_handler)
    app.add_exception_handler(OSError, os_error_handler)
    app.add_exception_handler(RequestValidationError, validation_error_handler)


def error_response(
    status_code: int,
    code: str,
    message: str,
    details: ErrorDetails | None = None,
) -> JSONResponse:
    """Build the stable JSON error envelope."""
    return JSONResponse(
        status_code=status_code,
        content={
            "error": {
                "code": code,
                "message": message,
                "details": details or {},
            }
        },
    )


async def api_error_handler(
    request: Request,
    exc: Exception,
) -> JSONResponse:
    """Translate expected API errors to public JSON."""
    if not isinstance(exc, ApiError):
        return error_response(
            status.HTTP_500_INTERNAL_SERVER_ERROR,
            "INTERNAL_SERVER_ERROR",
            "unexpected API error.",
        )
    return error_response(exc.status_code, exc.code, exc.message, exc.details)


async def solve_error_handler(
    request: Request,
    exc: Exception,
) -> JSONResponse:
    """Translate application solver failures to public JSON."""
    if not isinstance(exc, SolveError):
        return error_response(
            status.HTTP_500_INTERNAL_SERVER_ERROR,
            "INTERNAL_SERVER_ERROR",
            "unexpected solver error.",
        )
    details: ErrorDetails = {}
    if exc.line is not None:
        details["line"] = exc.line
    return error_response(
        _SOLVE_STATUS.get(exc.code, status.HTTP_500_INTERNAL_SERVER_ERROR),
        exc.code,
        exc.message,
        details,
    )


async def os_error_handler(
    request: Request,
    exc: Exception,
) -> JSONResponse:
    """Hide server filesystem details behind a stable map-read error."""
    return error_response(
        status.HTTP_500_INTERNAL_SERVER_ERROR,
        "MAP_READ_ERROR",
        "server map file could not be read.",
    )


async def validation_error_handler(
    request: Request,
    exc: Exception,
) -> JSONResponse:
    """Normalize FastAPI request validation errors to the public envelope."""
    field = "request"
    if isinstance(exc, RequestValidationError) and exc.errors():
        location = exc.errors()[0].get("loc", ())
        if isinstance(location, tuple) and location:
            field = str(location[-1])
    return error_response(
        422,
        "REQUEST_VALIDATION_ERROR",
        f"invalid request field: {field}.",
        {"field": field},
    )
