import re

import pytest


def shorten(client, url):
    return client.post("/shorten", json={"url": url})


def test_create_short_url_returns_expected_contract(client):
    original_url = "https://www.example.com/articulo?lang=es"

    response = shorten(client, original_url)

    assert response.status_code == 200
    data = response.json()
    assert set(data) == {"short_code", "short_url", "original_url"}
    assert data["original_url"] == original_url
    assert re.fullmatch(r"[A-Za-z0-9]{6}", data["short_code"])
    assert data["short_url"] == f"http://testserver/s/{data['short_code']}"


def test_same_url_returns_the_same_short_code(client):
    url = "https://www.example.com/recurso-compartido"

    first = shorten(client, url).json()
    second = shorten(client, url).json()

    assert first["short_code"] == second["short_code"]
    assert first["short_url"] == second["short_url"]


def test_different_urls_return_different_short_codes(client):
    first = shorten(client, "https://www.example.com/uno").json()
    second = shorten(client, "https://www.example.com/dos").json()

    assert first["short_code"] != second["short_code"]


def test_extra_fields_are_ignored(client):
    response = client.post(
        "/shorten",
        json={"url": "https://www.example.com/extra", "campo_extra": True},
    )

    assert response.status_code == 200
    assert set(response.json()) == {"short_code", "short_url", "original_url"}


def test_short_code_redirects_to_original_url(client):
    original_url = "https://www.example.com/destino?origen=unishort"
    code = shorten(client, original_url).json()["short_code"]

    response = client.get(f"/s/{code}", follow_redirects=False)

    assert response.status_code == 307
    assert response.headers["location"] == original_url


def test_unknown_short_code_returns_404(client):
    response = client.get("/s/noexiste")

    assert response.status_code == 404
    assert response.json() == {"detail": "Enlace corto no encontrado"}


@pytest.mark.parametrize(
    ("payload", "expected_type"),
    [
        ({"url": "javascript:alert(1)"}, "url_scheme"),
        ({"url": "not-a-url"}, "url_parsing"),
        ({}, "missing"),
        ({"url": "https://example.com/" + "a" * 3000}, "url_too_long"),
    ],
)
def test_invalid_payloads_return_422(client, payload, expected_type):
    response = client.post("/shorten", json=payload)

    assert response.status_code == 422
    detail = response.json()["detail"]
    assert detail[0]["type"] == expected_type


def test_cors_allows_frontend_origin(client):
    response = client.options(
        "/shorten",
        headers={
            "Origin": "http://localhost:5500",
            "Access-Control-Request-Method": "POST",
            "Access-Control-Request-Headers": "content-type",
        },
    )

    assert response.status_code == 200
    assert response.headers["access-control-allow-origin"] == "http://localhost:5500"
