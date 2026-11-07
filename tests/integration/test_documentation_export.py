"""Verifica exportación real de OpenAPI sin usar datos o secretos del entorno."""

import json
import runpy
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def test_openapi_export_uses_temporary_database_and_contains_admin_contract(
    tmp_path, monkeypatch
):
    forbidden = tmp_path / "must-not-be-created.db"
    output = tmp_path / "openapi.json"
    monkeypatch.setenv("UNISHORT_DATABASE_URL", f"sqlite:///{forbidden.as_posix()}")
    monkeypatch.setenv("UNISHORT_ADMIN_API_KEY", "export-sentinel-not-public")
    module = runpy.run_path(str(ROOT / "scripts/render_portal.py"))
    module["export_openapi"](output)
    assert not forbidden.exists()
    schema = json.loads(output.read_text(encoding="utf-8"))
    assert "/api/v1/admin/stats" in schema["paths"]
    assert "/api/v1/links" in schema["paths"]
    assert schema["paths"]["/api/v1/admin/stats"]["get"]["security"] == [
        {"APIKeyHeader": []}
    ]
    assert "export-sentinel-not-public" not in output.read_text(encoding="utf-8")
