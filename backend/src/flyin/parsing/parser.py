"""Parser for the currently supported Fly-In map contract."""

from flyin.domain import (
    CapacityLimit,
    Connection,
    Metadata,
    ParsedMap,
    Zone,
    ZoneType,
)


class MapParseError(ValueError):
    """A parsing failure tied to its physical source line."""

    def __init__(self, line_number: int, cause: str) -> None:
        super().__init__(f"line {line_number}: {cause}")
        self.line_number = line_number
        self.cause = cause


class MapParser:
    """Convert Fly-In map text into typed domain objects."""

    def parse(self, source: str) -> ParsedMap:
        """Parse significant lines, raw metadata, zones, and connections."""
        physical_lines = source.splitlines()
        significant_lines = [
            (line_number, stripped)
            for line_number, line in enumerate(physical_lines, start=1)
            if (stripped := line.partition("#")[0].strip())
        ]
        (drone_line_number, drone_line), *declaration_lines = significant_lines
        if not drone_line.startswith("nb_drones: "):
            raise MapParseError(drone_line_number, "expected nb_drones declaration")
        drone_count = int(drone_line.removeprefix("nb_drones: "))
        zones: dict[str, Zone] = {}
        hubs: list[Zone] = []
        connections: list[Connection] = []
        connection_identities: set[tuple[str, str]] = set()
        start: Zone | None = None
        end: Zone | None = None

        for line_number, line in declaration_lines:
            if line.startswith("start_hub: "):
                if start is not None:
                    raise MapParseError(line_number, "duplicate start_hub")
                start = self._parse_zone(
                    line_number,
                    line,
                    "start_hub: ",
                    is_terminal=True,
                )
                self._register_zone(line_number, start, zones)
            elif line.startswith("end_hub: "):
                if end is not None:
                    raise MapParseError(line_number, "duplicate end_hub")
                end = self._parse_zone(
                    line_number,
                    line,
                    "end_hub: ",
                    is_terminal=True,
                )
                self._register_zone(line_number, end, zones)
            elif line.startswith("hub: "):
                hub = self._parse_zone(line_number, line, "hub: ")
                self._register_zone(line_number, hub, zones)
                hubs.append(hub)
            elif line.startswith("connection: "):
                connection = self._parse_connection(line_number, line, zones)
                if connection.identity in connection_identities:
                    left_name, right_name = connection.identity
                    raise MapParseError(
                        line_number,
                        f"duplicate connection: {left_name}-{right_name}",
                    )
                connection_identities.add(connection.identity)
                connections.append(connection)
            else:
                raise MapParseError(line_number, "unknown declaration")

        eof_line_number = max(1, len(physical_lines))
        if start is None:
            raise MapParseError(eof_line_number, "missing start_hub")
        if end is None:
            raise MapParseError(eof_line_number, "missing end_hub")
        return ParsedMap(
            drone_count=drone_count,
            start=start,
            end=end,
            hubs=tuple(hubs),
            connections=tuple(connections),
        )

    @staticmethod
    def _register_zone(
        line_number: int,
        zone: Zone,
        zones: dict[str, Zone],
    ) -> None:
        if zone.name in zones:
            raise MapParseError(
                line_number,
                f"duplicate zone name: {zone.name}",
            )
        zones[zone.name] = zone

    @staticmethod
    def _parse_connection(
        line_number: int,
        line: str,
        zones: dict[str, Zone],
    ) -> Connection:
        structural, metadata = MapParser._split_metadata(line_number, line)
        left_name, right_name = structural.removeprefix("connection: ").split("-")
        for zone_name in (left_name, right_name):
            if zone_name not in zones:
                raise MapParseError(
                    line_number,
                    f"unknown connection zone: {zone_name}",
                )
        capacity = MapParser._parse_capacity(
            line_number,
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
        structural, metadata = MapParser._split_metadata(line_number, line)
        name, x, y = structural.removeprefix(prefix).split()
        zone_type = MapParser._parse_zone_type(line_number, metadata)
        declared_capacity = MapParser._parse_capacity(
            line_number,
            metadata,
            "max_drones",
        )
        effective_zone_type = ZoneType.NORMAL if is_terminal else zone_type
        effective_capacity = (
            CapacityLimit.UNLIMITED if is_terminal else declared_capacity
        )
        return Zone(
            name,
            int(x),
            int(y),
            metadata,
            effective_zone_type,
            dict(metadata).get("color"),
            effective_capacity,
        )

    @staticmethod
    def _parse_zone_type(line_number: int, metadata: Metadata) -> ZoneType:
        raw_zone_type = dict(metadata).get("zone", ZoneType.NORMAL)
        try:
            return ZoneType(raw_zone_type)
        except ValueError as error:
            raise MapParseError(
                line_number,
                f"invalid zone type: {raw_zone_type}",
            ) from error

    @staticmethod
    def _parse_capacity(
        line_number: int,
        metadata: Metadata,
        key: str,
    ) -> int:
        raw_capacity = dict(metadata).get(key)
        if raw_capacity is None:
            return 1
        try:
            capacity = int(raw_capacity)
        except ValueError as error:
            raise MapParseError(
                line_number,
                f"{key} must be a positive integer",
            ) from error
        if capacity <= 0:
            raise MapParseError(
                line_number,
                f"{key} must be a positive integer",
            )
        return capacity

    @staticmethod
    def _split_metadata(line_number: int, line: str) -> tuple[str, Metadata]:
        structural, separator, metadata_block = line.partition(" [")
        if not separator:
            return line, ()
        if not metadata_block.endswith("]"):
            raise MapParseError(line_number, "unclosed metadata block")

        metadata: list[tuple[str, str]] = []
        for token in metadata_block[:-1].split():
            key, equals, value = token.partition("=")
            if not equals:
                raise MapParseError(line_number, "metadata must use key=value")
            metadata.append((key, value))

        return structural, tuple(sorted(metadata))
