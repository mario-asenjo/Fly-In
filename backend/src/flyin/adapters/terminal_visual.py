"""Colored terminal visualization for application solve results."""

from flyin.application import MovementView, SolveResult, ZoneView

_RESET = "\033[0m"
_COLOR_CODES = {
    "black": "90",
    "red": "31",
    "green": "32",
    "yellow": "33",
    "blue": "34",
    "magenta": "35",
    "purple": "35",
    "cyan": "36",
    "white": "37",
    "orange": "38;5;208",
    "brown": "38;5;94",
    "maroon": "38;5;88",
    "gold": "38;5;220",
    "darkred": "38;5;52",
    "violet": "38;5;177",
    "crimson": "38;5;161",
    "rainbow": "38;5;201",
    "gray": "90",
    "grey": "90",
}


def format_visual_result(result: SolveResult) -> tuple[str, ...]:
    """Return human terminal output using application projections."""
    lines = [
        "Fly-In visual simulation",
        f"Drones: {result.map_view.drone_count}",
        "Zones:",
    ]
    zone_colors = {
        zone.name: zone.color for zone in result.map_view.zones
    }
    lines.extend(_format_zone(zone) for zone in result.map_view.zones)
    lines.append("Connections:")
    lines.extend(
        _format_connection(
            connection.left,
            connection.right,
            connection.capacity,
            zone_colors,
        )
        for connection in result.map_view.connections
    )
    lines.append("Turns:")
    lines.extend(
        f"  Turn {turn.number}: "
        + " ".join(_format_movement(movement) for movement in turn.movements)
        for turn in result.turns
    )
    lines.append("Metrics:")
    moved_counts = ",".join(
        str(count) for count in result.metrics.moved_drones_per_turn
    )
    lines.append(f"  moved_drones_per_turn={moved_counts}")
    lines.append(
        f"  average_turns_per_drone="
        f"{result.metrics.average_turns_per_drone:.2f}"
    )
    lines.append(f"  total_path_cost={result.metrics.total_path_cost}")
    return tuple(lines)


def _format_zone(zone: ZoneView) -> str:
    color = zone.color or "none"
    return (
        f"  {_paint('■', zone.color)} {_paint(zone.name, zone.color)} "
        f"kind={zone.kind} xy=({zone.x},{zone.y}) "
        f"capacity={zone.capacity} color={color}"
    )


def _format_connection(
    left: str,
    right: str,
    capacity: int,
    zone_colors: dict[str, str | None],
) -> str:
    return (
        f"  {_paint(left, zone_colors.get(left))}-"
        f"{_paint(right, zone_colors.get(right))} "
        f"capacity={capacity}"
    )


def _format_movement(movement: MovementView) -> str:
    if movement.token != f"D{movement.drone_id}-{movement.destination}":
        return (
            f"D{movement.drone_id}-"
            f"{_paint(movement.origin, movement.origin_color)}-"
            f"{_paint(movement.destination, movement.destination_color)}"
        )
    return (
        f"D{movement.drone_id}-"
        f"{_paint(movement.destination, movement.destination_color)}"
    )


def _paint(text: str, color: str | None) -> str:
    code = _COLOR_CODES.get((color or "").lower())
    if code is None:
        return text
    return f"\033[{code}m{text}{_RESET}"
