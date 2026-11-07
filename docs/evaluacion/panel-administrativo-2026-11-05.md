# Informe del incremento 003 — Panel administrativo UniShort QR

Fecha: 2026-11-05, America/Guayaquil. Implementación local solicitada por el
propietario. Sin commit, push, despliegue ni aprobación institucional/equipo atribuida.

## 1. Funcionalidades implementadas

- Pantalla de acceso con campo password. Valida mediante GET /api/v1/links paginado,
  endpoint protegido preexistente; no transmite la clave en URL ni formularios.
- Clave solo en memoria de la página. Logout/pagehide vacían la clave, limpian
  registros y editor, cancelan solicitudes y descartan respuestas tardías.
- Mensajes específicos para 401/403/503; permisos reales en backend en cada operación.
- Cinco indicadores globales con COUNT/SUM/CASE en una consulta SQL, sin materializar
  enlaces. Inactivo tiene prioridad sobre vencido; los estados no se solapan.
- Lista paginada con total filtrado, orden estable, búsqueda literal por código/URL
  y filtros active/inactive/expired; `%` y `_` no actúan como comodines.
- Copiar, abrir, visitas, descarga QR y Gestión con confirmación para habilitar,
  deshabilitar y modificar/quitar caducidad. Sin borrado físico ni cambio de destino.
- Identidad verde, diseño responsivo, tabla desplazable, estados vacíos/carga,
  foco visible, etiquetas y diálogo nativo. Catálogo español/inglés externo.
- DOM seguro con textContent/createElement, esquemas HTTP/HTTPS validados, QR desde
  el backend configurado sin clave, CSP restrictiva y no-store en operaciones admin.
- Generador público y contratos heredados conservados.

## 2. Archivos creados

- Frontend: `frontend/admin.html`, `frontend/admin.css`, `frontend/admin.mjs`,
  `frontend/admin-i18n.mjs`.
- Especificación: `specs/003-admin-dashboard/` con `spec.md`, `plan.md`, `tasks.md`,
  `research.md`, `data-model.md`, `quickstart.md` y `contracts/admin.md`.
- Pruebas: `tests/integration/test_admin_dashboard.py`,
  `tests/contract/test_admin_dashboard_contract.py`,
  `tests/security/test_admin_dashboard_security.py`, `tests/unit/test_admin_queries.py`,
  `tests/js/admin.test.mjs`.
- Portal: `quarto/administracion.qmd`; este informe.

## Archivos modificados

- Backend: `backend/app/api/deps.py`, `api/schemas.py`, `api/v1.py`, `main.py`,
  `services.py`, `repository.py`, `i18n.py` (todos bajo backend/app).
- Frontend público: `frontend/index.html` (navegación al panel).
- Operación: `.github/workflows/quality.yml` (pruebas JS), `docker/nginx.conf`
  (MIME .mjs), `scripts/verify_runtime.py` (recorrido HTTP del panel).
- Documentación: `README.md`, `CHANGELOG.md`,
  `docs/adr/0004-autenticacion-provisional-administrativa.md`,
  `quarto/_quarto.yml`, `quarto/api.qmd`, `quarto/index.qmd`,
  `quarto/requisitos.qmd`, `quarto/pruebas.qmd`, `quarto/entrega.qmd`.

No se modificaron dependencias, migraciones, tecnología ni pruebas anteriores.
No se cambió la constitución. Las excepciones de trabajo local y revisión pendiente
se registraron en el plan; no equivalen a una aprobación del equipo.

## 3. Endpoints

| Operación | Cambio |
|---|---|
| GET /api/v1/admin/stats | Nuevo, protegido; total_links, active_links, inactive_links, expired_links, total_visits. |
| GET /api/v1/links | Ampliación compatible: q 1..2048, status enumerado, limit 1..200, offset >=0. |
| PATCH /api/v1/links/{code} | Reutilizado para estado/caducidad, sin cambios de contrato. |
| GET /api/v1/links/{code}/qr | Reutilizado, PNG público; 410 para inactivos/caducados. |

OpenAPI se genera desde FastAPI y se comprueba en pruebas. Envelope conservado.
Se añade Cache-Control: no-store a respuestas de endpoints protegidos, incluidos errores.

## 4–5. Verificación y cobertura

