"""Parser for the minimal Fly-In map contract."""

from flyin.domain import Connection, ParsedMap, Zone


class MapParser:
    """Convert Fly-In map text into typed domain objects."""

    def parse(self, source: str) -> ParsedMap:
        """Parse the smallest valid linear Fly-In map."""
        drone_line, start_line, end_line, connection_line = source.splitlines()
        drone_count = int(drone_line.removeprefix("nb_drones: "))
        start = self._parse_zone(start_line, "start_hub: ")
        end = self._parse_zone(end_line, "end_hub: ")
        left_name, right_name = connection_line.removeprefix(
            "connection: "
        ).split("-")
        zones = {start.name: start, end.name: end}
        connection = Connection(zones[left_name], zones[right_name])

        return ParsedMap(drone_count, start, end, (connection,))

    @staticmethod
    def _parse_zone(line: str, prefix: str) -> Zone:
        name, x, y = line.removeprefix(prefix).split()
        return Zone(name, int(x), int(y))
