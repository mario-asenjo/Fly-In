from pathlib import Path

import pytest

from flyin.domain import CapacityLimit, ZoneType
from flyin.parsing import MapParseError, MapParser

PROJECT_ROOT = Path(__file__).parents[1]
FIXTURES = PROJECT_ROOT / "tests" / "fixtures" / "derived-v15"
OFFICIAL_MAPS = PROJECT_ROOT / "maps" / "maps-v1.5-added-before-m0"


def test_interprets_zone_color_and_effective_capacities() -> None:
    source = (FIXTURES / "valid_zone_semantics.txt").read_text(
        encoding="utf-8"
    )

    parsed_map = MapParser().parse(source)

    normal, blocked, restricted, priority = parsed_map.hubs
    first, second, third, fourth, fifth = parsed_map.connections

    assert parsed_map.start.color == "green"
    assert parsed_map.start.capacity is CapacityLimit.UNLIMITED
    assert parsed_map.start.zone_type is ZoneType.NORMAL
    assert parsed_map.end.color == "red"
    assert parsed_map.end.capacity is CapacityLimit.UNLIMITED
    assert parsed_map.start.metadata == (
        ("color", "green"),
        ("max_drones", "1"),
        ("zone", "blocked"),
    )

    assert (normal.zone_type, normal.color, normal.capacity) == (
        ZoneType.NORMAL,
        None,
        1,
    )
    assert (blocked.zone_type, blocked.color, blocked.capacity) == (
        ZoneType.BLOCKED,
        "black",
        2,
    )
    assert (restricted.zone_type, restricted.color, restricted.capacity) == (
        ZoneType.RESTRICTED,
        "orange",
        1,
    )
    assert (priority.zone_type, priority.color, priority.capacity) == (
        ZoneType.PRIORITY,
        "gold",
        3,
    )

    assert (first.capacity, second.capacity, third.capacity) == (2, 1, 3)
    assert (fourth.capacity, fifth.capacity) == (1, 1)


def test_parses_the_actual_official_map_with_its_leading_comment() -> None:
    source = (OFFICIAL_MAPS / "easy" / "01_linear_path.txt").read_text(
        encoding="utf-8"
    )

    assert source.splitlines()[0] == "# Easy Level 1: Simple linear path"

    parsed_map = MapParser().parse(source)
    first, second = parsed_map.hubs

    assert parsed_map.drone_count == 2
    assert parsed_map.start.color == "green"
    assert parsed_map.start.capacity is CapacityLimit.UNLIMITED
    assert (first.zone_type, first.color, first.capacity) == (
        ZoneType.NORMAL,
        "blue",
        1,
    )
    assert (second.zone_type, second.color, second.capacity) == (
        ZoneType.NORMAL,
        "blue",
        1,
    )
    assert parsed_map.end.color == "red"
    assert parsed_map.end.capacity is CapacityLimit.UNLIMITED
    capacities = tuple(
        connection.capacity for connection in parsed_map.connections
    )
    assert capacities == (1, 1, 1)


def test_parses_all_ten_official_maps_without_modifying_them() -> None:
    paths = tuple(sorted(OFFICIAL_MAPS.glob("*/*.txt")))

    assert len(paths) == 10
    for path in paths:
        source = path.read_text(encoding="utf-8")
        parsed_map = MapParser().parse(source)

        assert parsed_map.start.capacity is CapacityLimit.UNLIMITED
        assert parsed_map.end.capacity is CapacityLimit.UNLIMITED


@pytest.mark.parametrize(
    ("source", "expected_line", "expected_cause"),
    (
        (
            "\n".join(
                (
                    "nb_drones: 1",
                    "start_hub: start 0 0",
                    "hub: bad 1 0 [zone=teleport]",
                    "end_hub: goal 2 0",
                )
            ),
            3,
            "invalid zone type: teleport",
        ),
        (
            (FIXTURES / "invalid_zero_capacity.txt").read_text(
                encoding="utf-8"
            ),
            5,
            "max_drones must be a positive integer",
        ),

        (
            "\n".join(
                (
                    "nb_drones: 1",
                    "start_hub: start 0 0",
                    "end_hub: goal 1 0",
                    "connection: start-goal [max_link_capacity=wide]",
                )
            ),
            4,
            "max_link_capacity must be a positive integer",
        ),
    ),
)
def test_rejects_invalid_zone_types_and_capacities(
    source: str,
    expected_line: int,
    expected_cause: str,
) -> None:
    with pytest.raises(MapParseError) as caught:
        MapParser().parse(source)

    assert caught.value.line_number == expected_line
    assert caught.value.cause == expected_cause
