import pytest

from flyin.domain import CapacityLimit
from flyin.parsing import (
    MapParseError,
    MapParseErrorCode,
    MapParser,
)

_TOO_LONG_INTEGER = "9" * 5000


def _source(*lines: str) -> str:
    return "\n".join(lines)


def _minimal_with(*extra_lines: str) -> str:
    return _source(
        "nb_drones: 1",
        "start_hub: start 0 0",
        "end_hub: end 1 0",
        *extra_lines,
    )


@pytest.mark.parametrize("leading_text", ("", "# optional title\n"))
def test_accepts_an_optional_leading_comment(leading_text: str) -> None:
    parsed_map = MapParser().parse(
        leading_text + _minimal_with("connection: start-end")
    )

    assert parsed_map.drone_count == 1


@pytest.mark.parametrize(
    ("source", "expected_line", "expected_excerpt"),
    (
        ("", 1, None),
        ("# comment only", 1, None),
        ("hub: first 0 0", 1, "hub: first 0 0"),
    ),
)
def test_reports_a_missing_drone_count(
    source: str,
    expected_line: int,
    expected_excerpt: str | None,
) -> None:
    with pytest.raises(MapParseError) as caught:
        MapParser().parse(source)

    error = caught.value
    assert error.code is MapParseErrorCode.MISSING_DRONE_COUNT
    assert error.line_number == expected_line
    assert error.excerpt == expected_excerpt
    assert error.cause


@pytest.mark.parametrize(
    "drone_line",
    (
        "nb_drones:",
        "nb_drones:1",
        "nb_drones: 0",
        "nb_drones: -1",
        "nb_drones: many",
        "nb_drones: 1 extra",
    ),
)
def test_rejects_an_invalid_drone_count(drone_line: str) -> None:
    source = _source(
        drone_line,
        "start_hub: start 0 0",
        "end_hub: end 1 0",
    )

    with pytest.raises(MapParseError) as caught:
        MapParser().parse(source)

    assert caught.value.code is MapParseErrorCode.INVALID_DRONE_COUNT
    assert caught.value.line_number == 1
    assert caught.value.excerpt == drone_line


def test_rejects_a_duplicate_drone_count() -> None:
    source = _source(
        "nb_drones: 1",
        "start_hub: start 0 0",
        "nb_drones: 2",
        "end_hub: end 1 0",
    )

    with pytest.raises(MapParseError) as caught:
        MapParser().parse(source)

    assert caught.value.code is MapParseErrorCode.INVALID_DRONE_COUNT
    assert caught.value.line_number == 3


def test_limits_the_diagnostic_excerpt() -> None:
    source = "unknown: " + ("x" * 200)

    with pytest.raises(MapParseError) as caught:
        MapParser().parse(source)

    assert caught.value.excerpt is not None
    assert len(caught.value.excerpt) == 120
    assert caught.value.excerpt.endswith("...")


@pytest.mark.parametrize(
    ("zone_line", "expected_code"),
    (
        (
            "start_hub: start 0",
            MapParseErrorCode.INVALID_FIELD_COUNT,
        ),
        (
            "start_hub: start west 0",
            MapParseErrorCode.INVALID_COORDINATE,
        ),
        (
            "start_hub: start-zone 0 0",
            MapParseErrorCode.INVALID_ZONE_NAME,
        ),
    ),
)
def test_rejects_invalid_zone_fields(
    zone_line: str,
    expected_code: MapParseErrorCode,
) -> None:
    source = _source(
        "nb_drones: 1",
        zone_line,
        "end_hub: end 1 0",
    )

    with pytest.raises(MapParseError) as caught:
        MapParser().parse(source)

    assert caught.value.code is expected_code
    assert caught.value.line_number == 2
    assert caught.value.excerpt == zone_line


@pytest.mark.parametrize(
    "zone_line",
    (
        "hub: bad 1 0 [color=red",
        "hub: bad 1 0 color=red]",
        "hub: bad 1 0 []",
        "hub: bad 1 0 [color]",
        "hub: bad 1 0 [=red]",
        "hub: bad 1 0 [color=]",
        "hub: bad 1 0 [color=red=blue]",
        "hub: bad 1 0 [color=red] [zone=normal]",
    ),
)
def test_rejects_malformed_metadata(zone_line: str) -> None:
    source = _source(
        "nb_drones: 1",
        "start_hub: start 0 0",
        zone_line,
        "end_hub: end 2 0",
    )

    with pytest.raises(MapParseError) as caught:
        MapParser().parse(source)

    assert caught.value.code is MapParseErrorCode.MALFORMED_METADATA
    assert caught.value.line_number == 3
    assert caught.value.excerpt == zone_line


@pytest.mark.parametrize(
    ("zone_line", "expected_code"),
    (
        (
            "hub: bad 1 0 [speed=2]",
            MapParseErrorCode.UNKNOWN_METADATA,
        ),
        (
            "hub: bad 1 0 [color=red color=blue]",
            MapParseErrorCode.DUPLICATE_METADATA,
        ),
    ),
)
def test_rejects_unsupported_zone_metadata(
    zone_line: str,
    expected_code: MapParseErrorCode,
) -> None:
    source = _source(
        "nb_drones: 1",
        "start_hub: start 0 0",
        zone_line,
        "end_hub: end 2 0",
    )

    with pytest.raises(MapParseError) as caught:
        MapParser().parse(source)

    assert caught.value.code is expected_code
    assert caught.value.line_number == 3


