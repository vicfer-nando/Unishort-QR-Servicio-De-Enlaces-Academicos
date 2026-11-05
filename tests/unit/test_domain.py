"""Pruebas unitarias del dominio: URL, códigos y fechas."""

from datetime import datetime, timedelta, timezone

import pytest
from app.domain import (
    SHORT_CODE_ALPHABET,
    build_short_url,
    generate_short_code,
    is_expired,
    normalize_expiration,
    validate_destination_url,
)
from app.errors import (
    EmbeddedCredentialsError,
    EmptyURLError,
    InvalidExpirationError,
    InvalidHostError,
    InvalidSchemeError,
    InvalidURLDomainError,
    URLLengthError,
)


def test_valid_url_is_preserved_without_outer_whitespace():
    assert (
        validate_destination_url("  https://www.example.com/a?b=1  ")
        == "https://www.example.com/a?b=1"
    )


@pytest.mark.parametrize("value", ["", "   ", "\t\n"])
def test_empty_urls_are_rejected(value):
    with pytest.raises(EmptyURLError):
        validate_destination_url(value)


@pytest.mark.parametrize(
    "value",
    ["ftp://example.com/file", "javascript:alert(1)", "data:text/plain,hola"],
)
def test_non_http_schemes_are_rejected(value):
    with pytest.raises(InvalidSchemeError):
        validate_destination_url(value)


@pytest.mark.parametrize("value", ["https://", "http:///path", "not-a-url"])
def test_missing_or_invalid_host_is_rejected(value):
    with pytest.raises((InvalidHostError, InvalidSchemeError)):
        validate_destination_url(value)


def test_embedded_credentials_are_rejected():
    with pytest.raises(EmbeddedCredentialsError):
        validate_destination_url("https://usuario:clave@example.com/recurso")


def test_internal_whitespace_is_rejected():
    with pytest.raises(InvalidURLDomainError):
        validate_destination_url("https://exa mple.com/ruta")


def test_url_over_the_limit_is_rejected():
    with pytest.raises(URLLengthError):
        validate_destination_url("https://example.com/" + "a" * 2049)


def test_codes_use_unambiguous_alphabet_and_requested_length():
    code = generate_short_code()
    assert len(code) == 7
    assert set(code) <= set(SHORT_CODE_ALPHABET)
    assert not set(code) & set("0O1lo@")


def test_ten_thousand_codes_are_unique():
    codes = {generate_short_code() for _ in range(10_000)}
    assert len(codes) == 10_000


def test_code_generator_can_be_injected_for_determinism():
    assert generate_short_code(4, chooser=lambda alphabet: alphabet[0]) == "aaaa"


def test_expiration_is_normalized_to_utc():
    naive = datetime(2030, 1, 1, 12, 0, 0)
    normalized = normalize_expiration(naive)
    assert normalized.tzinfo is timezone.utc
    assert normalized.hour == 12


def test_past_expiration_is_rejected():
    with pytest.raises(InvalidExpirationError):
        normalize_expiration(datetime.now(timezone.utc) - timedelta(seconds=1))


def test_is_expired_handles_none_naive_and_aware_values():
    now = datetime(2030, 1, 1, tzinfo=timezone.utc)
    assert is_expired(None, now=now) is False
    assert is_expired(datetime(2029, 12, 31), now=now) is True
    assert is_expired(datetime(2030, 1, 2, tzinfo=timezone.utc), now=now) is False


def test_short_url_is_built_from_configured_base():
    assert (
        build_short_url("https://qr.unl.edu.ec/", "abc2345")
        == "https://qr.unl.edu.ec/s/abc2345"
    )
