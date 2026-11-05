# Quickstart: UniShort QR — incremento actual

Fecha: 2026-11-05. Se conserva FastAPI y el MVP existente.

La guía anterior correspondía al MVP `/shorten`. La interfaz actual usa
`POST /api/v1/links` con estado 201, siete símbolos y sin deduplicación.
Existen QR, caducidad, desactivación, métricas agregadas, Alembic y clave
administrativa provisional. Los roles y OIDC no están implementados.
Proyecto académico sin aprobación oficial de la UNL.

## Instalación y arranque

Desde raíz en PowerShell, siga [README](../../README.md), secciones 3–6.
Para conservar el original use una base demo antes de ejecutar Alembic:

```powershell
$env:UNISHORT_DATABASE_URL = "sqlite:///./demo-unishort.db"
$env:UNISHORT_BASE_URL = "http://localhost:8000"
$env:UNISHORT_ADMIN_API_KEY = [guid]::NewGuid().ToString("N")
Write-Host "Clave temporal de demo: $env:UNISHORT_ADMIN_API_KEY"
python -m alembic upgrade head
python -m uvicorn backend.app.main:app --host 127.0.0.1 --port 8000 --no-access-log
```

En otra terminal, desde raíz:

```powershell
python scripts/serve_frontend.py
```

## Verificación

1. Abrir `http://localhost:5500` y enviar `http://localhost:5500/?demo=unl`.
2. Comprobar URL corta, imagen y descarga PNG. El QR codifica la URL corta.
3. Abrir la URL corta: redirección 307 y contador incrementado.
4. Abrir `http://localhost:8000/docs`; Authorize con la clave temporal.
5. Listar enlaces y consultar stats. Sin clave: 401; incorrecta: 403.
6. Desactivar con PATCH o DELETE: redirección y QR responden 410.
7. Reactivar y asignar expiración futura; al vencer debe responder 410.
8. Probar URL inválida (400/422), código inexistente (404) y `/health` (200).
9. Reiniciar backend y comprobar persistencia. Registrar duración con una
   persona no técnica; esa aceptación sigue pendiente.

Prueba automática por TCP sobre base temporal: `python scripts/verify_runtime.py`.
Pruebas aisladas: `python -m pytest tests --cov=backend/app --cov-report=term-missing`.

Contratos: [v1](contracts/v1-links.md), [heredado](contracts/shorten.md),
[QR](../002-generate-qr/contracts/qr.md).
Evidencia: [informe](../../docs/evaluacion/verificacion-2026-11-05.md).

Docker: `docker compose up --build` (pendiente de ejecución local).
Portal: `python scripts/render_portal.py` requiere Quarto instalado;
`--prepare-only` prepara recursos sin afirmar que se renderizaron.
