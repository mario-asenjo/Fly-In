"""OpenAPI contract coverage for the map API."""

from fastapi.testclient import TestClient

from flyin.adapters.api.app import create_app


def test_openapi_contains_map_catalog_and_simulation_contracts() -> None:
    """OpenAPI publishes the synchronous map API paths and schemas."""
    client = TestClient(create_app())

    schema = client.get("/openapi.json").json()

    assert "/api/v1/maps" in schema["paths"]
    assert "/api/v1/maps/{map_index}/simulate" in schema["paths"]
    assert "get" in schema["paths"]["/api/v1/maps"]
    assert "post" in schema["paths"]["/api/v1/maps/{map_index}/simulate"]
    assert "MapCatalogResponse" in schema["components"]["schemas"]
    assert "SolveResponse" in schema["components"]["schemas"]
    assert "ErrorResponse" in schema["components"]["schemas"]
