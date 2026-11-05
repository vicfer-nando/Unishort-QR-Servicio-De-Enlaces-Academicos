# Verificación del incremento — 5 de noviembre de 2026

## Diagnóstico

Raíz comprobada: `Unishort-QR-Servicio-De-Enlaces-Academicos`. Rama inicial
`main`, sincronizada con `origin/main`, sin cambios. La línea base reportada
se reprodujo: 96 pruebas, 93,17 % de cobertura y Ruff/mypy limpios. El primer
intento de pytest encontró permisos del directorio temporal de Windows; al
ejecutar con acceso autorizado al temporal pasó la suite completa.

Se encontraron errores reales de IPv6 malformado, autenticación no ASCII,
envelope de 404/405, OpenAPI 422, CORS y trazabilidad en 500, retención de IP
durante inactividad, logs con ruta y cabeceras arbitrarias, diferencias de
índices ORM/Alembic y descarga QR entre puertos. Se reprodujeron mediante
regresiones fallidas antes de corregir. La ruta heredada también permitía
credenciales embebidas y eludir el límite de creación: ahora rechaza ambas
situaciones conservando éxito 200, deduplicación y formato heredado.

## Correcciones y evidencias

| Área | Corrección | Evidencia |
|------|------------|-----------|
| Entrada | IPv6 inválido produce 400 sin insertar; URL pública inválida falla al configurar | `test_regressions.py`, `test_deployment_config.py` |
| Errores | 404/405 v1 con envelope, `Allow` preservado; 500 sin detalles, con CORS y request ID | `test_regressions.py` |
| Administración | Comparación de bytes UTF-8; cabecera incorrecta no ASCII produce 403 | `test_regressions.py` |
| OpenAPI | `ErrorEnvelope` real y esquema de seguridad `APIKeyHeader` | `test_regressions.py` |
| Privacidad | Rutas de plantilla, ID interno, sin texto de excepciones SQL; redacción de IP, email y Bearer | `test_logging_config.py`, `test_regressions.py` |
| TTL | Eliminación aun sin tráfico, temporizadores antiguos no borran reemplazos | `test_rate_limit.py` |
| Heredado | Credenciales rechazadas y contador de tasa compartido con v1 | `test_admin_access.py` |
| Índices | ORM incluye fechas/estado; `0003` agrega índice de estado sin tocar filas; metadata cargada en Alembic | `test_migrations.py` compara esquema nuevo con ORM |
| Aislamiento | La colección pytest fuerza una base temporal propia y cierra SQLite antes de limpiar | `tests/conftest.py` |
| QR | Descarga fetch → Blob local → archivo; no navegación accidental entre puertos | `scripts/verify_frontend.mjs` |
| Contenedor | Lock, Alembic antes de Uvicorn, CORS, healthcheck y Nginx sin logs de acceso/error con PII | Revisión estática; ejecución pendiente |
| CI | Suite/cobertura, Ruff, mypy y JavaScript | `.github/workflows/quality.yml`; ejecución remota pendiente |

## Calidad comprobada

- Pytest con cobertura: **115 pruebas aprobadas, 94,88 %** (umbral 85 %).
- Ruff check y format check: backend, tests, Alembic y scripts.
- mypy strict: backend, 20 archivos.
- Logging y limitador: 100 % de cobertura.
- JavaScript real ejecutado con DOM/red simulados: validación, creación,
  representación QR, descarga Blob, error HTTP y fallo de red.

El Python disponible es 3.13.14. `pip check` detectó un conflicto del entorno
global con Streamlit (ajeno a este proyecto). No se cambió ese entorno; para
la entrega debe usarse un venv. No se certifica reinstalación limpia de los
locks ni ejecución de CI remota.

## Sistema real por TCP

`python scripts/verify_runtime.py --serve` arrancó Uvicorn y un servidor estático
en loopback, sobre SQLite temporal migrada hasta `0003`. Verificó frontend
200, `/health`, `/docs`, `/openapi.json`, creación 201, CORS, QR decodificado,
redirección 307 sin seguir destinos de Internet, contador 0 al obtener QR y 1
al redirigir, administración 401/403/200, URLs inválidas, inexistencia 404,
desactivación 410, caducidad 410, reactivación y persistencia tras reiniciar.

Medición local: 100 solicitudes secuenciales por operación, concurrencia 1,
SQLite temporal, sin límite de tasa solo en ese subproceso. Percentil 95 por
vecino más próximo (muestra ordenada 95): **7,71 ms** creación y **6,31 ms**
redirección. Incluye HTTP loopback y escritura SQLite. No mide el tiempo de
pintado del navegador, carga concurrente ni el escenario de un millón de filas.
SC-004 visual sigue pendiente; no se presenta esta medición como equivalente.

