""""""


from fastapi.testclient import TestClient

from flyin.adapters.api.app import create_app


def test_api_simulates_map_selected_from_catalog() -> None:
    """"""

    with TestClient(create_app()) as client:
        catalog = client.get("/api/v1/maps").json()["maps"]

        selected = next(
            item
            for item in catalog
            if item["display_path"].endswith(
                "easy/01_linear_path.txt"
            )
        )

        response = client.post(
            f"/api/v1/maps/{selected['index']}/simulate"
        )

    assert response.status_code == 200

    payload = response.json()

    assert payload["turn_count"] == 4
    assert payload["map"]["drone_count"] == 2

    assert payload["movement_lines"] == [
        "D1-waypoint1",
        "D1-waypoint2 D2-waypoint1",
        "D1-goal D2-waypoint2",
        "D2-goal",
    ]
