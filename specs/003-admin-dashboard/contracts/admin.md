# Contrato aditivo /api/v1

Todas las rutas administrativas exigen X-Admin-API-Key; sin clave 401,
incorrecta 403, sin configuración del servidor 503. Envelope existente
success/message/data/errors/meta y Cache-Control: no-store (incluye errores).

## GET /admin/stats

200 data: { total_links: int, active_links: int, inactive_links: int,
expired_links: int, total_visits: int }. Vacío: cinco ceros.
inactive = is_active false; expired = is_active true y expires_at <= ahora UTC;
active = is_active true y fecha nula o futura. Suma de estados = total_links.
Visitas de todos los registros, independientemente del estado. Sin filtros.
Seguridad OpenAPI: APIKeyHeader.

## GET /links

Conserva limit (50, 1..200), offset (0, >=0), items/total/limit/offset.
Añade q opcional (1..2048, coincidencia literal sin distinguir caja ASCII por
código o URL) y status opcional (active|inactive|expired). Filtros combinados AND.
total cuenta coincidencias antes de paginar. Orden created_at DESC, id DESC.
422 envelope si valores inválidos; 500 controlado si persistencia falla.

## Operaciones reutilizadas

PATCH /links/{code}: is_active y/o expires_at; fecha futura ISO o null para quitar.
No se cambia el destino. Un vencido reactivado sigue vencido hasta cambiar fecha.
GET /links/{code}/qr: público, PNG para utilizables, 410 si inactivo/caducado;
no cuenta visitas. El panel nunca envía la clave para descargar QR.
GET /s/{code}: público, 307 cuenta visita; abrir desde el panel sí cuenta visita.
