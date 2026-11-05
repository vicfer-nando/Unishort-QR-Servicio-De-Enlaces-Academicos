"""Validación de URL pública antes de emitir enlaces o QR inutilizables."""

import pytest
from app.config import Settings
from pydantic import ValidationError


@pytest.mark.parametrize(
    "base_url",
    [
        "https://",
        "https://user:password@example.edu",
        "https://[bad",
        "https://example.edu?token=secret",
        "https://example.edu/#fragment",
    ],
)
def test_invalid_public_url_fails_at_configuration(base_url):
    with pytest.raises(ValidationError):
        Settings(base_url=base_url, _env_file=None)
