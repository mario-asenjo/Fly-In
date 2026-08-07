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
