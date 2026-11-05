# Contract: endpoints heredados `POST /shorten` y `GET /s/{short_code}`

**Contract version**: 1.3.0 | **API version**: 1.0.0 | **Fecha**: 2026-11-05 | **Estado**: implementado y conservado

Estos endpoints se mantienen por compatibilidad con el MVP, el frontend
anterior y los enlaces ya publicados. La superficie recomendada para clientes
nuevos es [`v1-links.md`](v1-links.md). Los errores de la API v1 se documentan
en [`errors.md`](errors.md).

## `POST /shorten` - Crear enlace (heredado)

```http
POST /shorten
Content-Type: application/json

{"url": "https://www.example.com/articulo?lang=es"}
```

- `url` es obligatorio y se valida con `pydantic.HttpUrl`.
- Solo se aceptan esquemas `http` y `https`.
- Los campos adicionales se ignoran.
- No requiere autenticación. Comparte el límite de creación de v1 (429 con
  envelope y `Retry-After`); cambiar de ruta no reinicia el contador.
- Rechaza credenciales embebidas con `422` y detalle de validación heredado.
- No acepta fecha de expiración.
- Usa el mismo almacén que v1, pero conserva deduplicación y código de 6.

### Respuesta de éxito

**Estado:** `200 OK` (no `201`).

```json
{
  "short_code": "dfgBoG",
  "short_url": "http://localhost:8000/s/dfgBoG",
  "original_url": "https://www.example.com/articulo?lang=es"
}
```

| Campo | Tipo | Descripción |
|-------|------|-------------|
| `short_code` | string | Código de 6 caracteres alfanuméricos (`random.choice`). |
| `short_url` | string | Construida con la cabecera `Host` y la ruta `/s/{short_code}`. |
| `original_url` | string | URL normalizada por Pydantic. |

### Deduplicación

Si ya existe un enlace con la misma `original_url`, se devuelve el mismo
`short_code` y `short_url`. No se crean filas nuevas.

> Un enlace deduplicado puede estar inactivo o caducado; en ese caso la
> redirección responderá `410` aunque `POST /shorten` devuelva `200`.

### Errores

- Validación de Pydantic: `422` con `{"detail": [...]}`.
- Esquema no permitido: `422` con `type: "url_scheme"`.
- Fallo al guardar: `500` con `{"detail": "No se pudo guardar el enlace"}`.
- Colisión no resuelta: `500` con `{"detail": "No se pudo generar un codigo unico"}`.

## `GET /s/{short_code}` - Redirección

- Código activo y vigente: `307 Temporary Redirect` con la URL original en
  `Location`, sin cuerpo; incrementa `click_count`.
- Código inexistente: `404 Not Found` con
  `{"detail": "Enlace corto no encontrado"}`.
- Código desactivado: `410 Gone` con envelope `link_inactive`.
- Código caducado: `410 Gone` con envelope `link_expired`.

La redirección no consulta la URL de destino ni registra datos personales.

## Diferencias frente a `/api/v1/links`

| Aspecto | Heredado | v1 |
|---------|----------|----|
| Estado de creación | `200` | `201` |
| Longitud del código | 6 | 7 |
| Deduplicación | Sí | No |
| Envelope | No | Sí |
| Límite de tasa | Sí, compartido con v1 | Sí (60/60 s) |
| Expiración | No | `expires_at` opcional |
| QR | No | `GET .../qr` |
| Administración | No | Clave `X-Admin-API-Key` |

## Semántica adicional

- Ambos contratos comparten la tabla `short_urls` y la misma relación
  código → URL.
- Las columnas nuevas (`is_active`, `expires_at`, `click_count`) tienen valores
  por defecto compatibles con las filas existentes.
- No se consulta ni se descarga la URL de destino.

## Registro de cambios

| Versión | Fecha | Cambio |
|---------|-------|--------|
| 1.3.0 | 2026-11-05 | Corrección de seguridad: rechazo de credenciales (422) y límite compartido con v1 (429); éxito heredado conservado. |
| 1.2.0 | 2026-11-05 | Documentados `410` para enlaces inactivos/caducados y la convivencia con `/api/v1`; añadida tabla comparativa. |
| 1.1.0 | 2026-10-26 | Documentado el comportamiento realmente implementado: 200, 6 caracteres, deduplicación, `/s/{code}` y errores por defecto de Pydantic. |
| 1.0.0 | 2026-10-21 | Contrato inicial de diseño. |
