"""Pruebas de integración de administración, métricas y configuración."""

from datetime import datetime, timedelta, timezone

from app.config import get_settings


def _create(client, url="https://example.com/admin"):
    return client.post("/api/v1/links", json={"url": url}).json()["data"]


def test_stats_count_only_successful_redirects(client, admin_key):
    code = _create(client, "https://example.com/metricas")["short_code"]

    client.get(f"/s/{code}", follow_redirects=False)
    client.get(f"/s/{code}", follow_redirects=False)

    response = client.get(
        f"/api/v1/links/{code}/stats", headers={"X-Admin-API-Key": admin_key}
    )

    assert response.status_code == 200
    assert response.json()["data"]["click_count"] == 2


def test_list_is_paginated_and_reports_total(client, admin_key):
    _create(client, "https://example.com/uno")
    _create(client, "https://example.com/dos")

    response = client.get(
        "/api/v1/links?limit=1&offset=1",
        headers={"X-Admin-API-Key": admin_key},
    )

    body = response.json()["data"]
    assert body["total"] == 2
    assert body["limit"] == 1
    assert body["offset"] == 1
    assert len(body["items"]) == 1


def test_patch_can_set_and_clear_expiration(client, admin_key):
    code = _create(client)["short_code"]
    future = (datetime.now(timezone.utc) + timedelta(days=2)).isoformat()

    updated = client.patch(
        f"/api/v1/links/{code}",
        json={"expires_at": future},
        headers={"X-Admin-API-Key": admin_key},
    )
    assert updated.status_code == 200
    assert updated.json()["data"]["expires_at"] is not None
    assert updated.json()["data"]["status"] == "active"

    cleared = client.patch(
        f"/api/v1/links/{code}",
        json={"expires_at": None},
        headers={"X-Admin-API-Key": admin_key},
    )
    assert cleared.status_code == 200
    assert cleared.json()["data"]["expires_at"] is None


def test_patch_with_empty_body_is_rejected(client, admin_key):
    code = _create(client)["short_code"]

    response = client.patch(
        f"/api/v1/links/{code}",
        json={},
        headers={"X-Admin-API-Key": admin_key},
    )

    assert response.status_code == 422


def test_delete_deactivates_without_removing_the_record(client, admin_key):
    code = _create(client)["short_code"]

    deleted = client.delete(
        f"/api/v1/links/{code}", headers={"X-Admin-API-Key": admin_key}
    )
    still_there = client.get(f"/api/v1/links/{code}")

    assert deleted.status_code == 200
    assert deleted.json()["data"]["is_active"] is False
    assert still_there.status_code == 200
    assert still_there.json()["data"]["status"] == "inactive"


def test_base_url_from_environment_is_used_in_short_url(client, monkeypatch):
    monkeypatch.setenv("UNISHORT_BASE_URL", "https://qr.unl.edu.ec")
    get_settings.cache_clear()
    try:
        data = _create(client, "https://example.com/base-url")
        assert data["short_url"].startswith("https://qr.unl.edu.ec/s/")
        assert data["qr_url"].startswith("https://qr.unl.edu.ec/api/v1/")
    finally:
        get_settings.cache_clear()
