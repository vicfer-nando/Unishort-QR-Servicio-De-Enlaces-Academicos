"""Verifica agregación y búsquedas sin materializar toda la tabla."""

from datetime import datetime, timedelta, timezone

from app import repository
from app.models import ShortURL
from sqlalchemy import event


def test_summary_is_one_sql_query_without_loading_link_entities(db_session):
    now = datetime(2030, 1, 1, tzinfo=timezone.utc)
    db_session.add_all(
        [
            ShortURL(
                short_code="aaaaaaa",
                original_url="https://example.edu/a",
                click_count=2,
            ),
            ShortURL(
                short_code="bbbbbbb",
                original_url="https://example.edu/b",
                is_active=False,
                expires_at=now - timedelta(days=1),
                click_count=7,
            ),
            ShortURL(
                short_code="ccccccc",
                original_url="https://example.edu/c",
                expires_at=now,
                click_count=3,
            ),
        ]
    )
    db_session.commit()
    db_session.expunge_all()
    statements = []

    def record(connection, cursor, statement, parameters, context, executemany):
        statements.append(statement)

    event.listen(db_session.bind, "before_cursor_execute", record)
    try:
        stats = repository.get_admin_stats(db_session, now)
    finally:
        event.remove(db_session.bind, "before_cursor_execute", record)
    assert stats == {
        "total_links": 3,
        "active_links": 1,
        "inactive_links": 1,
        "expired_links": 1,
        "total_visits": 12,
    }
    assert len(statements) == 1
    assert "sum(" in statements[0].lower()
    assert not db_session.identity_map


def test_literal_search_escapes_escape_character_and_wildcards(db_session):
    repository.create_link(
        db_session, "https://example.edu/a/%_path", code_generator=lambda: "aaaaaaa"
    )
    repository.create_link(
        db_session, "https://example.edu/a/other", code_generator=lambda: "bbbbbbb"
    )
    for query, expected in [("/%_", 1), ("/", 2), ("\\", 0), ("%", 1), ("_", 1)]:
        links = repository.list_links(db_session, q=query)
        assert len(links) == expected
        assert repository.count_links(db_session, q=query) == expected
