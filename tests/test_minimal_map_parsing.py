from dataclasses import FrozenInstanceError

import pytest

from flyin.parsing import MapParser


def test_parses_the_smallest_valid_linear_map() -> None:
    parsed_map = MapParser().parse(
        "\n".join(
            (
                "nb_drones: 1",
                "start_hub: start 0 0",
                "end_hub: end 1 0",
                "connection: start-end",
            )
        )
    )

    assert parsed_map.drone_count == 1
    assert parsed_map.start.name == "start"
    assert (parsed_map.start.x, parsed_map.start.y) == (0, 0)
    assert parsed_map.end.name == "end"
    assert (parsed_map.end.x, parsed_map.end.y) == (1, 0)
    connection, = parsed_map.connections

    assert connection.left is parsed_map.start
    assert connection.right is parsed_map.end

    with pytest.raises(FrozenInstanceError):
        setattr(parsed_map, "drone_count", 2)
