"""Pruebas de generación y decodificación de códigos QR."""

import cv2
import numpy as np
import pytest
from app.qr import generate_qr_png


def decode_qr(png_bytes: bytes) -> str:
    array = np.frombuffer(png_bytes, dtype=np.uint8)
    image = cv2.imdecode(array, cv2.IMREAD_COLOR)
    assert image is not None
    data, _points, _straight = cv2.QRCodeDetector().detectAndDecode(image)
    return data


def test_generated_qr_is_decodable_and_contains_the_content():
    content = "https://qr.unl.edu.ec/s/abc2345"
    png = generate_qr_png(content)

    assert png.startswith(b"\x89PNG\r\n\x1a\n")
    assert decode_qr(png) == content


def test_empty_content_is_rejected():
    with pytest.raises(ValueError):
        generate_qr_png("   ")


def test_endpoint_returns_png_with_the_short_url(client):
    created = client.post(
        "/api/v1/links", json={"url": "https://example.com/qr-destino"}
    ).json()["data"]

    response = client.get(f"/api/v1/links/{created['short_code']}/qr")

    assert response.status_code == 200
    assert response.headers["content-type"] == "image/png"
    assert decode_qr(response.content) == created["short_url"]


def test_unknown_code_does_not_produce_a_qr(client):
    response = client.get("/api/v1/links/noexiste/qr")

    assert response.status_code == 404
    assert response.json()["errors"][0]["code"] == "link_not_found"


def test_inactive_link_does_not_produce_a_qr(client, admin_key):
    code = client.post(
        "/api/v1/links", json={"url": "https://example.com/qr-inactivo"}
    ).json()["data"]["short_code"]
    client.patch(
        f"/api/v1/links/{code}",
        json={"is_active": False},
        headers={"X-Admin-API-Key": admin_key},
    )

    response = client.get(f"/api/v1/links/{code}/qr")

    assert response.status_code == 410
    assert response.json()["errors"][0]["code"] == "link_inactive"
