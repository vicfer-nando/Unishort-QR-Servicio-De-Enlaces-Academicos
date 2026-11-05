# UniShort QR

Servicio institucional de acortamiento de enlaces y generación de códigos QR
para la Universidad Nacional de Loja. Proyecto académico: no constituye una
aprobación oficial de la universidad.

Este repositorio contiene un incremento funcional sobre el MVP existente:
creación de enlaces, redirección, QR, caducidad, desactivación, métricas
agregadas, API REST versionada y controles básicos de seguridad.

## 1. Estado del incremento

| Capacidad | Estado | Evidencia |
|-----------|--------|-----------|
| Crear enlace corto con código único | Implementado | `POST /api/v1/links`, `tests/contract` |
| Redirección 307 sin cuerpo JSON | Implementado | `GET /s/{short_code}` |
| QR que codifica la URL corta | Implementado | `GET /api/v1/links/{code}/qr`, `tests/integration/test_qr.py` |
| Caducidad y desactivación | Implementado | `PATCH`/`DELETE`, columnas `expires_at`, `is_active` |
| Métricas agregadas sin PII | Implementado | `click_count`, `GET .../stats` |
| Autenticación administrativa provisional | Implementado | `X-Admin-API-Key`, `tests/security` |
| Health check | Implementado | `GET /health` |
| API heredada | Conservada | `POST /shorten`, `GET /s/{code}` |
| PostgreSQL en producción | Documentado, no implementado | `docs/adr/0002-*` |

> La generación de QR se especificó en `specs/002-generate-qr/spec.md` y su
> contrato en `specs/002-generate-qr/contracts/qr.md`.

## 2. Tecnologías

- Python 3.11+ (probado con 3.13).
- FastAPI + Uvicorn.
- Pydantic v2 + pydantic-settings.
- SQLAlchemy 2.x + SQLite.
- qrcode + Pillow.
- Pytest + httpx + OpenCV (decodificación de QR en pruebas).
- Quarto (portal técnico), Structurizr DSL y PlantUML (diagramas).

La justificación de FastAPI frente a Django REST Framework está en
[`docs/adr/0001-fastapi-vs-django-rest-framework.md`](docs/adr/0001-fastapi-vs-django-rest-framework.md).

## 3. Instalación en Windows

Desde la raíz del repositorio, en PowerShell:

```powershell
py -m venv .venv
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r backend\requirements-dev.txt
```

Para reproducir exactamente las versiones verificadas, use los locks generados
desde un entorno limpio: `requirements.lock` (servicio) y
`requirements-dev.lock` (servicio + pruebas y herramientas).

Si no se usa entorno virtual, basta con instalar las dependencias en el Python
global. Para ejecutar solo el servicio no hacen falta las dependencias de
prueba: `backend\requirements.txt`.

## 4. Configuración

La configuración se lee de variables de entorno con prefijo `UNISHORT_` y,
opcionalmente, de un archivo `.env` en la raíz. Copia `.env.example` y ajusta
los valores. **No confirmes secretos reales.**

| Variable | Valor por defecto | Uso |
|----------|-------------------|-----|
| `UNISHORT_DATABASE_URL` | `sqlite:///<raíz>/unishort.db` | Motor de datos. Conserva la BD existente. |
| `UNISHORT_BASE_URL` | `http://localhost:8000` | Dominio usado en `short_url` y en el QR. |
| `UNISHORT_ADMIN_API_KEY` | vacío | Clave provisional de administración. Si falta, los endpoints admin responden 503. |
| `UNISHORT_RATE_LIMIT_ENABLED` | `true` | Activa el límite de creación. |
| `UNISHORT_RATE_LIMIT_MAX` | `60` | Creaciones por ventana y cliente. |
| `UNISHORT_RATE_LIMIT_WINDOW_SECONDS` | `60` | Ventana en segundos (máximo 60). |
| `UNISHORT_SHORT_CODE_LENGTH` | `7` | Longitud del código en v1. |
| `UNISHORT_QR_BOX_SIZE` | `10` | Tamaño de módulo del QR. |
| `UNISHORT_LOG_LEVEL` | `INFO` | Nivel del registro estructurado JSON. |
| `UNISHORT_CORS_ORIGINS` | `*` | Orígenes permitidos separados por coma. |

No se almacenan direcciones IP, cookies, User-Agent ni datos personales de los
visitantes. El limitador usa la IP solo como clave efímera en memoria y el
registro JSON redacta URLs de destino, claves, cookies y agentes de usuario.

## 5. Ejecución del backend

Desde la raíz del repositorio:

```powershell
$env:UNISHORT_BASE_URL = "http://localhost:8000"
$env:UNISHORT_ADMIN_API_KEY = "dev-admin-cambiar-en-produccion"
python -m uvicorn backend.app.main:app --reload --host 127.0.0.1 --port 8000 --no-access-log
```

