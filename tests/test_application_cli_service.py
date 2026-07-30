from pathlib import Path

import pytest

from flyin.adapters.cli import main
from flyin.application import FlyInSolver, SolveError

PROJECT_ROOT = Path(__file__).parents[1]
OFFICIAL_MAPS = PROJECT_ROOT / "maps" / "maps-v1.5-added-before-m0"


def test_application_service_solves_text_to_evaluator_lines() -> None:
    result = FlyInSolver.solve_text(
        "\n".join(
            (
                "nb_drones: 4",
                "start_hub: start 0 0",
                "hub: alpha 1 0",
                "hub: beta 1 1",
                "end_hub: end 2 0",
                "connection: start-alpha",
                "connection: alpha-end",
                "connection: start-beta",
                "connection: beta-end",
            )
        )
    )

    assert result.movement_lines == (
        "D1-alpha D2-beta",
        "D1-end D2-end D3-alpha D4-beta",
        "D3-end D4-end",
    )
    assert result.turn_count == 3
    assert result.warnings == ()


def test_application_service_exposes_colored_zone_projection() -> None:
    result = FlyInSolver.solve_text(
        "\n".join(
            (
                "nb_drones: 1",
                "start_hub: start 0 0 [color=green]",
                "hub: redhub 1 0 [color=red]",
                "end_hub: end 2 0 [color=yellow]",
                "connection: start-redhub",
                "connection: redhub-end",
            )
        )
    )

    assert tuple(zone.name for zone in result.map_view.zones) == (
        "start",
        "redhub",
        "end",
    )
    assert tuple(zone.color for zone in result.map_view.zones) == (
        "green",
        "red",
        "yellow",
    )
    assert result.turns[0].movements[0].origin_color == "green"
    assert result.turns[0].movements[0].destination_color == "red"
    assert result.turns[1].movements[0].destination_color == "yellow"


def test_application_service_solves_official_map() -> None:
    source = (OFFICIAL_MAPS / "easy" / "01_linear_path.txt").read_text(
        encoding="utf-8"
    )

    result = FlyInSolver.solve_text(source)

    assert result.movement_lines == (
        "D1-waypoint1",
        "D1-waypoint2 D2-waypoint1",
        "D1-goal D2-waypoint2",
        "D2-goal",
    )
    assert tuple(zone.color for zone in result.map_view.zones) == (
        "green",
        "blue",
        "blue",
        "red",
    )
    assert result.metrics.moved_drones_per_turn == (1, 2, 2, 1)
    assert result.metrics.average_turns_per_drone == 3.5
    assert result.metrics.total_path_cost == 6


def test_application_service_exposes_capacity_projection() -> None:
    result = FlyInSolver.solve_text(
        "\n".join(
            (
                "nb_drones: 2",
                "start_hub: start 0 0",
                "hub: waypoint 1 0 [max_drones=1]",
                "end_hub: end 2 0",
                "connection: start-waypoint [max_link_capacity=1]",
                "connection: waypoint-end [max_link_capacity=1]",
            )
        )
    )

    assert tuple(turn.number for turn in result.capacity_turns) == (1, 2, 3)
    assert result.capacity_turns[0].zones == (
        ("start", 1, "unlimited"),
        ("waypoint", 1, 1),
        ("end", 0, "unlimited"),
    )
    assert result.capacity_turns[1].connections == (
        ("start", "waypoint", 1, 1),
        ("waypoint", "end", 1, 1),
    )


