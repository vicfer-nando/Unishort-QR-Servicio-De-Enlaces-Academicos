# Tareas verificables de QR

Fecha: 2026-11-05. Reconciliación del incremento existente, no reconstrucción.

- [x] Q001 Especificación y contrato del endpoint PNG, 404/410.
- [x] Q002 Generación local con borde configurable ≥4.
- [x] Q003 Decodificación real del PNG y comprobación de URL corta.
- [x] Q004 HTTP real con FastAPI y SQLite temporal.
- [x] Q005 Corregir descarga entre puertos con Blob y probar JavaScript real.
- [ ] Q006 Abrir interfaz, descargar físicamente y escanear desde un navegador.
- [ ] Q007 Registrar sesión de una persona no técnica y su duración.

Evidencia: `tests/integration/test_qr.py`, `scripts/verify_frontend.mjs`,
`scripts/verify_runtime.py` e informe `docs/evaluacion/verificacion-2026-11-05.md`.
Q006 quedó bloqueada por timeout de autorización de la herramienta de navegador;
no se presenta la simulación DOM como sustituto de esa aceptación visual.