Alternativa desde `backend`:

```powershell
cd backend
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000 --no-access-log
```

- Swagger UI: <http://127.0.0.1:8000/docs>
- OpenAPI JSON: <http://127.0.0.1:8000/openapi.json>
- Health check: <http://127.0.0.1:8000/health>

> `--no-access-log` evita que el registro de acceso de Uvicorn incluya la IP del
> cliente, conforme al principio de privacidad del proyecto.

### Migraciones de base de datos

Alembic adopta de forma aditiva la base existente, sin borrar enlaces:

```powershell
python -m alembic upgrade head
```

Las migraciones crean la tabla si no existe, agregan solo las columnas o
índices faltantes y conservan los datos de `unishort.db`. El `downgrade` elimina
la tabla y exige confirmación explícita:

```powershell
$env:UNISHORT_ALEMBIC_ALLOW_DESTRUCTIVE_DOWNGRADE = "1"
python -m alembic downgrade base
```

No defina esa variable en producción salvo que acepte perder los datos.

## 6. Frontend

En otra terminal, desde la raíz (sin logs de IP ni consultas):

```powershell
python scripts/serve_frontend.py
```

Abre <http://localhost:5500>. El frontend llama a
`http://localhost:8000/api/v1` y muestra también el QR descargable. Si cambias
el host o el puerto del backend, define `window.UNISHORT_API_BASE_URL` antes de
cargar el script o ajusta el valor por defecto en `frontend/index.html`. La API
refleja `X-Request-Id` y expone `X-Log-Request-Id`, generado por el servidor
para encontrar los logs sin registrar cabeceras arbitrarias del cliente.

## 7. API

### 7.1 Crear enlace (versionada)

```powershell
$body = @{ url = "https://www.example.com/articulo?lang=es" } | ConvertTo-Json
Invoke-RestMethod -Method Post -Uri "http://localhost:8000/api/v1/links" -ContentType "application/json" -Body $body
```

Respuesta `201` con envelope:

```json
{
  "success": true,
  "message": "Enlace corto creado correctamente.",
  "data": {
    "short_code": "abc2345",
    "short_url": "http://localhost:8000/s/abc2345",
    "original_url": "https://www.example.com/articulo?lang=es",
    "qr_url": "http://localhost:8000/api/v1/links/abc2345/qr",
    "created_at": "2026-11-06T12:00:00+00:00",
    "expires_at": null,
    "is_active": true,
    "click_count": 0,
    "status": "active"
  },
  "errors": [],
  "meta": {"request_id": "...", "api_version": "1.0.0", "language": "es"}
}
```

### 7.2 Redirección

```powershell
Invoke-WebRequest -Uri "http://localhost:8000/s/abc2345" -MaximumRedirection 0
```

Responde `307` con `Location`. No incluye cuerpo JSON. Un código desactivado o
caducado responde `410` con envelope; uno inexistente responde `404`.

### 7.3 QR

```powershell
Invoke-WebRequest -Uri "http://localhost:8000/api/v1/links/abc2345/qr" -OutFile "qr.png"
```

El PNG contiene exactamente `http://localhost:8000/s/abc2345`, no la URL de
destino.

### 7.4 Administración

```powershell
$headers = @{ "X-Admin-API-Key" = "dev-admin-cambiar-en-produccion" }
Invoke-RestMethod -Uri "http://localhost:8000/api/v1/links" -Headers $headers
Invoke-RestMethod -Method Patch -Uri "http://localhost:8000/api/v1/links/abc2345" `
  -Headers $headers -ContentType "application/json" -Body '{"is_active": false}'