def test_application_metrics_count_restricted_cost_once() -> None:
    result = FlyInSolver.solve_text(
        "\n".join(
            (
                "nb_drones: 1",
                "start_hub: start 0 0",
                "hub: restricted 1 0 [zone=restricted]",
                "end_hub: end 2 0",
                "connection: start-restricted",
                "connection: restricted-end",
            )
        )
    )

    assert result.movement_lines == (
        "D1-start-restricted",
        "D1-restricted",
        "D1-end",
    )
    assert result.metrics.moved_drones_per_turn == (1, 1, 1)
    assert result.metrics.average_turns_per_drone == 3.0
    assert result.metrics.total_path_cost == 3
    assert result.capacity_turns[0].zones == (
        ("start", 0, "unlimited"),
        ("restricted", 0, 1),
        ("end", 0, "unlimited"),
    )
    assert result.capacity_turns[1].zones == (
        ("start", 0, "unlimited"),
        ("restricted", 1, 1),
        ("end", 0, "unlimited"),
    )
    assert result.capacity_turns[1].connections == (
        ("start", "restricted", 0, 1),
        ("restricted", "end", 0, 1),
    )


def test_capacity_projection_skips_restricted_arrival_link() -> None:
    result = FlyInSolver.solve_text(
        "\n".join(
            (
                "nb_drones: 2",
                "start_hub: start 0 0",
                "hub: restricted 1 0 [zone=restricted max_drones=1]",
                "end_hub: end 2 0",
                "connection: start-restricted [max_link_capacity=1]",
                "connection: restricted-end",
            )
        )
    )

    assert result.capacity_turns[1].connections[0] == (
        "start",
        "restricted",
        1,
        1,
    )


