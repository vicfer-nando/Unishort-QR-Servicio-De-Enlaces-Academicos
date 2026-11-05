"""Pruebas de seguridad básica y control de acceso administrativo."""

from app.config import get_settings
from sqlalchemy import inspect


def test_creation_remains_public(client):
    response = client.post("/api/v1/links", json={"url": "https://example.com/publico"})

    assert response.status_code == 201


def test_admin_list_requires_key(client, admin_key):
    missing = client.get("/api/v1/links")
    wrong = client.get("/api/v1/links", headers={"X-Admin-API-Key": "incorrecta"})
    valid = client.get("/api/v1/links", headers={"X-Admin-API-Key": admin_key})

    assert missing.status_code == 401
    assert missing.json()["errors"][0]["code"] == "admin_authentication_required"
    assert wrong.status_code == 403
    assert wrong.json()["errors"][0]["code"] == "admin_forbidden"
    assert valid.status_code == 200


def test_administrative_operations_are_protected(client, admin_key):
    code = client.post(
        "/api/v1/links", json={"url": "https://example.com/protegido"}
    ).json()["data"]["short_code"]

    for response in (
        client.get(f"/api/v1/links/{code}/stats"),
        client.patch(f"/api/v1/links/{code}", json={"is_active": False}),
        client.delete(f"/api/v1/links/{code}"),
    ):
        assert response.status_code == 401
        assert response.json()["success"] is False


def test_admin_disabled_when_key_is_not_configured(client, monkeypatch):
    monkeypatch.delenv("UNISHORT_ADMIN_API_KEY", raising=False)
    get_settings.cache_clear()
    try:
        response = client.get("/api/v1/links")
        assert response.status_code == 503
        assert response.json()["errors"][0]["code"] == "admin_not_configured"
    finally:
        get_settings.cache_clear()


def test_database_does_not_store_personal_data_columns(db_session):
    columns = {
        column["name"] for column in inspect(db_session.bind).get_columns("short_urls")
    }

    assert columns == {
        "id",
        "short_code",
        "original_url",
        "created_at",
        "is_active",
        "expires_at",
        "click_count",
    }
    forbidden = {"ip", "ip_address", "user_agent", "cookie", "email", "session_id"}
    assert columns.isdisjoint(forbidden)
