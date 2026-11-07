# Seguridad del incremento y riesgos residuales

Revisión local: 2026-11-06. Corresponde al PDF oficial, pp. 4–5/7. Es un análisis
de amenazas y controles del software actual, no una certificación OWASP ni pentest.

## Activos, actores y límites de confianza

Activos: enlaces persistidos, disponibilidad de redirección, integridad del estado,
clave administrativa y contadores. Visitantes y creadores son anónimos; una clave
compartida concede administración global. No existen propietarios por enlace ni
roles individuales, por lo que no se inventan permisos por objeto inexistentes.
Límites: navegador ↔ API; cabeceras/cuerpo/consultas ↔ validación; servicios ↔ SQL;
entorno del proceso ↔ configuración. El servidor no consulta destinos externos.
El GET público de metadatos de un código conserva destino, estado y contador según
LinkData; proteger el endpoint /stats no convierte esos metadatos en confidenciales.
No se recomienda publicar enlaces a recursos cuyo destino o conteo deba ser privado.

| Riesgo / referencia OWASP conceptual | Control real | Evidencia | Límite residual |
|---|---|---|---|
| Acceso administrativo indebido (control de acceso) | require_admin en listado, resumen, PATCH, DELETE y estadísticas; compare_digest | tests/security, test_admin_dashboard_contract | Clave compartida sin identidad individual; no hay auditoría por persona. |
| Clave persistida o filtrada (autenticación/configuración) | Solo cierre léxico; campo vacío; no Web Storage/cookies; no-store; cancelación/epoch al salir | 19 pruebas JS, seguridad admin | Memoria puede inspeccionarse por scripts comprometidos o herramientas del navegador. |
| Representación accidental de configuración | admin_api_key usa repr=False; logs redactan campos sensibles | test_settings_representation_never_exposes_admin_key; test_logging_config | No registrar model_dump/configuración completa. No se afirma que el campo deje de existir internamente. |
| XSS / URL peligrosa (inyección) | textContent/createElement, esquema HTTP/HTTPS, CSP del panel, sin terceros | admin.test.mjs; domain tests | Frontend público histórico carece de la CSP estricta del panel; verificar visualmente. |
| Inyección SQL | SQLAlchemy con parámetros, filtros literales escapados, conteos SQL | test_admin_queries; búsquedas con %/_ y texto SQL | Substring puede hacer escaneo; escala masiva no verificada. |
| SSRF / credenciales en destino | Sin resolver/descargar destino; rechazo user:password@host | dominio, test_qr y pruebas de credenciales | Acortador público puede enlazar sitios maliciosos; no hay clasificación de reputación. |
| Entrada inválida / fuga de errores | Pydantic, extra forbid en v1, errores de dominio y 500 controlado | contratos y regresiones | Legacy conserva algunos formatos detail/JSON plano; ADR 0005 los documenta. |
| Abuso / denegación de servicio | Límite de creación compartido por v1 y legacy, TTL <=60 s; paginación <=200 | test_rate_limit, seguridad legacy | Limitador por proceso; no limita intentos de clave ni sustituye proxy o protección distribuida. |
| Pérdida de registros | Índice único, commit/rollback, Alembic aditivo y downgrade protegido | test_repository, migraciones/reinicio; copia real | Copias de seguridad y concurrencia de producción no acreditadas. |
| Datos sensibles en observabilidad | JSON estructurado, ruta de plantilla, ID interno, sin access-log de IP; solo tipo de excepción | test_logging_config y regresiones | No recopilar metadatos no garantiza que la URL original ingresada carezca de PII. |
| Host no confiable en API heredada | v1 usa BASE_URL validada; frontend nuevo consume v1 | configuración + flujo v1 | /shorten conserva URL derivada de Host y http por compatibilidad. Restringir Host en proxy y no recomendar legacy en remoto. |

## Decisiones y operación

- Usar HTTPS fuera de loopback y orígenes explícitos en CORS. No se cambiaron los
  permisos CORS para facilitar pruebas. El * predeterminado histórico no es una
  configuración recomendada para publicación; Compose especifica los dos orígenes locales.
- Leer clave mediante Read-Host -AsSecureString, pasarla por entorno, no por URL,
  argumentos de proceso, fuentes o mensajes. No guardar capturas de cabeceras.
- Cerrar sesión borra la clave local; no la revoca en otros clientes. Rotar en
  entorno y reiniciar Uvicorn para invalidar la clave compartida.
- Docker usa usuario sin privilegios y volumen separado. No se ha ejecutado su
  build aquí; no equivale a demostrar endurecimiento de producción.
- No se añade identidad institucional para esta entrega. ADR 0004 delimita el
  mecanismo provisional y su sustitución futura.

No se descubrieron secretos reales durante la revisión de las fuentes operativas
consultadas; no se afirma un escaneo forense completo de todo el historial Git.
No se imprimieron valores de claves reales ni se modificaron bases existentes.
