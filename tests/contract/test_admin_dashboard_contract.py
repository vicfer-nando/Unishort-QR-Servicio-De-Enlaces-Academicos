"""Contrato aditivo del resumen y filtros administrativos."""

import pytest


@pytest.mark.parametrize(
    "query",
    [
        {"q": ""},
        {"q": "x" * 2049},
        {"status": "deleted"},
        {"limit": 0},
        {"limit": 201},
        {"offset": -1},
        {"limit": "abc"},
    ],
)
def test_invalid_list_parameters_use_existing_envelope(client, admin_key, query):
    response = client.get(
        "/api/v1/links", params=query, headers={"X-Admin-API-Key": admin_key}
    )
    assert response.status_code == 422
    assert set(response.json()) == {"success", "message", "data", "errors", "meta"}


def test_summary_openapi_and_envelope(client, admin_key):
    response = client.get(
        "/api/v1/admin/stats",
        headers={"X-Admin-API-Key": admin_key, "Accept-Language": "en"},
    )
    assert response.status_code == 200
    assert set(response.json()) == {"success", "message", "data", "errors", "meta"}
    assert response.json()["meta"]["language"] == "en"
    schema = client.get("/openapi.json").json()
    operation = schema["paths"]["/api/v1/admin/stats"]["get"]
    assert operation["security"] == [{"APIKeyHeader": []}]
    assert "200" in operation["responses"]
    parameters = schema["paths"]["/api/v1/links"]["get"]["parameters"]
    assert {p["name"] for p in parameters} >= {"q", "status", "limit", "offset"}
