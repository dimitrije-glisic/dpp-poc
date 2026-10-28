from app.qr import make_qr, passport_url

PNG_SIGNATURE = b"\x89PNG\r\n\x1a\n"


def test_passport_url_builder():
    assert passport_url("ABC-123", "http://example.org/") == "http://example.org/passport/ABC-123"


def test_make_qr_png():
    assert make_qr("http://example.org").startswith(PNG_SIGNATURE)


def test_make_qr_svg():
    assert b"<svg" in make_qr("http://example.org", kind="svg")


def test_qr_endpoint_png(client, created_battery):
    response = client.get("/api/batteries/TEST-LFP-0001/qr")
    assert response.status_code == 200
    assert response.headers["content-type"] == "image/png"
    assert response.content.startswith(PNG_SIGNATURE)


def test_qr_endpoint_svg(client, created_battery):
    response = client.get("/api/batteries/TEST-LFP-0001/qr", params={"format": "svg"})
    assert response.status_code == 200
    assert response.headers["content-type"].startswith("image/svg+xml")


def test_qr_endpoint_unknown_battery(client):
    assert client.get("/api/batteries/NOPE-0000/qr").status_code == 404


def test_qr_endpoint_invalid_format(client, created_battery):
    response = client.get("/api/batteries/TEST-LFP-0001/qr", params={"format": "gif"})
    assert response.status_code == 422
