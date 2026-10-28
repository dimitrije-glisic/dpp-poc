from app.config import PUBLIC_BASE_URL


def test_health(client):
    assert client.get("/health").json() == {"status": "ok"}


def test_openapi_docs_available(client):
    assert client.get("/docs").status_code == 200
    paths = client.get("/openapi.json").json()["paths"]
    assert "/api/batteries" in paths
    assert "/batteries" not in paths  # HTML routes are excluded from the API schema


def test_register_battery(created_battery, battery_payload):
    assert created_battery["product_id"] == battery_payload["product_id"]
    assert created_battery["passport_url"] == f"{PUBLIC_BASE_URL}/passport/TEST-LFP-0001"
    assert created_battery["is_demo_data"] is True
    assert "id" not in created_battery


def test_duplicate_product_id_conflict(client, created_battery, battery_payload):
    battery_payload["serial_number"] = "OTHER-SERIAL"
    response = client.post("/api/batteries", json=battery_payload)
    assert response.status_code == 409
    assert "product_id" in response.json()["detail"]


def test_duplicate_serial_for_same_manufacturer_conflict(client, created_battery, battery_payload):
    battery_payload["product_id"] = "TEST-LFP-0002"
    response = client.post("/api/batteries", json=battery_payload)
    assert response.status_code == 409
    assert "serial_number" in response.json()["detail"]


def test_same_serial_different_manufacturer_allowed(client, created_battery, battery_payload):
    battery_payload["product_id"] = "TEST-LFP-0003"
    battery_payload["manufacturer"] = "Another Fictional Maker"
    assert client.post("/api/batteries", json=battery_payload).status_code == 201


def test_invalid_payload_returns_422(client, battery_payload):
    battery_payload["capacity_kwh"] = -1
    assert client.post("/api/batteries", json=battery_payload).status_code == 422


def test_get_battery(client, created_battery):
    response = client.get("/api/batteries/TEST-LFP-0001")
    assert response.status_code == 200
    assert response.json()["model"] == "Test Pack 10"


def test_get_unknown_battery_404(client):
    assert client.get("/api/batteries/NOPE-0000").status_code == 404


def test_list_and_filter_by_status(client, created_battery, battery_payload):
    battery_payload.update(
        product_id="TEST-LFP-0004", serial_number="TP10-0004", lifecycle_status="in_service"
    )
    client.post("/api/batteries", json=battery_payload)

    all_items = client.get("/api/batteries").json()
    assert [b["product_id"] for b in all_items] == ["TEST-LFP-0001", "TEST-LFP-0004"]

    in_service = client.get("/api/batteries", params={"status": "in_service"}).json()
    assert [b["product_id"] for b in in_service] == ["TEST-LFP-0004"]


def test_list_pagination(client, created_battery):
    assert client.get("/api/batteries", params={"limit": 1, "offset": 1}).json() == []
    assert client.get("/api/batteries", params={"limit": 0}).status_code == 422


def test_update_status(client, created_battery):
    response = client.patch(
        "/api/batteries/TEST-LFP-0001/status", json={"lifecycle_status": "in_service"}
    )
    assert response.status_code == 200
    assert response.json()["lifecycle_status"] == "in_service"
    assert client.get("/api/batteries/TEST-LFP-0001").json()["lifecycle_status"] == "in_service"


def test_update_status_invalid_value(client, created_battery):
    response = client.patch(
        "/api/batteries/TEST-LFP-0001/status", json={"lifecycle_status": "lost"}
    )
    assert response.status_code == 422


def test_update_status_unknown_battery(client):
    response = client.patch(
        "/api/batteries/NOPE-0000/status", json={"lifecycle_status": "recycled"}
    )
    assert response.status_code == 404
