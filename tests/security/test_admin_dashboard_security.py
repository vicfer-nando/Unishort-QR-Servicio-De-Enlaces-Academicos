"""Autorización, privacidad y caché del nuevo panel."""

import pytest
from app.config import get_settings


@pytest.mark.parametrize("path", ["/api/v1/admin/stats", "/api/v1/links?q=private"])
def test_dashboard_access_and_no_store(client, admin_key, path):
    for headers, status in [
        ({}, 401),
        ({"X-Admin-API-Key": "wrong"}, 403),
        ({"X-Admin-API-Key": admin_key}, 200),
    ]:
        response = client.get(path, headers=headers)
        assert response.status_code == status
        assert response.headers.get("cache-control") == "no-store"
        assert admin_key not in response.text
        assert "set-cookie" not in response.headers


def test_summary_without_server_configuration(client, monkeypatch):
    monkeypatch.setenv("UNISHORT_ADMIN_API_KEY", "")
    get_settings.cache_clear()
    try:
        response = client.get("/api/v1/admin/stats")
        assert response.status_code == 503
        assert response.json()["errors"][0]["code"] == "admin_not_configured"
        assert response.headers.get("cache-control") == "no-store"
    finally:
        get_settings.cache_clear()


def test_search_and_key_are_not_logged(client, admin_key, caplog):
    response = client.get(
        "/api/v1/links",
        params={"q": "https://private.edu/secret-document"},
        headers={"X-Admin-API-Key": admin_key},
    )
    assert response.status_code == 200
    server_logs = " ".join(
        record.getMessage()
        for record in caplog.records
        if record.name.startswith("unishort")
    )
    assert admin_key not in server_logs
    assert "private.edu" not in server_logs


def test_new_endpoint_cannot_authenticate_using_query(client, admin_key):
    assert (
        client.get("/api/v1/admin/stats", params={"api_key": admin_key}).status_code
        == 401
    )
