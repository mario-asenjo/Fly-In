from dataclasses import FrozenInstanceError

import pytest

from flyin.parsing import MapParseError, MapParser


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


def test_parses_regular_hubs_and_multiple_connections() -> None:
    parsed_map = MapParser().parse(
        "\n".join(
            (
                "nb_drones: 4",
                "start_hub: start 0 0",
                "hub: alpha 1 -1",
                "hub: beta 2 1",
                "end_hub: end 3 0",
                "connection: start-alpha",
                "connection: alpha-beta",
                "connection: beta-end",
            )
        )
    )

    alpha, beta = parsed_map.hubs
    first, second, third = parsed_map.connections

    assert parsed_map.drone_count == 4
    assert (alpha.name, alpha.x, alpha.y) == ("alpha", 1, -1)
    assert (beta.name, beta.x, beta.y) == ("beta", 2, 1)
    assert first.left is parsed_map.start
    assert first.right is alpha
    assert second.left is alpha
    assert second.right is beta
    assert third.left is beta
    assert third.right is parsed_map.end


def test_ignores_comments_and_blanks_and_parses_ordered_metadata() -> None:
    parsed_map = MapParser().parse(
        "\n".join(
            (
                "# map title",
                "",
                "nb_drones: 2",
                "# zones",
                "start_hub: start 0 0 [color=green]",
                "hub: alpha 1 0 [max_drones=2 color=blue]",
                "",
                "hub: beta 2 0 [color=blue max_drones=2]",
                "end_hub: end 3 0",
                "# links",
                "connection: start-alpha [max_link_capacity=3]",
                "connection: alpha-beta",
                "connection: beta-end",
            )
        )
    )

    alpha, beta = parsed_map.hubs
    first, second, third = parsed_map.connections

    assert parsed_map.start.metadata == (("color", "green"),)
    assert alpha.metadata == beta.metadata == (
        ("color", "blue"),
        ("max_drones", "2"),
    )
    assert parsed_map.end.metadata == ()
    assert first.metadata == (("max_link_capacity", "3"),)
    assert second.metadata == third.metadata == ()


def test_reports_the_physical_line_for_an_unknown_declaration() -> None:
    source = "\n".join(
        (
            "# title",
            "",
            "nb_drones: 1",
            "start_hub: start 0 0",
            "unknown: surprise",
        )
    )

    with pytest.raises(MapParseError) as caught:
        MapParser().parse(source)

    assert caught.value.line_number == 5
