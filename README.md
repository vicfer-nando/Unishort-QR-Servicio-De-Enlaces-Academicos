# UniShort QR

Servicio académico de **enlaces cortos persistentes y códigos QR**. Facilita compartir
recursos extensos desde aulas, presentaciones y material impreso. Proyecto de la
Evaluación Sumativa 1 de la Universidad Nacional de Loja, **6 de noviembre de 2026**;
no representa una integración ni aprobación institucional.

El incremento conserva el generador público y añade un **panel administrativo**:
acceso provisional, resumen agregado, búsqueda, filtros, paginación, visitas,
desactivación/reactivación y caducidad con confirmación. No hay borrado físico.

**Tecnologías:** Python/FastAPI, Pydantic, SQLAlchemy, SQLite/Alembic, HTML/CSS/JavaScript,
qrcode/Pillow; pytest, Node, Ruff y mypy; Docker/Nginx, Actions y Quarto.
[ADR de FastAPI](docs/adr/0001-fastapi-vs-django-rest-framework.md): continuidad del
proyecto y API tipada, sin reconstrucción en otro framework.

## Entrega y documentación

- **[Dossier final para el evaluador](docs/evaluacion/entrega-final/README.md)**:
  rúbrica, guion, reproducción, capturas, fichas individuales, IA y texto EVA.
- [Resultados efectivos y límites](docs/evaluacion/entrega-final/resultados-verificacion.md).
- [Portal Quarto: fuentes](quarto/index.qmd) y [publicación reproducible](docs/evaluacion/entrega-final/publicacion-quarto.md).
- **URL pública Quarto: [PENDIENTE: publicar y verificar GitHub Pages].**
- [Auditoría previa contra el PDF oficial](docs/evaluacion/auditoria-final-rubrica.md).
- [Especificaciones 001–003](specs/features.md), [BPMN](docs/procesos/analisis-bpmn.md),
  [C4](docs/arquitectura/unishort-c4.dsl), [UML](docs/arquitectura/c4-codigo.puml).

Los cambios locales deben revisarse e integrarse antes de entregar: un enlace al
repositorio no garantiza que main ya los contenga. No se publican automáticamente.

## Instalar en Windows 11

Requisitos: Git, Python 3.13; Node 22+ para las pruebas JS. Desde una copia:

```powershell
git clone https://github.com/vicfer-nando/Unishort-QR-Servicio-De-Enlaces-Academicos.git
Set-Location Unishort-QR-Servicio-De-Enlaces-Academicos
py -3.13 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements-dev.lock
.\.venv\Scripts\python.exe -m pip check
```

No hace falta activar el entorno ni cambiar ExecutionPolicy. Los locks fijan versiones.

## Iniciar una demostración segura

Primera terminal, en raíz: base **nueva y aislada**, migraciones y backend.

```powershell
$demoDirectory = Join-Path ([IO.Path]::GetTempPath()) ("unishort-demo-" + [guid]::NewGuid().ToString("N"))
New-Item -ItemType Directory -Path $demoDirectory | Out-Null
$env:UNISHORT_DATABASE_URL = "sqlite:///$($demoDirectory.Replace('\', '/'))/demo.db"
$env:UNISHORT_BASE_URL = "http://localhost:8000"
$env:UNISHORT_CORS_ORIGINS = "http://localhost:5500,http://127.0.0.1:5500"
$adminSecret = Read-Host "Define una clave temporal para el panel" -AsSecureString
$env:UNISHORT_ADMIN_API_KEY = [Net.NetworkCredential]::new("", $adminSecret).Password
Remove-Variable adminSecret
.\.venv\Scripts\python.exe -m alembic upgrade head
.\.venv\Scripts\python.exe -m uvicorn backend.app.main:app --host 127.0.0.1 --port 8000 --no-access-log
```

Segunda terminal en raíz:

```powershell
.\.venv\Scripts\python.exe scripts/serve_frontend.py
```

| Interfaz | Dirección local |
|---|---|
| Acortador/QR | <http://localhost:5500/index.html> |
| Panel | <http://localhost:5500/admin.html> |
| Swagger | <http://localhost:8000/docs> |
| OpenAPI | <http://localhost:8000/openapi.json> |
| Salud | <http://localhost:8000/health> |

Introducir en el panel la misma clave leída de forma oculta. No aparece en URL ni
se guarda en storage/cookies: solo memoria de la página. Logout/recargar descarta
esa copia; el backend comprueba permisos en cada operación. Sin configuración
administrativa devuelve 503; sin cabecera 401; clave incorrecta 403.

Al terminar: Ctrl+C en ambas terminales; quitar las variables de clave/base en la
primera con `Remove-Item Env:UNISHORT_ADMIN_API_KEY` y `Remove-Item Env:UNISHORT_DATABASE_URL`.
La base temporal permanece; no se borra unishort.db ni demo-unishort.db.
[Guía completa, variables, persistencia y Docker](docs/evaluacion/entrega-final/instrucciones-reproduccion.md).

## API y pruebas

`POST /api/v1/links`, `GET /api/v1/links/{code}` y `/qr` son públicos;
listado, `/api/v1/admin/stats`, estadísticas individuales y cambios requieren clave.
`GET /s/{code}` redirige con 307. Envelope v1: success, message, data, errors, meta;
errors es [] en éxito. PNG/307 tienen su representación HTTP; JSON legacy plano
se conserva por compatibilidad ([ADR 0005](docs/adr/0005-api-versionada-envelope-errores.md)).

```powershell
$testTemp = Join-Path ([IO.Path]::GetTempPath()) ("unishort-tests-" + [guid]::NewGuid().ToString("N"))
.\.venv\Scripts\python.exe -m pytest tests --cov=backend/app --cov-report=term-missing -p no:cacheprovider --basetemp=$testTemp
.\.venv\Scripts\python.exe -m ruff check backend tests alembic scripts
.\.venv\Scripts\python.exe -m ruff format --check backend tests alembic scripts
.\.venv\Scripts\python.exe -m mypy backend/app
node scripts/verify_frontend.mjs
node --test tests/js/admin.test.mjs
```

Usar un basetemp exclusivo nuevo. [Resultados](docs/evaluacion/entrega-final/resultados-verificacion.md)
separan la suite actual de históricos y de las verificaciones pendientes.

## Construir documentación y entregar

[Instrucciones Quarto/diagramas](docs/evaluacion/entrega-final/instrucciones-reproduccion.md)
y [workflow Pages manual](docs/evaluacion/entrega-final/publicacion-quarto.md).
El sitio generado queda en quarto/_site; los ocho SVG se exportan desde BPMN/DSL/UML,
con fuentes conservadas. Actions puede construir sin mantener encendida la PC.
La publicación requiere configuración Pages, revisión y ejecución manual autorizada.

## Límites y colaboración

Autenticación compartida provisional, sin identidad/roles/MFA; HTTPS obligatorio
fuera de loopback. Límite de solicitudes por proceso; PostgreSQL y despliegue de
producción son futuros. Una URL puede contener datos sensibles; no recopilar
metadatos de visitantes no elimina ese riesgo. No registrar secretos/destinos completos.

[Contribución real y PR](docs/evaluacion/entrega-final/contribuciones-individuales.md),
[declaración IA](docs/evaluacion/entrega-final/declaracion-uso-ia.md) y
[estrategia de ramas](docs/CONTRIBUTING.md). Las revisiones/reflexiones personales,
capturas y entrega EVA requieren intervención humana; no se simulan con documentación.
