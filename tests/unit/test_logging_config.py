"""Pruebas del registro estructurado y de la redacción de datos sensibles."""

import io
import json
import logging
import sys
from datetime import datetime, timezone

from app.logging_config import (
    JsonFormatter,
    configure_logging,
    get_request_id,
    reset_request_id,
    set_request_id,
)


def _record(message: str, **extra):
    record = logging.LogRecord(
        "unishort.test", logging.INFO, __file__, 1, message, (), None
    )
    for key, value in extra.items():
        setattr(record, key, value)
    return record


def test_json_formatter_emits_utc_metadata_and_request_id():
    token = set_request_id("req-123")
    try:
        payload = json.loads(JsonFormatter().format(_record("hola")))
    finally:
        reset_request_id(token)

    assert payload["service"] == "unishort-qr"
    assert payload["level"] == "INFO"
    assert payload["logger"] == "unishort.test"
    assert payload["message"] == "hola"
    assert payload["request_id"] == "req-123"
    assert payload["timestamp"].endswith("+00:00")


def test_json_formatter_redacts_sensitive_extra_fields():
    payload = json.loads(
        JsonFormatter().format(
            _record(
                "evento",
                original_url="https://privado.example/ruta",
                admin_api_key="clave-secreta",
                user_agent="agente",
                short_code="abc123",
            )
        )
    )

    assert "original_url" not in payload
    assert "admin_api_key" not in payload
    assert "user_agent" not in payload
    assert payload["short_code"] == "abc123"


def test_json_formatter_redacts_urls_and_secrets_inside_messages():
    payload = json.loads(
        JsonFormatter().format(
            _record("fallo en https://privado.example/a?token=abc api_key=xyz")
        )
    )

    assert "privado.example" not in payload["message"]
    assert "abc" not in payload["message"]
    assert "xyz" not in payload["message"]
    assert "<redacted" in payload["message"]


def test_json_formatter_sanitizes_nested_mappings_and_exceptions():
    try:
        raise RuntimeError("token=abc https://privado.example/x")
    except RuntimeError:
        exc_info = sys.exc_info()

    record = _record(
        "error",
        context={"authorization": "Bearer xyz", "safe": "https://ejemplo.example"},
    )
    record.exc_info = exc_info
    payload = json.loads(JsonFormatter().format(record))

    assert payload["context"]["authorization"] == "<redacted>"
    assert payload["context"]["safe"] == "<redacted-url>"
    assert "privado.example" not in payload["exception"]
    assert "abc" not in payload["exception"]


def test_json_formatter_converts_numeric_datetime_sequences_and_objects():
    class CustomValue:
        def __str__(self):
            return "https://privado.example/x"

    payload = json.loads(
        JsonFormatter().format(
            _record(
                "tipos",
                count=3,
                ratio=1.5,
                enabled=True,
                missing=None,
                occurred=datetime(2026, 11, 5, 12, 0, tzinfo=timezone.utc),
                tags=["uno", {"token": "secreto"}],
                custom=CustomValue(),
            )
        )
    )

    assert payload["count"] == 3
    assert payload["ratio"] == 1.5
    assert payload["enabled"] is True
    assert payload["missing"] is None
    assert payload["occurred"] == "2026-11-05T12:00:00+00:00"
    assert payload["tags"] == ["uno", {"token": "<redacted>"}]
    assert payload["custom"] == "<redacted-url>"


def test_configure_logging_is_idempotent_and_writes_json():
    stream = io.StringIO()
    root = logging.getLogger()
    original_level = root.level
    try:
        configure_logging(logging.INFO, stream=stream, force=True)
        configure_logging(logging.INFO, stream=stream, force=True)
        handlers = [
            handler
            for handler in root.handlers
            if getattr(handler, "_unishort_json", False)
        ]
        logging.getLogger("unishort.test").info("mensaje", extra={"short_code": "x"})
    finally:
        for handler in list(root.handlers):
            if getattr(handler, "_unishort_json", False):
                root.removeHandler(handler)
        root.setLevel(original_level)

    assert len(handlers) == 1
    payload = json.loads(stream.getvalue().strip())
    assert payload["message"] == "mensaje"
    assert payload["short_code"] == "x"


def test_request_id_helpers_restore_context():
    assert get_request_id() is None
    token = set_request_id("uno")
    try:
        assert get_request_id() == "uno"
        inner = set_request_id("dos")
        try:
            assert get_request_id() == "dos"
        finally:
            reset_request_id(inner)
        assert get_request_id() == "uno"
    finally:
        reset_request_id(token)
    assert get_request_id() is None


def test_formatter_redacts_pii_and_bearer_and_never_serializes_sql_parameters():
    record = _record(
        "person@example.edu 192.0.2.1 2001:db8::1 authorization=Bearer abc"
    )
    record.exc_info = (
        RuntimeError,
        RuntimeError("bound parameter: private-person"),
        None,
    )
    payload = json.loads(JsonFormatter().format(record))
    assert "person@" not in payload["message"]
    assert "192.0.2.1" not in payload["message"]
    assert "2001:db8::1" not in payload["message"]
    assert "abc" not in payload["message"]
    assert payload["exception"] == "RuntimeError"