@pytest.mark.parametrize(
    ("connection_line", "expected_code"),
    (
        (
            "connection: startend",
            MapParseErrorCode.INVALID_FIELD_COUNT,
        ),
        (
            "connection: start-middle-end",
            MapParseErrorCode.INVALID_FIELD_COUNT,
        ),
        (
            "connection: start-start",
            MapParseErrorCode.SELF_CONNECTION,
        ),
        (
            "connection: start-end [color=red]",
            MapParseErrorCode.UNKNOWN_METADATA,
        ),
        (
            "connection: start-end "
            "[max_link_capacity=1 max_link_capacity=2]",
            MapParseErrorCode.DUPLICATE_METADATA,
        ),
    ),
)
def test_rejects_invalid_connection_syntax(
    connection_line: str,
    expected_code: MapParseErrorCode,
) -> None:
    source = _minimal_with(connection_line)

    with pytest.raises(MapParseError) as caught:
        MapParser().parse(source)

    assert caught.value.code is expected_code
    assert caught.value.line_number == 4
    assert caught.value.excerpt == connection_line


def test_ignores_declared_terminal_capacity_without_validating_value() -> None:
    source = _source(
        "nb_drones: 1",
        "start_hub: start 0 0 [max_drones=invalid]",
        "end_hub: end 1 0 [max_drones=0]",
    )

    parsed_map = MapParser().parse(source)

    assert parsed_map.start.capacity is CapacityLimit.UNLIMITED
    assert parsed_map.end.capacity is CapacityLimit.UNLIMITED
    assert parsed_map.start.metadata == (("max_drones", "invalid"),)
    assert parsed_map.end.metadata == (("max_drones", "0"),)


@pytest.mark.parametrize(
    ("source", "expected_code", "expected_line"),
    (
        (
            _minimal_with("unknown: surprise"),
            MapParseErrorCode.UNKNOWN_DECLARATION,
            4,
        ),
        (
            _source(
                "nb_drones: 1",
                "start_hub: start 0 0",
                "hub: start 1 0",
                "end_hub: end 2 0",
            ),
            MapParseErrorCode.DUPLICATE_ZONE,
            3,
        ),
        (
            _source(
                "nb_drones: 1",
                "start_hub: start 0 0",
                "end_hub: end 1 0",
                "end_hub: other 2 0",
            ),
            MapParseErrorCode.DUPLICATE_END,
            4,
        ),
        (
            _source(
                "nb_drones: 1",
                "end_hub: end 1 0",
            ),
            MapParseErrorCode.MISSING_START,
            2,
        ),
        (
            _source(
                "nb_drones: 1",
                "start_hub: start 0 0",
                "hub: bad 1 0 [zone=teleport]",
                "end_hub: end 2 0",
            ),
            MapParseErrorCode.INVALID_ZONE_TYPE,
            3,
        ),
        (
            _source(
                "nb_drones: 1",
                "start_hub: start 0 0",
                "hub: bad 1 0 [max_drones=-1]",
                "end_hub: end 2 0",
            ),
            MapParseErrorCode.INVALID_CAPACITY,
            3,
        ),
        (
            _source(
                "nb_drones: 1",
                "start_hub: start 0 0",
                "start_hub: other 1 0",
                "end_hub: end 2 0",
            ),
            MapParseErrorCode.DUPLICATE_START,
            3,
        ),
        (
            _source(
                "nb_drones: 1",
                "start_hub: start 0 0",
            ),
            MapParseErrorCode.MISSING_END,
            2,
        ),
        (
            _minimal_with("connection: start-later"),
            MapParseErrorCode.UNKNOWN_CONNECTION_ZONE,
            4,
        ),
        (
            _minimal_with(
                "connection: start-end",
                "connection: end-start",
            ),
            MapParseErrorCode.DUPLICATE_CONNECTION,
            5,
        ),
    ),
)
def test_uses_stable_codes_for_semantic_and_cross_line_errors(
    source: str,
    expected_code: MapParseErrorCode,
    expected_line: int,
) -> None:
    with pytest.raises(MapParseError) as caught:
        MapParser().parse(source)

    assert caught.value.code is expected_code
    assert caught.value.line_number == expected_line


@pytest.mark.parametrize(
    ("source", "expected_code", "expected_line"),
    (
        (
            "nb_drones: " + _TOO_LONG_INTEGER,
            MapParseErrorCode.INVALID_DRONE_COUNT,
            1,
        ),
        (
            _source(
                "nb_drones: 1",
                "start_hub: start " + _TOO_LONG_INTEGER + " 0",
                "end_hub: end 1 0",
            ),
            MapParseErrorCode.INVALID_COORDINATE,
            2,
        ),
        (
            _source(
                "nb_drones: 1",
                "start_hub: start 0 0",
                "hub: huge 1 0 [max_drones="
                + _TOO_LONG_INTEGER
                + "]",
                "end_hub: end 2 0",
            ),
            MapParseErrorCode.INVALID_CAPACITY,
            3,
        ),
        (
            _minimal_with(
                "connection: start-end [max_link_capacity="
                + _TOO_LONG_INTEGER
                + "]",
            ),
            MapParseErrorCode.INVALID_CAPACITY,
            4,
        ),
    ),
)
def test_wraps_oversized_integer_conversion_errors(
    source: str,
    expected_code: MapParseErrorCode,
    expected_line: int,
) -> None:
    with pytest.raises(MapParseError) as caught:
        MapParser().parse(source)

    assert caught.value.code is expected_code
    assert caught.value.line_number == expected_line
    assert caught.value.excerpt is not None
    assert len(caught.value.excerpt) == 120
