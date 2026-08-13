"""Static contract checks for the dependency-free browser client."""

from pathlib import Path


FRONTEND = Path(__file__).parents[1] / "frontend"


def read(name: str) -> str:
    """Read one frontend source file as UTF-8 text."""
    return (FRONTEND / name).read_text(encoding="utf-8")


def test_frontend_declares_happy_drone_favicon_and_runtime_scripts() -> None:
    """The browser shell loads the SVG-first simulation pipeline."""
    index = read("index.html")

    assert 'rel="icon" type="image/svg+xml" href="img/happy.svg"' in index
    assert 'src="graph.js"' in index
    assert 'src="project-turn.js"' in index
    assert 'src="render-simulation.js"' in index
    assert 'src="playback.js"' in index
    assert 'src="app.js"' in index


def test_frontend_calls_catalog_and_synchronous_simulation_api() -> None:
    """The transport script consumes the real local FastAPI endpoints."""
    script = read("app.js")

    assert 'const API_BASE_URL = "http://127.0.0.1:8000";' in script
    assert '`${API_BASE_URL}/api/v1/maps`' in script
    assert '/simulate`' in script
    assert 'method: "POST"' in script
    assert "window.FlyInSimulation.load(payload, map)" in script


def test_supplied_svg_assets_drive_the_graph_renderer() -> None:
    """The first graph implementation uses the supplied visual assets."""
    graph = read("graph.js")

    assert 'href:"img/zone.svg"' in graph
    assert 'href:"img/conn.svg"' in graph
    assert 'href:`img/${icon}.svg`' in graph
    assert "window.FlyInGraph" in graph


def test_runtime_zone_and_connection_assets_have_no_placeholder_text() -> None:
    """Template assets leave labels to runtime data instead of demo copy."""
    zone = read("img/zone.svg")
    connection = read("img/conn.svg")

    assert "Zone A" not in zone
    assert "drones received" not in zone
    assert "Connection</text>" not in connection
    assert "in transit: 0" not in connection
