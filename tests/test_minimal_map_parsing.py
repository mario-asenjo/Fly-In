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
    assert parsed_map.end.name == "end"
    connection_names = {
        (connection.left.name, connection.right.name)
        for connection in parsed_map.connections
    }

    assert connection_names == {
        ("start", "end")
    }
