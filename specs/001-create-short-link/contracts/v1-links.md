# Contract: API versionada `/api/v1/links`

**Contract version**: 1.0.0 | **API version**: 1.0.0 | **Fecha**: 2026-11-05 | **Estado**: implementado

Contrato de la superficie recomendada para clientes nuevos. Los endpoints
heredados `/shorten` y `/s/{short_code}` se conservan y se documentan en
[`shorten.md`](shorten.md).

## Convenciones comunes

### Envelope

Todas las respuestas JSON de `/api/v1` usan la misma envolvente:

```json
{
  "success": true,
  "message": "Enlace corto creado correctamente.",
  "data": {},
  "errors": [],
  "meta": {
    "request_id": "5f0c...",
    "api_version": "1.0.0",
    "language": "es"
  }
}
```

- `message` está localizado en español (`es`) o inglés (`en`).
- `errors` es un arreglo de objetos `{code, message, field}`.
- `field` es `null` cuando el error no corresponde a un campo.
- `data` es `null` en los errores.

### Cabeceras

| Cabecera | Uso |
|----------|-----|
| `X-Request-Id` | Opcional al enviar; se conserva (máximo 128 caracteres) o se genera. Se devuelve en la respuesta. |
| `X-Log-Request-Id` | Generado por el servidor y devuelto en la respuesta; identifica los logs sin registrar la cabecera arbitraria del cliente. |
| `Accept-Language` | `es` (por defecto) o `en`. |
| `X-Admin-API-Key` | Obligatoria en operaciones administrativas. |

### Representación de un enlace (`LinkData`)

| Campo | Tipo | Descripción |
|-------|------|-------------|
| `short_code` | string | Código único de 7 caracteres del alfabeto `abcdefghijkmnpqrstuvwxyz23456789`. |
| `short_url` | string | `{UNISHORT_BASE_URL}/s/{short_code}`. |
| `original_url` | string | URL de destino validada y almacenada. |
| `qr_url` | string | `{UNISHORT_BASE_URL}/api/v1/links/{short_code}/qr`. |
| `created_at` | string \| null | Fecha ISO 8601 en UTC. |
| `expires_at` | string \| null | Fecha ISO 8601 en UTC o `null` si no caduca. |
| `is_active` | boolean | Estado administrativo. |
| `click_count` | integer | Clics agregados; nunca datos por visitante. |
| `status` | string | `active`, `inactive` o `expired`. |

## `POST /api/v1/links` - Crear enlace

**Autenticación:** no requerida.
**Límite:** 60 creaciones por ventana de 60 s por cliente (configurable).

```http
POST /api/v1/links
Content-Type: application/json
Accept-Language: es

{
  "url": "https://www.example.com/articulo?lang=es",
  "expires_at": "2026-12-31T23:59:59Z"
}
```

- `url`: obligatoria, 1..2048 caracteres; solo `http`/`https` absolutas, host
  válido, sin credenciales embebidas y sin espacios internos.
- `expires_at`: opcional, ISO 8601; si se envía debe ser futura. Sin zona
  horaria se asume UTC.
- Campos adicionales: `422 invalid_payload` (`extra="forbid"`).
- Cada envío crea un enlace nuevo; **no hay deduplicación**.

**Respuesta `201 Created`:** envelope con `LinkData`.

| Caso | Estado | `code` |
|------|--------|--------|
| URL válida | `201` | - |
| Cuerpo inválido o campo extra | `422` | `invalid_payload` |
| URL vacía/solo espacios | `422` | `invalid_payload` |
| URL demasiado larga | `422` | `url_too_long` |
| Expiración pasada | `422` | `invalid_expiration` |
| Esquema no permitido | `400` | `invalid_scheme` |
| Host ausente o puerto inválido | `400` | `invalid_host` |
| Credenciales embebidas | `400` | `embedded_credentials` |
| URL relativa, espacios o control | `400` | `invalid_url` |
| Colisión no resuelta tras 10 intentos | `409` | `collision_unresolved` |
| Límite superado | `429` | `rate_limit_exceeded` + `Retry-After` |
| Fallo de persistencia | `500` | `persistence_failure` |

