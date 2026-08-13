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


def test_api_does_not_serve_frontend_files() -> None:
    """The API remains JSON/OpenAPI only and does not host the native UI."""
    client = TestClient(create_app())

    assert client.get("/").status_code == 404
    assert client.get("/style.css").status_code == 404
    assert client.get("/app.js").status_code == 404
    assert client.get("/img/happy.svg").status_code == 404


def test_api_allows_local_frontend_origin() -> None:
    """The standalone frontend may read API responses through narrow CORS."""
    client = TestClient(create_app())
    response = client.get(
        "/api/v1/health",
        headers={"Origin": "http://127.0.0.1:8080"},
    )

    assert response.status_code == 200
    assert response.headers["access-control-allow-origin"] == (
        "http://127.0.0.1:8080"
    )


def test_api_does_not_allow_unknown_frontend_origin() -> None:
    """CORS stays restricted to the documented local frontend origins."""
    client = TestClient(create_app())
    response = client.get(
        "/api/v1/health",
        headers={"Origin": "http://example.test"},
    )

    assert response.status_code == 200
    assert "access-control-allow-origin" not in response.headers
