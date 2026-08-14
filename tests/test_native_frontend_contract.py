"""Static contract checks for the dependency-free browser client."""

from pathlib import Path


FRONTEND = Path(__file__).parents[1] / "frontend"


def read(name: str) -> str:
    """Read one frontend source file as UTF-8 text."""
    return (FRONTEND / name).read_text(encoding="utf-8")


def test_frontend_declares_happy_drone_favicon_and_runtime_scripts() -> None:
    """The browser shell loads the native simulation pipeline."""
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


def test_graph_uses_native_svg_for_zones_and_connections() -> None:
    """Dense graph primitives no longer reuse the oversized card assets."""
    graph = read("graph.js")

    assert 'S("line"' in graph
    assert 'S("rect"' in graph
    assert 'href:"img/zone.svg"' not in graph
    assert 'href:"img/conn.svg"' not in graph
    assert "img/${O(" in graph
    assert "X_STEP=142" in graph
    assert "Y_STEP=156" in graph
    assert "setBaseSize(a.w,a.h)" in graph
    assert "window.FlyInGraph" in graph


def test_simulation_ui_prioritizes_large_navigable_canvas() -> None:
    """Dense maps get an explorable canvas instead of dashboard chrome."""
    index = read("index.html")
    styles = read("style.css")
    playback = read("playback.js")

    assert 'id="graph-viewport"' in index
    assert 'id="graph-surface"' in index
    assert 'id="zoom-in-button"' in index
    assert 'id="zoom-out-button"' in index
    assert 'id="fit-button"' in index
    assert "height:min(74vh,900px)" in styles
    assert "overflow:auto" in styles
    assert "setBaseSize" in playback
    assert '"canvas:pan"' in playback
    assert '"canvas:zoom"' in playback
    assert '"canvas:fit"' in playback


def test_dashboard_metrics_and_movement_lines_are_not_rendered() -> None:
    """The simulation remains visually focused on the graph and playback."""
    index = read("index.html")
    renderer = read("render-simulation.js")

    assert 'id="metric-turns"' not in index
    assert 'id="fleet-waiting"' not in index
    assert 'id="movement-output"' not in index
    assert "movement_lines" not in renderer


def test_drone_and_decorative_assets_remain_available() -> None:
    """Native graph primitives do not remove the supplied visual identity."""
    index = read("index.html")
    graph = read("graph.js")

    assert 'img/happy.svg' in index
    assert 'img/sad.svg' in index
    assert 'img/normal.svg' in index
    assert '"sad":"normal"' in graph