## Protección de la base existente y Git

`python scripts/verify_database_copy.py` abrió el original en solo lectura,
creó una copia por SQLite backup, migró la copia hasta `0003`, comparó todas
las columnas preexistentes de sus **9 filas** y ejecutó `PRAGMA integrity_check`.
Resultado: filas idénticas e integridad OK. Hash original antes/después:

```text
5df7ad7c0231cd8f042fe0843132ba9fa6c084b1ef7b38e5925ccacf36768585
```

Diez `.pyc` y `unishort.db` se retiraron únicamente del índice mediante
`git rm --cached`, verificando existencia y hashes de los once archivos en
disco. Permanecen en disco y en el historial. `.gitignore` ignora las bases
locales y cachés. No se hicieron commits, pushes ni reescrituras de historial.

## Límites y aceptación pendiente

- Docker y Quarto no están en PATH ni en sus rutas habituales. No se ejecutaron
  build, compose ni render; la validación histórica de compose no acredita el
  Dockerfile modificado. Pendiente: `docker compose config`,
  `docker compose up --build` y persistencia al recrear contenedores.
- El inventario de la herramienta no encontró acceso de navegador; la apertura
  de Edge mediante control nativo agotó su autorización. No se verificaron
  visualmente formulario, descarga física, copiar/abrir ni Swagger interactivo.
  HTTP y DOM simulado son evidencias distintas. Falta US4/SC-007 con persona
  no técnica y duración registrada.
- BPMN: comprobar XML y referencias no equivale a validación BPMN/XSD ni render.
  C1–C4 se revisaron contra el código; no hay renderer Structurizr/PlantUML.
- La guía oficial de evaluación sigue ausente; no se inventó su contenido.
- Spec Kit tiene materiales históricos contradictorios: se señalan como diseño
  inicial y se enlaza esta evidencia. No se ejecutaron slash commands ni se
  certificó aprobación formal del equipo. La constitución conserva pendientes
  de ratificación, producción, revisión humana y accesibilidad/i18n completa.
- Identidad institucional, roles, panel administrativo, PostgreSQL y HTTPS de
  producción siguen fuera del incremento. La clave compartida es provisional.
- El limitador es por proceso, con un temporizador por cliente activo. Para
  tráfico institucional hay que evaluar proxy y escalado; no se acreditó carga.

## Arranque seguro para la demostración

Desde raíz, terminal 1 (base demo separada del original):

```powershell
py -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements-dev.lock
$env:UNISHORT_DATABASE_URL = "sqlite:///./demo-unishort.db"
$env:UNISHORT_BASE_URL = "http://localhost:8000"
$env:UNISHORT_ADMIN_API_KEY = [guid]::NewGuid().ToString("N")
Write-Host "Clave temporal de demo: $env:UNISHORT_ADMIN_API_KEY"
$env:UNISHORT_CORS_ORIGINS = "http://localhost:5500,http://127.0.0.1:5500"
.\.venv\Scripts\python.exe -m alembic upgrade head
.\.venv\Scripts\python.exe -m uvicorn backend.app.main:app --host 127.0.0.1 --port 8000 --no-access-log
```

Terminal 2, desde raíz:

```powershell
.\.venv\Scripts\python.exe scripts/serve_frontend.py
```

1. Abrir `http://localhost:5500`; crear un enlace a
   `http://localhost:5500/?demo=docente`, obteniendo un código nuevo de 7 símbolos.
2. Mostrar y descargar el PNG. Su contenido debe ser la URL corta. Para un
   teléfono, configurar antes una IP LAN accesible; localhost en él es el teléfono.
3. Abrir el enlace corto y verificar la página de destino. El PNG no suma clics.
4. Abrir `/health` y `/docs`; usar Authorize con la clave generada en la primera
   terminal (se muestra antes de arrancar Uvicorn). No guardar esa clave en el repositorio.
5. Consultar `/api/v1/links/{code}/stats`: un clic después de una apertura.
6. Probar administración sin clave/incorrecta y observar 401/403. Con clave,
   listar, PATCH `{"is_active":false}` y observar 410 al abrir o pedir QR.
7. Reactivar con PATCH `{"is_active":true}`, configurar `expires_at` unos segundos
   en el futuro, esperar y comprobar 410; limpiar con `{"expires_at":null}`.
