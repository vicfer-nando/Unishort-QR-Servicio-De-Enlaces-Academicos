"""Regresiones observables de validación, errores HTTP y autenticación."""

import pytest


@pytest.mark.parametrize("url", ["https://[invalid", "https://[no-ip]/"])
def test_malformed_ipv6_is_rejected_without_persisting(client, admin_key, url):
    response = client.post("/api/v1/links", json={"url": url})
    assert response.status_code == 400
    assert response.json()["success"] is False
    listed = client.get("/api/v1/links", headers={"X-Admin-API-Key": admin_key})
    assert listed.json()["data"]["total"] == 0


@pytest.mark.parametrize(
    "method,path,status",
    [
        ("GET", "/api/v1/unknown/route", 404),
        ("PUT", "/api/v1/links", 405),
    ],
)
def test_framework_errors_use_envelope(client, method, path, status):
    response = client.request(method, path)
    assert response.status_code == status
    assert response.json()["success"] is False
    assert response.json()["errors"][0]["code"] == "http_error"
    if status == 405:
        assert response.headers["allow"]


def test_non_ascii_admin_key_is_forbidden_not_server_error(client, admin_key):
    response = client.get("/api/v1/links", headers={"X-Admin-API-Key": b"clav\xe9"})
    assert response.status_code == 403
    assert response.json()["errors"][0]["code"] == "admin_forbidden"


def test_cors_preflight_allows_frontend_and_request_id(client):
    response = client.options(
        "/api/v1/links",
        headers={
            "Origin": "http://localhost:5500",
            "Access-Control-Request-Method": "POST",
            "Access-Control-Request-Headers": "content-type",
        },
    )
    assert response.status_code == 200
    assert response.headers["access-control-allow-origin"] == "http://localhost:5500"
    response = client.get("/health", headers={"Origin": "http://localhost:5500"})
    assert "X-Request-Id" in response.headers["access-control-expose-headers"]


def test_logs_never_include_arbitrary_path_or_client_request_id(client, caplog):
    response = client.get(
        "/api/v1/private/person@example.edu",
        headers={
            "X-Request-Id": "person@example.edu",
        },
    )
    records = [record for record in caplog.records if record.name == "unishort"]
    assert records
    assert all("person@example.edu" not in str(record.__dict__) for record in records)
    assert response.headers["X-Log-Request-Id"] != "person@example.edu"


def test_openapi_describes_envelope_errors_and_admin_security(client):
    schema = client.get("/openapi.json").json()
    operation = schema["paths"]["/api/v1/links"]["post"]
    ref = operation["responses"]["422"]["content"]["application/json"]["schema"]["$ref"]
    assert ref.endswith("/ErrorEnvelope")
    assert schema["paths"]["/api/v1/links"]["get"]["security"]


def test_unhandled_error_has_safe_envelope_cors_and_request_id(client, monkeypatch):
    def fail(*args, **kwargs):
        raise RuntimeError("private-person bound SQL parameter")

    monkeypatch.setattr("app.services.create_short_link", fail)
    response = client.post(
        "/api/v1/links",
        json={"url": "https://example.edu"},
        headers={"Origin": "http://localhost:5500"},
    )
    assert response.status_code == 500
    assert response.headers["X-Request-Id"] == response.json()["meta"]["request_id"]
    assert response.headers["access-control-allow-origin"] == "http://localhost:5500"
    assert "private-person" not in response.text
