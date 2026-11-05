# Contract: errores de la API

**Contract version**: 2.0.0 | **API version**: 1.0.0 | **Fecha**: 2026-11-05 | **Estado**: implementado

La API versionada usa un envelope común. Los endpoints heredados conservan su
formato anterior salvo los errores de dominio, que también usan envelope.

## Envelope de error (`/api/v1`)

```json
{
  "success": false,
  "message": "Solo se admiten URLs con esquema http o https.",
  "data": null,
  "errors": [
    {
      "code": "invalid_scheme",
      "message": "Solo se admiten URLs con esquema http o https.",
      "field": "url"
    }
  ],
  "meta": {
    "request_id": "5f0c...",
    "api_version": "1.0.0",
    "language": "es"
  }
}
```

- `code` es estable y apto para programas.
- `message` está localizado según `Accept-Language` (`es` por defecto, `en`
  alternativo).
- `field` identifica el campo responsable o es `null`.
- `X-Request-Id` se devuelve siempre; se acepta el valor del cliente si tiene
  hasta 128 caracteres.

## Catálogo de códigos

| `code` | Estado | Origen |
|--------|--------|--------|
| `invalid_payload` | `422` | Cuerpo inválido, campo faltante o campo extra. |
| `url_required` | `422` | URL vacía o solo espacios (mapeada como `invalid_payload` en el envelope). |
| `url_too_long` | `422` | URL de más de 2048 caracteres. |
| `invalid_expiration` | `422` | Expiración pasada o inválida. |
| `invalid_url` | `400` | URL relativa, con espacios internos o caracteres de control. |
| `invalid_scheme` | `400` | Esquema distinto de `http`/`https`. |
| `invalid_host` | `400` | Host ausente, netloc inválido o puerto inválido. |
| `embedded_credentials` | `400` | Usuario o contraseña embebidos. |
| `collision_unresolved` | `409` | Sin código libre tras 10 intentos. |
| `persistence_failure` | `500` | Fallo de base de datos con rollback. |
| `internal_error` | `500` | Excepción no controlada; no expone trazas. |
| `link_not_found` | `404` | Código inexistente. |
| `link_inactive` | `410` | Enlace desactivado. |
| `link_expired` | `410` | Enlace caducado. |
| `rate_limit_exceeded` | `429` | Límite de creación superado. |
| `admin_not_configured` | `503` | Sin clave administrativa configurada. |
| `admin_authentication_required` | `401` | Falta `X-Admin-API-Key`. |
| `admin_forbidden` | `403` | Clave administrativa incorrecta. |
| `service_unavailable` | `503` | Base de datos no disponible en `/health`. |

## Mensajes localizados

Las claves del catálogo viven en `backend/app/i18n.py`. Ejemplos:

| Clave | Español | Inglés |
|-------|---------|--------|
| `invalid_scheme` | Solo se admiten URLs con esquema http o https. | Only http or https URLs are allowed. |
| `invalid_host` | La URL debe ser absoluta y tener un host válido. | The URL must be absolute and have a valid host. |
| `link_inactive` | El enlace está desactivado. | The link is disabled. |
| `rate_limit_exceeded` | Se superó el límite de creación de enlaces. Espera un momento. | The link creation rate limit was exceeded. Please wait. |

## Errores heredados

`POST /shorten` conserva el formato anterior:

```json
{"detail": [{"type": "url_scheme", "loc": ["body", "url"], "msg": "..."}]}
```

`GET /s/{short_code}` con código inexistente conserva:

```json
{"detail": "Enlace corto no encontrado"}
```

Estados: `422` para validación de Pydantic y `404` para código inexistente. Los
errores de dominio (por ejemplo, enlace inactivo o caducado durante la
redirección) sí usan el envelope común, porque el handler de dominio es global.

## Casos verificados

| Entrada / situación | Estado | `code` |
|---------------------|--------|--------|
| `{}` | `422` | `invalid_payload` |
| `{"url": "   "}` | `422` | `invalid_payload` |
| `{"url": "ftp://example.com"}` | `400` | `invalid_scheme` |
| `{"url": "https://"}` | `400` | `invalid_host` |
| `{"url": "https://u:p@example.com"}` | `400` | `embedded_credentials` |
| URL de 3000 caracteres | `422` | `url_too_long` |
| Campo extra | `422` | `invalid_payload` |
| Expiración pasada | `422` | `invalid_expiration` |
| 61.ª creación en la ventana | `429` | `rate_limit_exceeded` |
| Código inexistente en v1 | `404` | `link_not_found` |
| Enlace desactivado en `/s` | `410` | `link_inactive` |
| Enlace caducado en `/s` | `410` | `link_expired` |
| Administración sin cabecera | `401` | `admin_authentication_required` |
| Administración con clave errónea | `403` | `admin_forbidden` |
| Administración sin clave configurada | `503` | `admin_not_configured` |

## Registro de cambios

| Versión | Fecha | Cambio |
|---------|-------|--------|
| 2.0.0 | 2026-11-05 | Implementados el envelope v1, la localización, `X-Request-Id`, los códigos de dominio y la autenticación administrativa; documentada la convivencia con los errores heredados. |
| 1.1.0 | 2026-10-26 | Documentados los errores reales de FastAPI/Pydantic y las diferencias pendientes. |
| 1.0.0 | 2026-10-21 | Envoltura y códigos iniciales de diseño. |
