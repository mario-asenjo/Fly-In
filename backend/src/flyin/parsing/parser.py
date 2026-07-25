"""Parser for the currently supported Fly-In map contract."""

from flyin.domain import Connection, Metadata, ParsedMap, Zone


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
        significant_lines = [
            (line_number, stripped)
            for line_number, line in enumerate(source.splitlines(), start=1)
            if (stripped := line.strip()) and not stripped.startswith("#")
        ]
        (drone_line_number, drone_line), *declaration_lines = significant_lines
        if not drone_line.startswith("nb_drones: "):
            raise MapParseError(drone_line_number, "expected nb_drones declaration")
        drone_count = int(drone_line.removeprefix("nb_drones: "))
        zones: dict[str, Zone] = {}
        hubs: list[Zone] = []
        connections: list[Connection] = []
        start: Zone | None = None
        end: Zone | None = None

        for line_number, line in declaration_lines:
            if line.startswith("start_hub: "):
                start = self._parse_zone(line_number, line, "start_hub: ")
                zones[start.name] = start
            elif line.startswith("end_hub: "):
                end = self._parse_zone(line_number, line, "end_hub: ")
                zones[end.name] = end
            elif line.startswith("hub: "):
                hub = self._parse_zone(line_number, line, "hub: ")
                hubs.append(hub)
                zones[hub.name] = hub
            elif line.startswith("connection: "):
                structural, metadata = self._split_metadata(line_number, line)
                left_name, right_name = structural.removeprefix(
                    "connection: "
                ).split("-")
                connections.append(
                    Connection(zones[left_name], zones[right_name], metadata)
                )
            else:
                raise MapParseError(line_number, "unknown declaration")

        assert start is not None and end is not None
        return ParsedMap(
            drone_count=drone_count,
            start=start,
            end=end,
            hubs=tuple(hubs),
            connections=tuple(connections),
        )

    @staticmethod
    def _parse_zone(line_number: int, line: str, prefix: str) -> Zone:
        structural, metadata = MapParser._split_metadata(line_number, line)
        name, x, y = structural.removeprefix(prefix).split()
        return Zone(name, int(x), int(y), metadata)

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
