def test_api_root(client):
    response = client.get("/")

    assert response.status_code == 200
    assert response.json() == {"message": "UniShort QR API", "docs": "/docs"}


def test_openapi_is_available(client):
    response = client.get("/openapi.json")

    assert response.status_code == 200
    assert response.json()["info"]["title"] == "UniShort QR API"
    assert "/shorten" in response.json()["paths"]
    assert "/s/{short_code}" in response.json()["paths"]