8. Probar URL inválida (400/422) y `/s/noexiste` (404). Mostrar en Swagger el
   envelope de errores y `X-Log-Request-Id`, sin trazas ni datos de visitantes.
9. Reiniciar backend y comprobar que el enlace y contador persisten en la base
   demo. Registrar duración y resultado de la persona evaluadora.

La clave solo se muestra en la terminal local de demostración; no se guarda
en archivos ni en logs del backend. No se implementó panel admin.

La prueba por TCP finalizó con código 0 tras corregir el cierre explícito
de la conexión SQLite del script en Windows. El servidor local recomendado
es `scripts/serve_frontend.py`, sin registros de acceso con IP. La preparación
de fuentes Quarto y el control estático de 43 documentos pasaron; el intento
de render se detuvo con el mensaje de que Quarto no está disponible.

## Archivos de esta continuacion

Rutas relativas al repositorio; las retiradas de cache y base son solo del indice.

- `.env.example`
- `.github/workflows/quality.yml`
- `.gitignore`
- `CHANGELOG.md`
- `Dockerfile`
- `README.md`
- `alembic/env.py`
- `alembic/versions/0001_initial_schema.py`
- `alembic/versions/0002_add_created_at_index.py`
- `alembic/versions/0003_align_active_index.py`
- `backend/app/__pycache__/__init__.cpython-313.pyc`
- `backend/app/__pycache__/database.cpython-313.pyc`
- `backend/app/__pycache__/main.cpython-313.pyc`
- `backend/app/__pycache__/models.cpython-313.pyc`
- `backend/app/__pycache__/schemas.cpython-313.pyc`
- `backend/app/__pycache__/utils.cpython-313.pyc`
- `backend/app/api/deps.py`
- `backend/app/api/schemas.py`
- `backend/app/api/v1.py`
- `backend/app/config.py`
- `backend/app/database.py`
- `backend/app/domain.py`
- `backend/app/logging_config.py`
- `backend/app/main.py`
- `backend/app/models.py`
- `backend/app/rate_limit.py`
- `backend/app/schemas.py`
- `docker-compose.yml`
- `docker/nginx.conf`
- `docs/adr/0006-qr-local.md`
- `docs/adr/0007-limite-efimero.md`
- `docs/evaluacion/trazabilidad-evaluacion.md`
- `docs/evaluacion/verificacion-2026-11-05.md`
- `frontend/index.html`
- `quarto/_quarto.yml`
- `quarto/api.qmd`
- `quarto/arquitectura.qmd`
- `quarto/entrega.qmd`
- `quarto/index.qmd`
- `quarto/procesos.qmd`
- `quarto/pruebas.qmd`
- `quarto/requisitos.qmd`
- `scripts/render_portal.py`
- `scripts/serve_frontend.py`
- `scripts/verify_database_copy.py`
- `scripts/verify_docs.py`
- `scripts/verify_frontend.mjs`
- `scripts/verify_runtime.py`
- `specs/001-create-short-link/checklists/requirements.md`
- `specs/001-create-short-link/contracts/shorten.md`
- `specs/001-create-short-link/contracts/v1-links.md`
- `specs/001-create-short-link/data-model.md`
- `specs/001-create-short-link/plan.md`
- `specs/001-create-short-link/quickstart.md`
- `specs/001-create-short-link/research.md`
- `specs/001-create-short-link/spec.md`
- `specs/001-create-short-link/tasks.md`
- `specs/001-create-short-link/verification-2026-11-05.md`
- `specs/002-generate-qr/contracts/qr.md`
- `specs/002-generate-qr/data-model.md`
- `specs/002-generate-qr/plan.md`
- `specs/002-generate-qr/quickstart.md`
- `specs/002-generate-qr/research.md`
- `specs/002-generate-qr/spec.md`
- `specs/002-generate-qr/tasks.md`
- `tests/__pycache__/conftest.cpython-313-pytest-8.3.3.pyc`
- `tests/__pycache__/test_basic.cpython-313-pytest-8.3.3.pyc`
- `tests/__pycache__/test_basic.cpython-313-pytest-9.1.1.pyc`
- `tests/__pycache__/test_shorten.cpython-313-pytest-8.3.3.pyc`
- `tests/conftest.py`
- `tests/contract/test_regressions.py`
- `tests/integration/test_migrations.py`
- `tests/security/test_admin_access.py`
- `tests/unit/test_deployment_config.py`
- `tests/unit/test_logging_config.py`
- `tests/unit/test_rate_limit.py`
- `unishort.db`
