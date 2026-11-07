"""Pruebas de configuración por variables de entorno."""

import pytest
from app.config import Settings, get_settings
from pydantic import ValidationError


def test_base_url_comes_from_environment_and_is_normalized(monkeypatch):
    monkeypatch.setenv("UNISHORT_BASE_URL", "https://qr.unl.edu.ec/")
    settings = Settings()

    assert settings.base_url == "https://qr.unl.edu.ec"


def test_base_url_must_be_absolute(monkeypatch):
    monkeypatch.setenv("UNISHORT_BASE_URL", "qr.unl.edu.ec")

    with pytest.raises(ValidationError):
        Settings()


def test_empty_admin_key_means_not_configured(monkeypatch):
    monkeypatch.setenv("UNISHORT_ADMIN_API_KEY", "   ")

    assert Settings().admin_api_key is None


def test_settings_representation_never_exposes_admin_key():
    settings = Settings(admin_api_key="audit-sentinel-never-log", _env_file=None)
    assert settings.admin_api_key == "audit-sentinel-never-log"
    assert "audit-sentinel-never-log" not in repr(settings)
    assert "audit-sentinel-never-log" not in str(settings)


def test_cached_settings_can_be_refreshed(monkeypatch):
    monkeypatch.setenv("UNISHORT_RATE_LIMIT_MAX", "7")
    get_settings.cache_clear()
    try:
        assert get_settings().rate_limit_max == 7
    finally:
        get_settings.cache_clear()
