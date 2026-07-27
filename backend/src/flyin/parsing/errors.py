"""Stable parsing errors for Fly-In map input."""

from enum import StrEnum

_MAX_EXCERPT_LENGTH = 120


class MapParseErrorCode(StrEnum):
    """Stable categories for map input failures."""

    MISSING_DRONE_COUNT = "MISSING_DRONE_COUNT"
    INVALID_DRONE_COUNT = "INVALID_DRONE_COUNT"
    UNKNOWN_DECLARATION = "UNKNOWN_DECLARATION"
    INVALID_FIELD_COUNT = "INVALID_FIELD_COUNT"
    INVALID_COORDINATE = "INVALID_COORDINATE"
    INVALID_ZONE_NAME = "INVALID_ZONE_NAME"
    DUPLICATE_ZONE = "DUPLICATE_ZONE"
    DUPLICATE_START = "DUPLICATE_START"
    DUPLICATE_END = "DUPLICATE_END"
    MISSING_START = "MISSING_START"
    MISSING_END = "MISSING_END"
    MALFORMED_METADATA = "MALFORMED_METADATA"
    UNKNOWN_METADATA = "UNKNOWN_METADATA"
    DUPLICATE_METADATA = "DUPLICATE_METADATA"
    INVALID_ZONE_TYPE = "INVALID_ZONE_TYPE"
    INVALID_CAPACITY = "INVALID_CAPACITY"
    UNKNOWN_CONNECTION_ZONE = "UNKNOWN_CONNECTION_ZONE"
    DUPLICATE_CONNECTION = "DUPLICATE_CONNECTION"
    SELF_CONNECTION = "SELF_CONNECTION"


class MapParseError(ValueError):
    """A stable parsing failure tied to a physical source line."""

    def __init__(
        self,
        code: MapParseErrorCode,
        line_number: int,
        cause: str,
        excerpt: str | None = None,
    ) -> None:
        safe_excerpt = excerpt.strip() if excerpt else None
        if (
            safe_excerpt is not None
            and len(safe_excerpt) > _MAX_EXCERPT_LENGTH
        ):
            safe_excerpt = safe_excerpt[:117] + "..."
        message = f"{code}: line {line_number}: {cause}"
        if safe_excerpt is not None:
            message += f": {safe_excerpt}"
        super().__init__(message)
        self.code = code
        self.line_number = line_number
        self.cause = cause
        self.excerpt = safe_excerpt
