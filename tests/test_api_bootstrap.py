"""HTTP application bootstrap tests."""

from fastapi.testclient import TestClient

from flyin.adapters.api.app import create_app


def test_api_health_endpoint() -> None:
    """The versioned health endpoint exposes its contract."""
    client = TestClient(create_app())
    response = client.get("/api/v1/health")

    assert response.json() == {"status": "ok"}
    assert response.status_code == 200


def test_openapi_contains_health_endpoint() -> None:
    """The application registers health in its OpenAPI schema."""
    client = TestClient(create_app())
    response = client.get("/openapi.json")

    assert response.status_code == 200
    assert "/api/v1/health" in response.json()["paths"]
    assert "/" not in response.json()["paths"]
    assert "/style.css" not in response.json()["paths"]
    assert "/app.js" not in response.json()["paths"]


def test_native_frontend_is_served_from_same_origin() -> None:
    """The API process serves the browser shell and its flat assets."""
    client = TestClient(create_app())

    index = client.get("/")
    stylesheet = client.get("/style.css")
    script = client.get("/app.js")
    drone = client.get("/img/happy.svg")

    assert index.status_code == 200
    assert "Choose a flight map" in index.text
    assert stylesheet.status_code == 200
    assert "selector-card" in stylesheet.text
    assert script.status_code == 200
    assert 'const UI_PREFIX = "[Fly-In UI]";' in script.text
    assert 'const endpoint = "/api/v1/maps";' in script.text
    assert drone.status_code == 200
    assert "Drone happy" in drone.text
