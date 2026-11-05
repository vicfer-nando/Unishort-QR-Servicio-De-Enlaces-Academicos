"""Prueba el flujo HTTP que ejecuta el frontend y su configuración de API."""

from pathlib import Path
from urllib.parse import urlsplit

FRONTEND = Path(__file__).resolve().parents[2] / "frontend" / "index.html"


def test_frontend_allows_configuring_api_base_url():
    html = FRONTEND.read_text(encoding="utf-8")

    assert "window.UNISHORT_API_BASE_URL" in html
    assert "`${API_BASE_URL}${API_PREFIX}/links`" in html


def test_frontend_create_redirect_and_qr_flow(client):
    created = client.post(
        "/api/v1/links", json={"url": "https://www.example.com/frontend"}
    )

    assert created.status_code == 201
    data = created.json()["data"]
    assert created.headers["X-Request-Id"]

    redirect = client.get(f"/s/{data['short_code']}", follow_redirects=False)
    assert redirect.status_code == 307
    assert redirect.headers["location"] == "https://www.example.com/frontend"

    qr = client.get(urlsplit(data["qr_url"]).path)
    assert qr.status_code == 200
    assert qr.headers["content-type"] == "image/png"
    assert qr.content.startswith(b"\x89PNG")
