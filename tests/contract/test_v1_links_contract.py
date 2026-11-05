"""Pruebas de contrato y códigos HTTP de ``/api/v1``."""

from datetime import datetime, timedelta, timezone

import pytest
from app.domain import SHORT_CODE_ALPHABET
from app.rate_limit import FixedWindowRateLimiter


def create_link(client, url="https://www.example.com/articulo?lang=es", **extra):
    return client.post("/api/v1/links", json={"url": url, **extra})


def test_create_returns_201_and_universal_envelope(client):
    response = create_link(client)

    assert response.status_code == 201
    body = response.json()
    assert set(body) == {"success", "message", "data", "errors", "meta"}
    assert body["success"] is True
    assert body["errors"] == []
    assert set(body["data"]) == {
        "short_code",
        "short_url",
        "original_url",
        "qr_url",
        "created_at",
        "expires_at",
        "is_active",
        "click_count",
        "status",
    }
    assert body["data"]["status"] == "active"
    assert body["data"]["original_url"] == "https://www.example.com/articulo?lang=es"
    assert body["data"]["short_url"] == (
        f"http://localhost:8000/s/{body['data']['short_code']}"
    )
    assert body["data"]["qr_url"] == (
        f"http://localhost:8000/api/v1/links/{body['data']['short_code']}/qr"
    )
    assert len(body["data"]["short_code"]) == 7
    assert set(body["data"]["short_code"]) <= set(SHORT_CODE_ALPHABET)
    assert body["meta"]["api_version"] == "1.0.0"


def test_request_id_is_echoed(client):
    response = client.get("/health", headers={"X-Request-Id": "prueba-123"})

    assert response.headers["X-Request-Id"] == "prueba-123"
    assert response.json()["meta"]["request_id"] == "prueba-123"


def test_same_url_generates_new_link_without_deduplication(client):
    first = create_link(client, "https://www.example.com/repetida")
    second = create_link(client, "https://www.example.com/repetida")

    assert first.status_code == second.status_code == 201
    assert first.json()["data"]["short_code"] != second.json()["data"]["short_code"]


@pytest.mark.parametrize(
    ("payload", "status", "code", "field"),
    [
        ({}, 422, "invalid_payload", "url"),
        ({"url": "   "}, 422, "invalid_payload", "url"),
        ({"url": "javascript:alert(1)"}, 400, "invalid_scheme", "url"),
        ({"url": "ftp://example.com/f"}, 400, "invalid_scheme", "url"),
        ({"url": "https://"}, 400, "invalid_host", "url"),
        (
            {"url": "https://usuario:clave@example.com/recurso"},
            400,
            "embedded_credentials",
            "url",
        ),
        ({"url": "https://exa mple.com/ruta"}, 400, "invalid_url", "url"),
        ({"url": "https://example.com/" + "a" * 3000}, 422, "url_too_long", "url"),
    ],
)
def test_invalid_inputs_use_envelope_without_creating_links(
    client, payload, status, code, field
):
    response = client.post("/api/v1/links", json=payload)

    assert response.status_code == status
    body = response.json()
    assert body["success"] is False
    assert body["data"] is None
    assert body["errors"][0]["code"] == code
    assert body["errors"][0]["field"] == field


def test_unknown_field_is_rejected_by_strict_schema(client):
    response = client.post(
        "/api/v1/links",
        json={"url": "https://example.com/ok", "campo_extra": True},
    )

    assert response.status_code == 422
    assert response.json()["errors"][0]["code"] == "invalid_payload"


def test_validation_messages_are_localized(client):
    response = client.post(
        "/api/v1/links",
        json={"url": "ftp://example.com/f"},
        headers={"Accept-Language": "en"},
    )

    assert response.status_code == 400
    assert "Only http or https" in response.json()["message"]
    assert response.json()["meta"]["language"] == "en"


def test_redirect_is_307_without_json_body_and_counts_one_click(client):
    created = create_link(client, "https://www.example.com/destino?origen=unishort")
    code = created.json()["data"]["short_code"]

    response = client.get(f"/s/{code}", follow_redirects=False)

    assert response.status_code == 307
    assert (
        response.headers["location"]
        == "https://www.example.com/destino?origen=unishort"
    )
    assert response.content == b""

    metadata = client.get(f"/api/v1/links/{code}").json()["data"]
    assert metadata["click_count"] == 1


def test_unknown_code_is_404_envelope_in_v1(client):
    response = client.get("/api/v1/links/noexiste")

    assert response.status_code == 404
    assert response.json()["errors"][0]["code"] == "link_not_found"


def test_disabled_link_returns_410_and_stops_redirection(client, admin_key):
    code = create_link(client).json()["data"]["short_code"]

    patched = client.patch(
        f"/api/v1/links/{code}",
        json={"is_active": False},
        headers={"X-Admin-API-Key": admin_key},
    )
    assert patched.status_code == 200
    assert patched.json()["data"]["status"] == "inactive"

    response = client.get(f"/s/{code}", follow_redirects=False)

    assert response.status_code == 410
    assert response.json()["errors"][0]["code"] == "link_inactive"


def test_expired_link_returns_410(client_with_session):
    client, session_factory = client_with_session
    created = create_link(
        client,
        "https://www.example.com/caduca",
        expires_at=(datetime.now(timezone.utc) + timedelta(days=1)).isoformat(),
    )
    code = created.json()["data"]["short_code"]

    session = session_factory()
    from app import repository

    link = repository.get_by_code(session, code)
    link.expires_at = datetime.now(timezone.utc) - timedelta(seconds=1)
    session.commit()
    session.close()

    response = client.get(f"/s/{code}", follow_redirects=False)

    assert response.status_code == 410
    assert response.json()["errors"][0]["code"] == "link_expired"


def test_past_expiration_is_rejected(client):
    response = create_link(
        client,
        expires_at=(datetime.now(timezone.utc) - timedelta(days=1)).isoformat(),
    )

    assert response.status_code == 422
    assert response.json()["errors"][0]["code"] == "invalid_expiration"


def test_rate_limit_returns_429_with_retry_after(client):
    from app.main import app

    original = app.state.rate_limiter
    app.state.rate_limiter = FixedWindowRateLimiter(max_requests=2, window_seconds=60)
    try:
        assert create_link(client).status_code == 201
        assert create_link(client).status_code == 201
        response = create_link(client)
        assert response.status_code == 429
        assert response.json()["errors"][0]["code"] == "rate_limit_exceeded"
        assert int(response.headers["Retry-After"]) >= 1
    finally:
        app.state.rate_limiter = original


def test_health_reports_service_and_database(client):
    response = client.get("/health")

    assert response.status_code == 200
    body = response.json()
    assert body["success"] is True
    assert body["data"]["status"] == "ok"
    assert body["data"]["database"] == "ok"


def test_openapi_contains_versioned_api_and_health(client):
    schema = client.get("/openapi.json").json()

    assert "/api/v1/links" in schema["paths"]
    assert "/api/v1/links/{short_code}" in schema["paths"]
    assert "/health" in schema["paths"]
    assert "/shorten" in schema["paths"]
    assert "/s/{short_code}" in schema["paths"]
    assert "201" in schema["paths"]["/api/v1/links"]["post"]["responses"]
