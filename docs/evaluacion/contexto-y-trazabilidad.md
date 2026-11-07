# Contexto, alcance y trazabilidad del incremento

## Problema y contexto

UniShort QR busca facilitar compartir recursos académicos mediante enlaces breves
y códigos QR. Se presenta en el contexto académico de la Universidad Nacional de
Loja, sin atribuir patrocinio, aprobación ni integración con sus sistemas. La
solicitud fija la entrega para el 2026-11-06. Se cotejaron las 11 páginas del PDF
oficial incorporado; la matriz final relaciona sus cinco criterios con evidencia.

## Actores y necesidades

| Actor | Necesidad | Superficie real |
|---|---|---|
| Usuario académico | Crear y compartir enlace/QR | index.html, POST /api/v1/links, GET QR |
| Visitante | Abrir recurso a través de enlace/QR | GET /s/{code} |
| Administrador técnico | Buscar, consultar visitas, cambiar estado/fecha | admin.html, listado/resumen/PATCH protegidos |
| Docente | Inspeccionar especificaciones, modelos, contratos y evidencia | Quarto, specs, OpenAPI, tests |

## Alcance y restricciones

Persistencia SQLite con Alembic, FastAPI/Pydantic/SQLAlchemy, frontend estático,
QR local y métricas agregadas. Sin usuarios/roles institucionales, eliminación
física, redirección proxy, eventos de clic individuales ni servicios externos.
HTTPS se exige en despliegues remotos; en esta entrega se verifica loopback.
No hay garantía de rendimiento concurrente ni certificación WCAG/producción.

## Requisito → HTTP → capas → datos → prueba

| Requisito | Petición y validación | Negocio/persistencia | Respuesta y prueba |
|---|---|---|---|
| 001 FR-001/002/003/005 | POST /api/v1/links; CreateLinkRequest + validación de URL | create_short_link → dominio → repository.create_link, índice único | 201 envelope; test_v1_links_contract.py y test_repository.py |
| 001 FR-004/007 | Crear y reiniciar; transacción SQL | commit/rollback; SQLite temporal y Alembic | Persistencia/errores; test_persistence_restart.py, test_migrations.py |
| 001 FR-006/009 | URL inválida o límite excedido | errores de dominio y ventana efímera | 400/422/429, sin fila; contrato/rate_limit |
| 001 FR-008 | Creación/redirección | Sin metadatos de visitantes; logs redactados | tests/security/test_admin_access.py y test_logging_config.py |
| 002 FR-001..008 | GET /links/{code}/qr; estado utilizable | resolve_link_for_redirect + generate_qr_png | PNG decodificado; test_qr.py, sin visita |
| Redirección | GET /s/{code}; existencia/estado | ensure_link_usable + record_click | 307 Location o 404/410; contrato v1 y regresión heredada |
| 003 US1/FR1..3 | GET listado con X-Admin-API-Key | require_admin; compare_digest | 200/401/403/503 y no-store; pruebas security/JS |
| 003 US2/FR5 | GET listado q/status/limit/offset y GET /admin/stats | filtros parametrizados, COUNT/SUM/CASE | Página/total y cinco totales; test_admin_dashboard.py, test_admin_queries.py |
| 003 US3 | PATCH con confirmación, fecha futura/null | update_link_state, normalize_expiration, commit | Enlace actualizado; integración admin y admin.test.mjs |
| 003 US4 | Panel y navegación pública | DOM seguro, i18n, dialog, estado/errores | 19 pruebas JS; visual/teclado y persona no técnica pendientes |

Las rutas de pruebas son relativas a tests/ (contract, unit, integration y security).
El catálogo vigente está en specs/features.md. La correspondencia detallada y sus
límites figuran en la matriz de auditoría final; no se sustituye una aceptación
manual por una prueba simulada.

## Riesgos y mitigación

Clave compartida: restringir entorno, no persistir en navegador y rotar en servidor.
URLs potencialmente sensibles: no registrarlas y usar enlaces académicos de prueba.
Abuso de creación: límite efímero; despliegue público requiere controles perimetrales.
SQLite/búsqueda substring: suficientes para el incremento, sin probar escala masiva.
Dependencias/render/CI: locks y comandos; faltan instalación limpia y ejecuciones
externas cuando no están disponibles. Cambios sin commit: revisión y autorización
del propietario antes de incorporarlos a Git; no se altera el historial.