## `GET /api/v1/links/{short_code}` - Consultar enlace

**Autenticación:** no requerida.

- `200`: envelope con `LinkData`, incluso si el enlace está inactivo o caducado
  (el campo `status` lo indica).
- `404`: `link_not_found`.

## `GET /api/v1/links` - Listar enlaces

**Autenticación:** `X-Admin-API-Key`.

| Parámetro | Tipo | Rango | Defecto |
|-----------|------|-------|---------|
| `limit` | integer | 1..200 | 50 |
| `offset` | integer | ≥ 0 | 0 |

**Respuesta `200`:**

```json
{
  "success": true,
  "message": "Enlaces recuperados correctamente.",
  "data": {
    "items": [],
    "total": 0,
    "limit": 50,
    "offset": 0
  },
  "errors": [],
  "meta": {"request_id": "...", "api_version": "1.0.0", "language": "es"}
}
```

Errores administrativos: `401 admin_authentication_required`, `403
admin_forbidden`, `503 admin_not_configured`.

## `PATCH /api/v1/links/{short_code}` - Actualizar estado o expiración

**Autenticación:** `X-Admin-API-Key`.

```json
{"is_active": false}
```

o

```json
{"expires_at": "2027-01-31T23:59:59Z"}
```

o

```json
{"expires_at": null}
```

- Al menos uno de `is_active` o `expires_at` debe estar presente; un cuerpo
  vacío produce `422 invalid_payload`.
- `expires_at` con valor debe ser futuro.
- `200`: envelope con `LinkData` actualizado.
- `404`: `link_not_found`.
- Errores administrativos: `401`, `403`, `503`.

## `DELETE /api/v1/links/{short_code}` - Desactivar enlace

**Autenticación:** `X-Admin-API-Key`.

- Desactivación lógica: no borra la fila ni rompe la relación código → URL.
- `200`: envelope con `LinkData` y `is_active: false`.
- `404`: `link_not_found`.

## `GET /api/v1/links/{short_code}/stats` - Métricas agregadas

**Autenticación:** `X-Admin-API-Key`.

- `200`: envelope con `LinkData`; el campo relevante es `click_count`.
- No expone IP, User-Agent, cookies ni eventos individuales.
- `404`: `link_not_found`.

## `GET /api/v1/links/{short_code}/qr` - Código QR

Ver [`../../002-generate-qr/contracts/qr.md`](../../002-generate-qr/contracts/qr.md).

- `200`: `image/png` con la URL corta codificada.
- `404`, `410`: envelope, sin imagen.
- No incrementa `click_count`.

## Redirección

La redirección compartida sigue en `GET /s/{short_code}`:

- Enlace activo y vigente: `307` con `Location` a la URL original, sin cuerpo
  JSON; incrementa `click_count`.
- Código inexistente: `404` con formato heredado.
- Enlace inactivo: `410 link_inactive` (envelope).
- Enlace caducado: `410 link_expired` (envelope).

## OpenAPI

FastAPI genera el esquema en `/openapi.json` y la documentación interactiva en
`/docs`. El contrato implementado se verifica en
`tests/contract/test_v1_links_contract.py`.

Los errores `422` se describen mediante `ErrorEnvelope`, igual que su cuerpo
real. Swagger ofrece autorización `APIKeyHeader` para `X-Admin-API-Key`.
Las rutas desconocidas y métodos no permitidos bajo `/api/v1` usan envelope
`http_error`; el `405` conserva `Allow`. Los errores internos conservan CORS,
`X-Request-Id` y `X-Log-Request-Id`, sin detalles internos.

## Registro de cambios

| Versión | Fecha | Cambio |
|---------|-------|--------|
| 1.0.0 | 2026-11-05 | Contrato inicial de la API versionada: creación, consulta, listado, actualización, desactivación, métricas y QR. |
| 1.0.1 | 2026-11-05 | Correcciones de errores 404/405/422/500, cabecera adicional de logs y documentación de seguridad OpenAPI; API sigue en 1.0.0. |