| Comprobación | Resultado observado |
|---|---|
| pytest completo | 143 aprobadas: las 115 anteriores + 28 nuevas; cero fallidas/errores finales. |
| Cobertura backend | 95,22 % (896/941 sentencias); umbral configurado 85 % intacto. |
| Node panel | 19 pruebas aprobadas; cero fallidas, omitidas o canceladas. |
| Node flujo público | Validación, creación, imagen, Blob QR y errores aprobados. |
| Ruff check | All checks passed. |
| Ruff format --check | 50 archivos ya formateados. |
| mypy estricto | Sin errores en 20 módulos. |
| HTTP real | Frontend/admin, MIME .mjs, resumen, filtros, autorización, QR decodificado, CORS, reinicio y persistencia aprobados. |
| Documentación | Fuentes UTF-8, enlaces, YAML y referencias BPMN comprobados. No equivale a render. |
| Navegador | No ejecutado: host de acceso al navegador no disponible. |
| Docker / render Quarto | Herramientas no disponibles; no ejecutados. |

La suite emite un aviso de deprecación de AnyIO/Starlette. La primera ejecución
tuvo tres errores por permisos de temporales de pytest (112 casos aprobados);
un basetemp nuevo exclusivo resolvió el bloqueo y aprobó la suite completa sin
alterar pruebas anteriores. Los nuevos casos se observaron fallando antes de
implementar resumen/filtros/caché; el primer test JS falló por módulo aún inexistente.

Comandos usados, desde raíz con el entorno virtual:

```powershell
.\.venv\Scripts\python.exe -m pytest tests --cov=backend/app --cov-report=term-missing -p no:cacheprovider --basetemp=.verification/admin-final-01
node --test tests/js/admin.test.mjs
node scripts/verify_frontend.mjs
.\.venv\Scripts\python.exe -m ruff check backend tests alembic scripts --no-cache
.\.venv\Scripts\python.exe -m ruff format --check backend tests alembic scripts --no-cache
.\.venv\Scripts\python.exe -m mypy backend/app --cache-dir=.verification/mypy-admin
.\.venv\Scripts\python.exe scripts/verify_runtime.py
.\.venv\Scripts\python.exe scripts/render_portal.py --prepare-only
.\.venv\Scripts\python.exe scripts/verify_docs.py
```

Para repetir pytest, elegir otro basetemp nuevo exclusivo: pytest elimina el
contenido de ese directorio al arrancar. Nunca pasar una carpeta de trabajo o datos.

Hashes SHA-256 antes y después, iguales:

- unishort.db: `5DF7AD7C0231CD8F042FE0843132BA9FA6C084B1EF7B38E5925CCACF36768585`.
- demo-unishort.db: `1DA10E7949B1F5794E9FEB9699AD36D2FE6545A24ABC90CE444C9078F92B64E3`.

Las pruebas usan SQLite temporal/memoria; las migraciones del recorrido HTTP se
aplican solo a su base temporal. No se modificaron las bases existentes.

## 6–7. Inicio y demostración sin exponer la clave

El [guion exacto](../../specs/003-admin-dashboard/quickstart.md) incluye creación
de base temporal, migración, backend y frontend. La clave se define mediante
Read-Host -AsSecureString y se transmite al proceso mediante entorno, sin literal
en historial ni impresión. Abrir <http://localhost:5500/admin.html> e introducir
la misma clave. No enviarla por chat, capturas, query string ni fuentes estáticas.

Desde el panel se puede volver al acortador. Gestionar abre un diálogo y solo
Confirmar cambios envía PATCH. Vacío quita caducidad; fechas futuras se convierten
a UTC. Reactivar no quita una caducidad vencida. Logout/recarga exige autenticarse
otra vez. Abrir enlace cuenta visita; obtener QR no.

## 8. Limitaciones y riesgos

- Clave compartida provisional, sin identidad individual, roles, MFA ni auditoría
  por persona. Logout local no revoca la clave en otros clientes; rotar/reiniciar.
- HTTPS obligatorio fuera de loopback; servir scripts confiables. La clave en
  memoria sigue expuesta a scripts comprometidos y herramientas del propio navegador.
- SQLite sigue siendo el motor de desarrollo; no se valida carga concurrente.
- Búsqueda por substring puede recorrer registros; se pagina y se cuenta en SQL,
  pero escalar a millones requiere evaluar índices/búsqueda y motor de producción.
- Totales y listado se consultan por separado; cambios concurrentes pueden verse
  en instantes ligeramente distintos. Actualizar vuelve a consultar ambos.
- No se ha realizado auditoría WCAG, comprobación visual de escritorio/móvil ni
  demostración con persona no técnica. El DOM simulado no las sustituye.
- Docker y render Quarto pendientes; CI ampliada sin ejecución remota verificada.
- Revisión/aprobación del equipo pendientes; no se inventan firmas ni evidencias.

## 9. Siguiente incremento recomendado

1. Validar visualmente el panel en escritorio/móvil, teclado y lector de pantalla.
2. Especificar identidad institucional OIDC, roles y auditoría sin datos de visitantes.
3. Probar Docker, render Quarto y CI remoto mediante el proceso normal de revisión.
4. Evaluar PostgreSQL, búsqueda e índices con volumen representativo antes de producción.
