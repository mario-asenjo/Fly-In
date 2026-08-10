"""HTTP error handling contract tests."""

from pathlib import Path

import pytest
from fastapi.testclient import TestClient

import flyin.adapters.api.routers.maps as maps_module
from flyin.adapters.api.app import create_app
from flyin.adapters.files import MapFileOption
from flyin.application import SolveError


@pytest.mark.parametrize("map_index", (0, -1, 999))
def test_api_reports_unknown_map_index(map_index: int) -> None:
    """Unknown catalog selections use the stable API error envelope."""
    client = TestClient(create_app())

    response = client.post(f"/api/v1/maps/{map_index}/simulate")

    assert response.status_code == 404
    assert response.json() == {
        "error": {
            "code": "MAP_NOT_FOUND",
            "message": f"map index {map_index} was not found.",
            "details": {"map_index": map_index},
        }
    }


def test_api_reports_invalid_map_index_type() -> None:
    """FastAPI path validation is normalized to the public error envelope."""
    client = TestClient(create_app())

    response = client.post("/api/v1/maps/not-a-number/simulate")

    assert response.status_code == 422
    assert response.json()["error"]["code"] == "REQUEST_VALIDATION_ERROR"
    assert "map_index" in response.json()["error"]["message"]


def test_api_reports_solver_errors(monkeypatch: pytest.MonkeyPatch) -> None:
    """Application solve failures become safe HTTP responses."""

    def fail_solve(source: str) -> object:
        raise SolveError("NO_ROUTE", "start cannot reach goal")

    monkeypatch.setattr(
        "flyin.adapters.api.routers.maps.FlyInSolver.solve_text",
        fail_solve,
    )
    client = TestClient(create_app())

    response = client.post("/api/v1/maps/1/simulate")

    assert response.status_code == 422
    assert response.json() == {
        "error": {
            "code": "NO_ROUTE",
            "message": "start cannot reach goal",
            "details": {},
        }
    }


def test_api_reports_map_file_read_errors(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    """Filesystem failures are hidden behind a stable server error."""
    missing = tmp_path / "missing.txt"

    def fake_root() -> Path:
        return tmp_path

    monkeypatch.setattr(maps_module, "default_map_root", fake_root)
    (tmp_path / "placeholder.txt").write_text("nb_drones: 1", encoding="utf-8")
    monkeypatch.setattr(
        "flyin.adapters.api.routers.maps.MapCatalog.option_for_index",
        lambda self, index: MapFileOption(
            index=index,
            path=missing,
            display_path="missing.txt",
        ),
    )
    client = TestClient(create_app())

    response = client.post("/api/v1/maps/1/simulate")

    assert response.status_code == 500
    assert response.json() == {
        "error": {
            "code": "MAP_READ_ERROR",
            "message": "server map file could not be read.",
            "details": {},
        }
    }
