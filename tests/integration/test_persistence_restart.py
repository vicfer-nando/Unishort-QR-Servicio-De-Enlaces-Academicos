"""Prueba de persistencia real: el enlace sobrevive a reabrir la base."""

import tempfile
from pathlib import Path

from app import repository
from app.database import Base
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker


def test_link_survives_engine_restart():
    database_path = Path(tempfile.gettempdir()) / "unishort_restart_test.db"
    if database_path.exists():
        database_path.unlink()
    database_url = f"sqlite:///{database_path.as_posix()}"

    first_engine = create_engine(
        database_url, connect_args={"check_same_thread": False}
    )
    Base.metadata.create_all(bind=first_engine)
    first_session = sessionmaker(bind=first_engine)()
    link = repository.create_link(
        first_session,
        "https://example.com/persistente",
        code_generator=lambda: "fffffff",
    )
    first_session.close()
    first_engine.dispose()

    second_engine = create_engine(
        database_url, connect_args={"check_same_thread": False}
    )
    second_session = sessionmaker(bind=second_engine)()
    recovered = repository.get_by_code(second_session, link.short_code)

    assert recovered is not None
    assert recovered.original_url == "https://example.com/persistente"

    second_session.close()
    second_engine.dispose()
    cleanup_engine = create_engine(database_url)
    Base.metadata.drop_all(bind=cleanup_engine)
    cleanup_engine.dispose()
    database_path.unlink(missing_ok=True)