Invoke-RestMethod -Uri "http://localhost:8000/api/v1/links/abc2345/stats" -Headers $headers
```

Sin cabecera: `401`. Con clave incorrecta: `403`. Sin clave configurada en el
servidor: `503`.

### 7.5 Compatibilidad heredada

`POST /shorten` conserva el comportamiento anterior (200, deduplicación, código
de 6 caracteres) para no romper clientes existentes. La ruta recomendada es
`/api/v1/links`.

## 8. Pruebas

Desde la raíz:

```powershell
python -m pytest tests -q
```

Con cobertura y análisis estáticos:

```powershell
python -m pytest tests --cov=backend/app --cov-report=term-missing
python -m ruff check backend tests
python -m ruff format --check backend tests
python -m mypy backend/app
```

Resultado de la revisión del 2026-11-05: **115 passed**, cobertura total
**94,88 %** (umbral 85 %), `ruff` limpio y `mypy --strict` sin errores.

Las pruebas usan SQLite aislada, aíslan la dependencia `get_db`, no acceden a la
red pública y verifican contratos, códigos HTTP, reglas de negocio, QR
decodificable, logging JSON, migraciones Alembic, flujo del frontend y control
de acceso.

Carpetas:

- `tests/unit`: dominio, configuración, repositorio, limitador y logging.
- `tests/integration`: QR, administración, métricas, migraciones, frontend y
  persistencia tras reinicio.
- `tests/contract`: envelope, estados HTTP y OpenAPI.
- `tests/security`: autenticación administrativa y ausencia de columnas PII.

## 9. Docker

```powershell
docker compose up --build
```

- Backend: <http://localhost:8000/docs>
- Frontend: <http://localhost:5500>
- Datos: volumen `unishort-data`, base SQLite en `/data/unishort.db`.

El frontend Docker usa `docker/nginx.conf` para omitir registros que incluyan
IP o consultas. El servidor de desarrollo recomendado es
`scripts/serve_frontend.py`, que también omite esos registros.

Para habilitar administración en el contenedor:

```powershell
$env:UNISHORT_ADMIN_API_KEY = "dev-admin-cambiar-en-produccion"
docker compose up --build
```

No se incluyen secretos reales. La configuración de producción (HTTPS,
PostgreSQL, proxy) queda documentada pero fuera de este incremento.

> En la revisión actual Docker no está instalado ni disponible en PATH: no se
> ejecutaron `docker compose config`, build ni arranque. La validación anterior
> de `compose config` es histórica. Se revisaron estáticamente los dos servicios,
> los healthchecks y el volumen. La imagen instala el lock y ejecuta Alembic
> antes de Uvicorn; todavía debe probarse en un equipo con Docker.

## 10. Documentación

- Constitución y especificaciones: `.specify/memory/constitution.md`, `specs/`.
- Contratos: `specs/001-create-short-link/contracts/`, `specs/002-generate-qr/contracts/`.
- ADR: `docs/adr/`.
- BPMN: `docs/procesos/`.
- C4: `docs/arquitectura/`.
- Portal Quarto: `quarto/` (`python scripts/render_portal.py` desde raíz). Quarto no estaba instalado en el
  entorno usado, por lo que el render no se ejecutó aquí.
- Trazabilidad de la evaluación: `docs/evaluacion/trazabilidad-evaluacion.md`.

## 11. Limitaciones conocidas

- La autenticación administrativa es provisional (clave compartida por
  variable de entorno); no existe integración institucional aprobada.
- SQLite es el motor implementado; PostgreSQL queda como decisión de producción.
- No se implementaron roles múltiples ni panel administrativo web.
- La guía oficial de la Evaluación Sumativa 1 no está incorporada al
  repositorio; los requisitos usados provienen del enunciado de la actividad y
  quedan registrados como fuente externa pendiente.
- Docker y Quarto no están disponibles en este entorno. El arranque de
  contenedores y el render del portal siguen pendientes.
- La automatización visual de Edge agotó el tiempo de autorización de la
  herramienta. Sigue pendiente la prueba del navegador con una persona no
  técnica (US4/SC-007), incluida la descarga física del archivo.
- Se midió p95 HTTP local; no acredita latencia visual ni carga concurrente.
- `/shorten` conserva su formato heredado, éxito 200 y deduplicación. Comparte
  ahora el límite de tasa de v1 y rechaza credenciales embebidas; los clientes
  deben contemplar 429. Para nuevas integraciones use `/api/v1/links`.

## 12. Comprobaciones reproducibles y demostración

```powershell
python scripts/verify_database_copy.py
python scripts/verify_runtime.py
```

El primer comando lee `unishort.db` en modo solo lectura, migra una copia
temporal hasta `0003`, compara todas las filas y comprueba el hash del original.
El segundo arranca API y frontend en 8000/5500 con una base temporal, verifica
creación, QR decodificado, CORS, errores, administración, métricas, caducidad,
desactivación y persistencia tras reinicio. Ambos puertos deben estar libres.
Con `--serve`, mantiene el entorno temporal hasta Ctrl+C para probar la interfaz.
El límite de tasa se desactiva solo en ese subproceso para la medición de 100
peticiones por operación. Las pruebas normales sí verifican el límite.

Medición del 2026-11-05: p95 HTTP por loopback **7,71 ms** creación y **6,31 ms**
redirección; 100 muestras por operación, concurrencia 1, SQLite temporal.
No es una medición de SC-004 en el navegador ni de capacidad en producción.

El JavaScript real también tiene una comprobación con DOM y red simulados:
`node scripts/verify_frontend.mjs` (Node 22+ opcional; también se ejecuta en CI).
El workflow `.github/workflows/quality.yml` está preparado; su ejecución remota
no se ha verificado porque no se hizo push.

La guía de demostración y los resultados detallados están en
[`docs/evaluacion/verificacion-2026-11-05.md`](docs/evaluacion/verificacion-2026-11-05.md).
La base local y diez `.pyc` se retiraron **solo del índice** con
`git rm --cached`; siguen en disco y en el historial. `.gitignore` evita
añadirlos de nuevo. Estas retiradas están preparadas para revisión, sin commit.
