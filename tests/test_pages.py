def test_root_redirects_to_list(client):
    response = client.get("/", follow_redirects=False)
    assert response.status_code == 307
    assert response.headers["location"] == "/batteries"


def test_empty_list_page(client):
    response = client.get("/batteries")
    assert response.status_code == 200
    assert "No batteries registered yet" in response.text


def test_list_page_shows_battery(client, created_battery):
    response = client.get("/batteries")
    assert "TEST-LFP-0001" in response.text
    assert "illustrative demo data" in response.text


def test_detail_page(client, created_battery):
    response = client.get("/batteries/TEST-LFP-0001")
    assert response.status_code == 200
    assert "TP10-0001" in response.text
    assert "/api/batteries/TEST-LFP-0001/qr" in response.text
    assert created_battery["passport_url"] in response.text


def test_public_passport_page(client, created_battery):
    response = client.get("/passport/TEST-LFP-0001")
    assert response.status_code == 200
    assert "Battery Passport" in response.text
    assert "60.0 kg CO₂e / kWh" in response.text
    assert "illustrative" in response.text


def test_unknown_pages_return_404(client):
    assert client.get("/batteries/NOPE-0000").status_code == 404
    assert client.get("/passport/NOPE-0000").status_code == 404


def test_html_is_escaped(client, battery_payload):
    battery_payload["end_of_life_info"] = "<script>alert('x')</script>"
    client.post("/api/batteries", json=battery_payload)
    response = client.get("/passport/TEST-LFP-0001")
    assert "<script>alert" not in response.text
    assert "&lt;script&gt;" in response.text