def test_cli_visual_preserves_restricted_connection_tokens(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    map_path = tmp_path / "restricted-map.txt"
    map_path.write_text(
        "\n".join(
            (
                "nb_drones: 1",
                "start_hub: start 0 0",
                "hub: loop_a 1 0 [zone=restricted color=blue]",
                "end_hub: end 2 0 [color=red]",
                "connection: start-loop_a",
                "connection: loop_a-end",
            )
        ),
        encoding="utf-8",
    )

    exit_code = main(("--visual", str(map_path)))
    captured = capsys.readouterr()

    assert exit_code == 0
    assert "Turn 1: D1-start-\033[34mloop_a\033[0m" in captured.out
    assert "Turn 2: D1-\033[34mloop_a\033[0m" in captured.out
    assert "Turn 3: D1-\033[31mend\033[0m" in captured.out


def test_application_service_reports_terminal_zone_type_warnings() -> None:
    result = FlyInSolver.solve_text(
        "\n".join(
            (
                "nb_drones: 1",
                "start_hub: start 0 0 [zone=blocked]",
                "end_hub: end 1 0 [zone=priority]",
                "connection: start-end",
            )
        )
    )

    assert tuple(warning.code for warning in result.warnings) == (
        "TERMINAL_ZONE_TYPE_IGNORED",
        "TERMINAL_ZONE_TYPE_IGNORED",
    )
    assert result.movement_lines == ("D1-end",)


def test_application_service_translates_parse_errors() -> None:
    try:
        FlyInSolver.solve_text("nb_drones: nope")
    except SolveError as exc:
        assert exc.code == "MAP_PARSE_ERROR"
        assert exc.line == 1
        assert "positive integer" in exc.message
    else:
        raise AssertionError("expected SolveError")


def test_cli_prints_only_movement_lines_to_stdout(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    map_path = tmp_path / "map.txt"
    map_path.write_text(
        "\n".join(
            (
                "nb_drones: 1",
                "start_hub: start 0 0",
                "end_hub: end 1 0",
                "connection: start-end",
            )
        ),
        encoding="utf-8",
    )

    exit_code = main((str(map_path),))
    captured = capsys.readouterr()

    assert exit_code == 0
    assert captured.out == "D1-end\n"
    assert captured.err == ""


def test_cli_prints_colored_map_and_turns(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    map_path = tmp_path / "visual-map.txt"
    map_path.write_text(
        "\n".join(
            (
                "nb_drones: 1",
                "start_hub: start 0 0 [color=green]",
                "hub: waypoint 1 0 [color=blue]",
                "end_hub: end 2 0 [color=red]",
                "connection: start-waypoint",
                "connection: waypoint-end",
            )
        ),
        encoding="utf-8",
    )

    exit_code = main(("--visual", str(map_path)))
    captured = capsys.readouterr()

    assert exit_code == 0
    assert captured.err == ""
    assert "Fly-In visual simulation" in captured.out
    assert "\033[32mstart\033[0m" in captured.out
    assert "\033[34mwaypoint\033[0m" in captured.out
    assert "\033[31mend\033[0m" in captured.out
    assert (
        "\033[32mstart\033[0m-\033[34mwaypoint\033[0m"
        in captured.out
    )
    assert "color=green" in captured.out
    assert "Turn 1: D1-\033[34mwaypoint\033[0m" in captured.out
    assert "Turn 2: D1-\033[31mend\033[0m" in captured.out
    assert "moved_drones_per_turn=1,1" in captured.out
    assert "average_turns_per_drone=2.00" in captured.out
    assert "total_path_cost=2" in captured.out


def test_cli_capacity_info_prints_diagnostics_without_default_stdout(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    map_path = tmp_path / "capacity-map.txt"
    map_path.write_text(
        "\n".join(
            (
                "nb_drones: 2",
                "start_hub: start 0 0",
                "hub: waypoint 1 0 [max_drones=1]",
                "end_hub: end 2 0",
                "connection: start-waypoint [max_link_capacity=1]",
                "connection: waypoint-end [max_link_capacity=1]",
            )
        ),
        encoding="utf-8",
    )

    exit_code = main(("--capacity-info", str(map_path)))
    captured = capsys.readouterr()

    assert exit_code == 0
    assert captured.err == ""
    assert "D1-waypoint" in captured.out
    assert "Capacity info:" in captured.out
    assert "Turn 1:" in captured.out
    assert "zone waypoint: 1/1 drones" in captured.out
    assert "connection start-waypoint: 1/1 used" in captured.out

    exit_code = main((str(map_path),))
    captured = capsys.readouterr()

    assert exit_code == 0
    assert "Capacity info:" not in captured.out


def test_cli_visual_supports_challenger_color_names(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    map_path = tmp_path / "color-map.txt"
    map_path.write_text(
        "\n".join(
            (
                "nb_drones: 1",
                "start_hub: start 0 0 [color=purple]",
                "hub: brown_zone 1 0 [color=brown]",
                "hub: orange_zone 2 0 [color=orange]",
                "end_hub: goal 3 0 [color=rainbow]",
                "connection: start-brown_zone",
                "connection: brown_zone-orange_zone",
                "connection: orange_zone-goal",
            )
        ),
        encoding="utf-8",
    )

    exit_code = main(("--visual", str(map_path)))
    captured = capsys.readouterr()

    assert exit_code == 0
    assert "\033[35m■\033[0m \033[35mstart\033[0m" in captured.out
    assert "\033[38;5;94m■\033[0m" in captured.out
    assert "\033[38;5;208m■\033[0m" in captured.out
    assert (
        "\033[31mg\033[0m\033[33mo\033[0m\033[32ma\033[0m"
        "\033[36ml\033[0m"
        in captured.out
    )


def test_cli_maps_invalid_input_to_stderr_and_exit_code(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    map_path = tmp_path / "bad-map.txt"
    map_path.write_text("nb_drones: nope", encoding="utf-8")

    exit_code = main((str(map_path),))
    captured = capsys.readouterr()

    assert exit_code == 2
    assert captured.out == ""
    assert "MAP_PARSE_ERROR" in captured.err
    assert "line 1" in captured.err


def test_cli_maps_unsolvable_input_to_stderr_and_exit_code(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    map_path = tmp_path / "blocked-map.txt"
    map_path.write_text(
        "\n".join(
            (
                "nb_drones: 1",
                "start_hub: start 0 0",
                "hub: blocked 1 0 [zone=blocked]",
                "end_hub: end 2 0",
                "connection: start-blocked",
                "connection: blocked-end",
            )
        ),
        encoding="utf-8",
    )

    exit_code = main((str(map_path),))
    captured = capsys.readouterr()

    assert exit_code == 3
    assert captured.out == ""
    assert "NO_ROUTE" in captured.err
