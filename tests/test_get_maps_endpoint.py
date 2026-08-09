""""""

from fastapi.testclient import TestClient

from flyin.adapters.api.app import create_app


def test_api_lists_official_map_catalog() -> None:
    """"""
    with TestClient(create_app()) as client:
        response = client.get("/api/v1/maps")

    assert response.status_code == 200

    payload = response.json()
    maps = payload["maps"]

    assert maps
    assert [item["index"] for item in maps] == list(
        range(1, len(maps) + 1)
    )
    assert set(maps[0]) == {"index", "display_path"}
