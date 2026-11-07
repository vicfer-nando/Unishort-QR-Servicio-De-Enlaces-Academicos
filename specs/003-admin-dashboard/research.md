# Decisiones verificadas en el repositorio

- GET /links ya pagina; se agregan filtros conservando su respuesta.
- PATCH ya habilita/deshabilita y edita/quita caducidad. No necesita otra ruta.
- GET /links/{code}/qr rechaza inactivos y caducados; se conserva este contrato.
- Una fecha pasada devuelve 422 InvalidExpirationError. Reactivar no limpia fecha.
- link_to_data prioriza inactivo sobre caducado. Se aplica lo mismo en SQL.
- No hay sistema institucional de usuarios; se mantiene ADR 0004 provisional.
- Node está disponible; node:test permite probar JavaScript sin dependencias.
- Los módulos .mjs requieren MIME JavaScript: se explicita en Nginx.
- El navegador automatizado no estuvo disponible: host de acceso no disponible.
  No se afirma prueba visual manual ni cumplimiento WCAG auditado.
