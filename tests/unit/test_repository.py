"""Pruebas del repositorio: colisiones, métricas y fallos de persistencia."""

from unittest.mock import MagicMock

import pytest
from app import repository
from app.errors import CollisionExhaustedError, PersistenceError
from sqlalchemy.exc import SQLAlchemyError


def _sequence_generator(*codes):
    values = list(codes)

    def generator():
        return values.pop(0)

    return generator


def test_collision_retries_without_overwriting_existing_link(db_session):
    first = repository.create_link(
        db_session,
        "https://example.com/primero",
        code_generator=lambda: "aaaaaaa",
    )

    second = repository.create_link(
        db_session,
        "https://example.com/segundo",
        code_generator=_sequence_generator("aaaaaaa", "bbbbbbb"),
    )

    db_session.refresh(first)
    assert first.original_url == "https://example.com/primero"
    assert first.short_code == "aaaaaaa"
    assert second.short_code == "bbbbbbb"
    assert second.original_url == "https://example.com/segundo"


def test_collision_exhaustion_raises_domain_error(db_session):
    repository.create_link(
        db_session,
        "https://example.com/ocupado",
        code_generator=lambda: "ccccccc",
    )

    with pytest.raises(CollisionExhaustedError):
        repository.create_link(
            db_session,
            "https://example.com/nuevo",
            code_generator=lambda: "ccccccc",
        )


def test_persistence_failure_rolls_back_and_raises():
    session = MagicMock()
    session.commit.side_effect = SQLAlchemyError("fallo simulado")

    with pytest.raises(PersistenceError):
        repository.create_link(
            session,
            "https://example.com/fallo",
            code_generator=lambda: "ddddddd",
        )

    session.rollback.assert_called_once()


def test_click_counter_is_aggregated(db_session):
    link = repository.create_link(
        db_session,
        "https://example.com/clics",
        code_generator=lambda: "eeeeeee",
    )
    repository.increment_click_count(db_session, link.short_code)
    repository.increment_click_count(db_session, link.short_code)
    db_session.refresh(link)
    assert link.click_count == 2
