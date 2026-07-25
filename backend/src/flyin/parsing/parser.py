"""Parser for the minimal Fly-In map contract."""

from flyin.domain import Connection, ParsedMap, Zone


class MapParser:
    """Convert Fly-In map text into typed domain objects."""

    def parse(self, source: str) -> ParsedMap:
        """Parse terminals, regular hubs, and connections from valid map text."""
        drone_line, *declaration_lines = source.splitlines()
        drone_count = int(drone_line.removeprefix("nb_drones: "))
        zones: dict[str, Zone] = {}
        hubs: list[Zone] = []
        connections: list[Connection] = []
        start: Zone | None = None
        end: Zone | None = None

        for line in declaration_lines:
            if line.startswith("start_hub: "):
                start = self._parse_zone(line, "start_hub: ")
                zones[start.name] = start
            elif line.startswith("end_hub: "):
                end = self._parse_zone(line, "end_hub: ")
                zones[end.name] = end
            elif line.startswith("hub: "):
                hub = self._parse_zone(line, "hub: ")
                hubs.append(hub)
                zones[hub.name] = hub
            else:
                left_name, right_name = line.removeprefix(
                    "connection: "
                ).split("-")
                connections.append(Connection(zones[left_name], zones[right_name]))

        assert start is not None and end is not None
        return ParsedMap(
            drone_count=drone_count,
            start=start,
            end=end,
            hubs=tuple(hubs),
            connections=tuple(connections),
        )

    @staticmethod
    def _parse_zone(line: str, prefix: str) -> Zone:
        name, x, y = line.removeprefix(prefix).split()
        return Zone(name, int(x), int(y))
