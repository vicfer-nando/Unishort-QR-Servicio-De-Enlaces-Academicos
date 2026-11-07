"""Aceptación US2/US3 del panel sobre SQLite aislada."""

from datetime import datetime, timedelta, timezone

import pytest
from app.models import ShortURL


@pytest.fixture()
def dashboard(client_with_session, admin_key, monkeypatch):
    client, sessions = client_with_session
    now = datetime(2030, 1, 1, tzinfo=timezone.utc)
    monkeypatch.setattr("app.services.utc_now", lambda: now)
    monkeypatch.setattr("app.domain.utc_now", lambda: now)
    with sessions() as session:
        for index, (code, active, expiration, visits, url) in enumerate(
            [
                ("aaaaaaa", True, None, 4, "https://example.edu/Research"),
                ("bbbbbbb", False, None, 2, "https://example.edu/disabled"),
                (
                    "ccccccc",
                    True,
                    now - timedelta(seconds=1),
                    3,
                    "https://example.edu/past",
                ),
                (
                    "ddddddd",
                    False,
                    now - timedelta(days=1),
                    1,
                    "https://example.edu/both",
                ),
                (
                    "eeeeeee",
                    True,
                    now + timedelta(days=1),
                    5,
                    "https://example.edu/100%_literal",
                ),
                ("fffffff", True, now, 6, "https://example.edu/boundary"),
            ]
        ):
            session.add(
                ShortURL(
                    short_code=code,
                    original_url=url,
                    is_active=active,
                    expires_at=expiration,
                    click_count=visits,
                    created_at=now,
                )
            )
        session.commit()
    return client, {"X-Admin-API-Key": admin_key}, now


def test_global_summary_uses_domain_status_precedence(dashboard, monkeypatch):
    client, headers, now = dashboard
    monkeypatch.setattr("app.services.utc_now", lambda: now, raising=False)
    response = client.get("/api/v1/admin/stats", headers=headers)
    assert response.status_code == 200
    assert response.json()["data"] == {
        "total_links": 6,
        "active_links": 2,
        "inactive_links": 2,
        "expired_links": 2,
        "total_visits": 21,
    }


def test_summary_empty_database(client, admin_key):
    response = client.get("/api/v1/admin/stats", headers={"X-Admin-API-Key": admin_key})
    assert response.status_code == 200
    assert set(response.json()["data"].values()) == {0}


@pytest.mark.parametrize(
    "query,codes",
    [
        ({"q": "RESEARCH"}, ["aaaaaaa"]),
        ({"q": "BBB"}, ["bbbbbbb"]),
        ({"q": "%_"}, ["eeeeeee"]),
        ({"q": "' OR 1=1 --"}, []),
        ({"status": "active"}, ["eeeeeee", "aaaaaaa"]),
        ({"status": "inactive"}, ["ddddddd", "bbbbbbb"]),
        ({"status": "expired"}, ["fffffff", "ccccccc"]),
        ({"status": "inactive", "q": "Research"}, []),
    ],
)
def test_search_and_status_filters(dashboard, monkeypatch, query, codes):
    client, headers, now = dashboard
    monkeypatch.setattr("app.services.utc_now", lambda: now, raising=False)
    response = client.get("/api/v1/links", params=query, headers=headers)
    assert response.status_code == 200
    assert [item["short_code"] for item in response.json()["data"]["items"]] == codes
    assert response.json()["data"]["total"] == len(codes)
    if "status" in query:
        assert all(
            item["status"] == query["status"]
            for item in response.json()["data"]["items"]
        )


def test_filtered_pagination_has_stable_order(dashboard, monkeypatch):
    client, headers, now = dashboard
    monkeypatch.setattr("app.services.utc_now", lambda: now, raising=False)
    response = client.get(
        "/api/v1/links",
        params={"limit": 1, "offset": 1, "status": "inactive"},
        headers=headers,
    )
    data = response.json()["data"]
    assert data["total"] == 2
    assert data["items"][0]["short_code"] == "bbbbbbb"
    assert (
        client.get("/api/v1/links?offset=100", headers=headers).json()["data"]["items"]
        == []
    )


def test_reactivation_does_not_bypass_expiration(client_with_session, admin_key):
    client, sessions = client_with_session
    headers = {"X-Admin-API-Key": admin_key}
    code = client.post("/api/v1/links", json={"url": "https://example.edu"}).json()[
        "data"
    ]["short_code"]
    with sessions() as session:
        link = session.query(ShortURL).filter_by(short_code=code).one()
        link.expires_at = datetime.now(timezone.utc) - timedelta(days=1)
        link.is_active = False
        session.commit()
    response = client.patch(
        f"/api/v1/links/{code}", json={"is_active": True}, headers=headers
    )
    assert response.json()["data"]["status"] == "expired"
    assert client.get(f"/s/{code}", follow_redirects=False).status_code == 410
    assert client.get(f"/api/v1/links/{code}/qr").status_code == 410
    rejected = client.patch(
        f"/api/v1/links/{code}",
        json={"is_active": False, "expires_at": "2000-01-01T00:00:00Z"},
        headers=headers,
    )
    assert rejected.status_code == 422
    assert client.get(f"/api/v1/links/{code}").json()["data"]["is_active"] is True
    restored = client.patch(
        f"/api/v1/links/{code}", json={"expires_at": None}, headers=headers
    )
    assert restored.json()["data"]["status"] == "active"
    assert client.get(f"/api/v1/links/{code}/qr").status_code == 200


def test_summary_failure_is_controlled(client, admin_key, monkeypatch):
    from sqlalchemy.exc import SQLAlchemyError

    def fail(*args, **kwargs):
        raise SQLAlchemyError("private database details")

    monkeypatch.setattr("app.repository.get_admin_stats", fail, raising=False)
    response = client.get("/api/v1/admin/stats", headers={"X-Admin-API-Key": admin_key})
    assert response.status_code == 500
    assert response.json()["success"] is False
    assert "private database details" not in response.text
