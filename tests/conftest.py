import os
import sys
import tempfile
from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

BACKEND_DIR = Path(__file__).resolve().parents[1] / "backend"
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

# Nunca heredar una base real del entorno o de .env durante la colección.
_BOOTSTRAP_DIRECTORY = tempfile.TemporaryDirectory(prefix="unishort-pytest-")
_BOOTSTRAP_DB = Path(_BOOTSTRAP_DIRECTORY.name) / "bootstrap.db"
os.environ["UNISHORT_DATABASE_URL"] = f"sqlite:///{_BOOTSTRAP_DB.as_posix()}"
os.environ["UNISHORT_BASE_URL"] = "http://localhost:8000"

from app.database import Base, get_db  # noqa: E402
from app.database import engine as bootstrap_engine  # noqa: E402
from app.main import app  # noqa: E402


def pytest_sessionfinish(session, exitstatus):
    """Cierra SQLite antes de limpiar el directorio temporal en Windows."""

    app.state.rate_limiter.reset()
    bootstrap_engine.dispose()
    _BOOTSTRAP_DIRECTORY.cleanup()


def _build_test_engine():
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    testing_session = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    Base.metadata.create_all(bind=engine)
    return engine, testing_session


@pytest.fixture()
def client():
    engine, testing_session = _build_test_engine()

    def override_get_db():
        db = testing_session()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db
    limiter = getattr(app.state, "rate_limiter", None)
    if limiter is not None:
        limiter.reset()
    try:
        with TestClient(app) as test_client:
            yield test_client
    finally:
        app.dependency_overrides.clear()
        Base.metadata.drop_all(bind=engine)
        engine.dispose()


@pytest.fixture()
def client_with_session():
    """Cliente de pruebas que además expone la fábrica de sesiones aislada."""

    engine, testing_session = _build_test_engine()

    def override_get_db():
        db = testing_session()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db
    limiter = getattr(app.state, "rate_limiter", None)
    if limiter is not None:
        limiter.reset()
    try:
        with TestClient(app) as test_client:
            yield test_client, testing_session
    finally:
        app.dependency_overrides.clear()
        Base.metadata.drop_all(bind=engine)
        engine.dispose()


@pytest.fixture()
def db_session():
    """Sesión aislada sobre SQLite en memoria para pruebas de repositorio."""

    engine, testing_session = _build_test_engine()
    session = testing_session()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine)
        engine.dispose()


@pytest.fixture()
def admin_key(monkeypatch):
    """Configura una clave administrativa provisional para las pruebas."""

    from app.config import get_settings

    key = "test-admin-key"
    monkeypatch.setenv("UNISHORT_ADMIN_API_KEY", key)
    get_settings.cache_clear()
    yield key
    get_settings.cache_clear()


@pytest.fixture()
def fake_clock():
    """Reloj monotónico controlable para pruebas de límites y expiración."""

    class FakeClock:
        def __init__(self) -> None:
            self.current = 1000.0

        def __call__(self) -> float:
            return self.current

        def advance(self, seconds: float) -> None:
            self.current += seconds

    return FakeClock()
