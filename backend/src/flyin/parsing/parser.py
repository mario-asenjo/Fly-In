"""Parse Fly-In map text into typed domain objects."""

import re
from enum import StrEnum

from flyin.domain import (
    CapacityLimit,
    Connection,
    Metadata,
    ParsedMap,
    Zone,
    ZoneType,
)

_INTEGER = re.compile(r"[+-]?[0-9]+\Z")
_POSITIVE_INTEGER = re.compile(r"[0-9]+\Z")
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


class MapParser:
    """Convert Fly-In map text into typed domain objects."""

    _ZONE_METADATA = frozenset(("zone", "color", "max_drones"))
    _CONNECTION_METADATA = frozenset(("max_link_capacity",))

    def parse(self, source: str) -> ParsedMap:
        """Parse declarations while preserving physical diagnostics."""
        physical_lines = source.splitlines()
        significant_lines = [
            (line_number, stripped)
            for line_number, line in enumerate(physical_lines, start=1)
            if (stripped := line.partition("#")[0].strip())
        ]
        if not significant_lines:
            raise MapParseError(
                MapParseErrorCode.MISSING_DRONE_COUNT,
                max(1, len(physical_lines)),
                "missing nb_drones declaration",
            )

        drone_line_number, drone_line = significant_lines[0]
        drone_count = self._parse_drone_count(
            drone_line_number,
            drone_line,
        )
        declaration_lines = significant_lines[1:]
        zones: dict[str, Zone] = {}
        hubs: list[Zone] = []
        connections: list[Connection] = []
        connection_identities: set[tuple[str, str]] = set()
        start: Zone | None = None
        end: Zone | None = None

        for line_number, line in declaration_lines:
            if line.startswith("start_hub: "):
                zone = self._parse_zone(
                    line_number,
                    line,
                    "start_hub: ",
                    is_terminal=True,
                )
                if start is not None:
                    raise MapParseError(
                        MapParseErrorCode.DUPLICATE_START,
                        line_number,
                        "duplicate start_hub",
                        line,
                    )
                self._register_zone(line_number, line, zone, zones)
                start = zone
            elif line.startswith("end_hub: "):
                zone = self._parse_zone(
                    line_number,
                    line,
                    "end_hub: ",
                    is_terminal=True,
                )
                if end is not None:
                    raise MapParseError(
                        MapParseErrorCode.DUPLICATE_END,
                        line_number,
                        "duplicate end_hub",
                        line,
                    )
                self._register_zone(line_number, line, zone, zones)
                end = zone
            elif line.startswith("hub: "):
                hub = self._parse_zone(line_number, line, "hub: ")
                self._register_zone(line_number, line, hub, zones)
                hubs.append(hub)
            elif line.startswith("connection: "):
                connection = self._parse_connection(
                    line_number,
                    line,
                    zones,
                )
                if connection.identity in connection_identities:
                    left_name, right_name = connection.identity
                    cause = (
                        "duplicate connection: "
                        f"{left_name}-{right_name}"
                    )
                    raise MapParseError(
                        MapParseErrorCode.DUPLICATE_CONNECTION,
                        line_number,
                        cause,
                        line,
                    )
                connection_identities.add(connection.identity)
                connections.append(connection)
            elif line.startswith("nb_drones:"):
                raise MapParseError(
                    MapParseErrorCode.INVALID_DRONE_COUNT,
                    line_number,
                    "duplicate nb_drones declaration",
                    line,
                )
            else:
                raise MapParseError(
                    MapParseErrorCode.UNKNOWN_DECLARATION,
                    line_number,
                    "unknown declaration",
                    line,
                )

        eof_line_number = max(1, len(physical_lines))
        if start is None:
            raise MapParseError(
                MapParseErrorCode.MISSING_START,
                eof_line_number,
                "missing start_hub",
            )
        if end is None:
            raise MapParseError(
                MapParseErrorCode.MISSING_END,
                eof_line_number,
                "missing end_hub",
            )
        return ParsedMap(
            drone_count=drone_count,
            start=start,
            end=end,
            hubs=tuple(hubs),
            connections=tuple(connections),
        )

    @staticmethod
    def _parse_drone_count(line_number: int, line: str) -> int:
        prefix = "nb_drones:"
        if not line.startswith(prefix):
            raise MapParseError(
                MapParseErrorCode.MISSING_DRONE_COUNT,
                line_number,
                "expected nb_drones declaration",
                line,
            )
        if not line.startswith(prefix + " "):
            raise MapParseError(
                MapParseErrorCode.INVALID_DRONE_COUNT,
                line_number,
                "nb_drones must use nb_drones: <positive_integer>",
                line,
            )
        raw_count = line.removeprefix(prefix).strip()
        if not _POSITIVE_INTEGER.fullmatch(raw_count):
            raise MapParseError(
                MapParseErrorCode.INVALID_DRONE_COUNT,
                line_number,
                "nb_drones must be a positive integer",
                line,
            )
        try:
            drone_count = int(raw_count)
        except ValueError:
            raise MapParseError(
                MapParseErrorCode.INVALID_DRONE_COUNT,
                line_number,
                "nb_drones is too large",
                line,
            ) from None
        if drone_count <= 0:
            raise MapParseError(
                MapParseErrorCode.INVALID_DRONE_COUNT,
                line_number,
                "nb_drones must be a positive integer",
                line,
            )
        return drone_count

    @staticmethod
    def _register_zone(
        line_number: int,
        line: str,
        zone: Zone,
        zones: dict[str, Zone],
    ) -> None:
        if zone.name in zones:
            raise MapParseError(
                MapParseErrorCode.DUPLICATE_ZONE,
                line_number,
                f"duplicate zone name: {zone.name}",
                line,
            )
        zones[zone.name] = zone

    @staticmethod
    def _parse_connection(
        line_number: int,
        line: str,
        zones: dict[str, Zone],
    ) -> Connection:
        structural, metadata = MapParser._split_metadata(
            line_number,
            line,
            MapParser._CONNECTION_METADATA,
        )
        endpoints = structural.removeprefix("connection: ")
        if endpoints.count("-") != 1 or not all(endpoints.split("-")):
            raise MapParseError(
                MapParseErrorCode.INVALID_FIELD_COUNT,
                line_number,
                "connection requires two zone names",
                line,
            )
        left_name, right_name = endpoints.split("-")
        for zone_name in (left_name, right_name):
            MapParser._validate_zone_name(
                line_number,
                line,
                zone_name,
            )
        if left_name == right_name:
            raise MapParseError(
                MapParseErrorCode.SELF_CONNECTION,
                line_number,
                "connection cannot link a zone to itself",
                line,
            )
        for zone_name in (left_name, right_name):
            if zone_name not in zones:
                cause = f"unknown connection zone: {zone_name}"
                raise MapParseError(
                    MapParseErrorCode.UNKNOWN_CONNECTION_ZONE,
                    line_number,
                    cause,
                    line,
                )
        capacity = MapParser._parse_capacity(
            line_number,
            line,
            metadata,
            "max_link_capacity",
        )
        return Connection(
            zones[left_name],
            zones[right_name],
            metadata,
            capacity,
        )

    @staticmethod
    def _parse_zone(
        line_number: int,
        line: str,
        prefix: str,
        is_terminal: bool = False,
    ) -> Zone:
        structural, metadata = MapParser._split_metadata(
            line_number,
            line,
            MapParser._ZONE_METADATA,
        )
        fields = structural.removeprefix(prefix).split()
        if len(fields) != 3:
            raise MapParseError(
                MapParseErrorCode.INVALID_FIELD_COUNT,
                line_number,
                "zone requires name and two coordinates",
                line,
            )
        name, raw_x, raw_y = fields
        MapParser._validate_zone_name(line_number, line, name)
        if not _INTEGER.fullmatch(raw_x) or not _INTEGER.fullmatch(raw_y):
            raise MapParseError(
                MapParseErrorCode.INVALID_COORDINATE,
                line_number,
                "zone coordinates must be integers",
                line,
            )
        try:
            x = int(raw_x)
            y = int(raw_y)
        except ValueError:
            raise MapParseError(
                MapParseErrorCode.INVALID_COORDINATE,
                line_number,
                "coordinates are too large",
                line,
            ) from None
        zone_type = MapParser._parse_zone_type(
            line_number,
            line,
            metadata,
        )
        declared_capacity = 1
        if not is_terminal:
            declared_capacity = MapParser._parse_capacity(
                line_number,
                line,
                metadata,
                "max_drones",
            )
        effective_zone_type = (
            ZoneType.NORMAL if is_terminal else zone_type
        )
        effective_capacity = (
            CapacityLimit.UNLIMITED
            if is_terminal
            else declared_capacity
        )
        return Zone(
            name,
            x,
            y,
            metadata,
            effective_zone_type,
            dict(metadata).get("color"),
            effective_capacity,
        )

    @staticmethod
    def _validate_zone_name(
        line_number: int,
        line: str,
        name: str,
    ) -> None:
        contains_space = any(character.isspace() for character in name)
        if not name or "-" in name or contains_space:
            raise MapParseError(
                MapParseErrorCode.INVALID_ZONE_NAME,
                line_number,
                f"invalid zone name: {name}",
                line,
            )

    @staticmethod
    def _parse_zone_type(
        line_number: int,
        line: str,
        metadata: Metadata,
    ) -> ZoneType:
        raw_zone_type = dict(metadata).get("zone", ZoneType.NORMAL)
        try:
            return ZoneType(raw_zone_type)
        except ValueError as error:
            raise MapParseError(
                MapParseErrorCode.INVALID_ZONE_TYPE,
                line_number,
                f"invalid zone type: {raw_zone_type}",
                line,
            ) from error

    @staticmethod
    def _parse_capacity(
        line_number: int,
        line: str,
        metadata: Metadata,
        key: str,
    ) -> int:
        raw_capacity = dict(metadata).get(key)
        if raw_capacity is None:
            return 1
        if not _POSITIVE_INTEGER.fullmatch(raw_capacity):
            raise MapParseError(
                MapParseErrorCode.INVALID_CAPACITY,
                line_number,
                f"{key} must be a positive integer",
                line,
            )
        try:
            capacity = int(raw_capacity)
        except ValueError:
            raise MapParseError(
                MapParseErrorCode.INVALID_CAPACITY,
                line_number,
                f"{key} is too large",
                line,
            ) from None
        if capacity <= 0:
            raise MapParseError(
                MapParseErrorCode.INVALID_CAPACITY,
                line_number,
                f"{key} must be a positive integer",
                line,
            )
        return capacity

    @staticmethod
    def _split_metadata(
        line_number: int,
        line: str,
        allowed_keys: frozenset[str],
    ) -> tuple[str, Metadata]:
        opening_count = line.count("[")
        closing_count = line.count("]")
        if opening_count == 0 and closing_count == 0:
            return line, ()
        opening = line.find("[")
        valid_block = (
            opening_count == 1
            and closing_count == 1
            and opening > 0
            and line[opening - 1].isspace()
            and line.endswith("]")
        )
        if not valid_block:
            raise MapParseError(
                MapParseErrorCode.MALFORMED_METADATA,
                line_number,
                "metadata requires one balanced trailing block",
                line,
            )

        structural = line[:opening].rstrip()
        raw_metadata = line[opening + 1:-1]
        tokens = raw_metadata.split()
        if not tokens:
            raise MapParseError(
                MapParseErrorCode.MALFORMED_METADATA,
                line_number,
                "metadata block cannot be empty",
                line,
            )

        metadata: list[tuple[str, str]] = []
        seen_keys: set[str] = set()
        for token in tokens:
            if token.count("=") != 1:
                raise MapParseError(
                    MapParseErrorCode.MALFORMED_METADATA,
                    line_number,
                    "metadata must use non-empty key=value tokens",
                    line,
                )
            key, value = token.split("=")
            if not key or not value:
                raise MapParseError(
                    MapParseErrorCode.MALFORMED_METADATA,
                    line_number,
                    "metadata must use non-empty key=value tokens",
                    line,
                )
            if key in seen_keys:
                raise MapParseError(
                    MapParseErrorCode.DUPLICATE_METADATA,
                    line_number,
                    f"duplicate metadata key: {key}",
                    line,
                )
            if key not in allowed_keys:
                raise MapParseError(
                    MapParseErrorCode.UNKNOWN_METADATA,
                    line_number,
                    f"unknown metadata key: {key}",
                    line,
                )
            seen_keys.add(key)
            metadata.append((key, value))

        return structural, tuple(sorted(metadata))
