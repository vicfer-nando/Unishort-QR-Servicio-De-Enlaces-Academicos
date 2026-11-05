# Contract: errores (implementación actual)

**Contract version**: 1.1.0 | **API version**: 1.0.0 | **Fecha**: 2026-10-26 | **Estado**: implementado

Este documento describe los errores que devuelve el backend real. La envolvente
`{"error": {"code", "message", "field"}}` del diseño objetivo **no está
implementada**; se conserva en [spec.md](../spec.md) como trabajo futuro.

## Errores de validación (`POST /shorten`)

FastAPI/Pydantic devuelve `422 Unprocessable Entity` con un arreglo `detail`:

```json
{
  "detail": [
    {
      "type": "url_scheme",
      "loc": ["body", "url"],
      "msg": "URL scheme should be 'http' or 'https'",
      "input": "javascript:alert(1)",
      "ctx": {"expected_schemes": "'http' or 'https'"}
    }
  ]
}
```

- `detail` es un arreglo; puede contener más de un error.
- `msg` está en inglés porque proviene de Pydantic.
- El frontend convierte los `msg` en texto legible para la persona usuaria.
- No se crea ningún enlace cuando la validación falla.

Tipos observados:

| `type` | Caso |
|--------|------|
| `url_scheme` | Esquema distinto de `http`/`https`. |
| `url_parsing` | URL relativa o malformada. |
| `missing` | Falta el campo `url`. |
| `url_too_long` | La URL supera los 2083 caracteres. |

## Código corto inexistente (`GET /s/{short_code}`)

```json
{"detail": "Enlace corto no encontrado"}
```

Estado: `404 Not Found`.

## Colisión no resuelta

Si no se consigue un código libre tras 10 intentos, el backend lanza una
`HTTPException` con estado `500` y:

```json
{"detail": "No se pudo generar un codigo unico"}
```

## Errores no controlados

Un fallo no capturado (por ejemplo, de SQLAlchemy) puede devolver una respuesta
`500` que no sea JSON. El frontend detecta el `Content-Type` y muestra un mensaje
genérico comprensible en lugar de intentar interpretar el cuerpo como JSON.

## Diferencias con el diseño objetivo

Todavía no están implementados:

- la envolvente `error.code`, `error.message`, `error.field`;
- la localización `es`/`en` mediante `Accept-Language`;
- `X-Request-Id`;
- los códigos `rate_limit_exceeded`, `invalid_host`, `embedded_credentials`,
  `collision_unresolved`, `persistence_failure` e `internal_error`;
- el límite de tasa.

## Registro de cambios

| Versión | Fecha | Cambio |
|---------|-------|--------|
| 1.1.0 | 2026-10-26 | Documentados los errores reales de FastAPI/Pydantic y las diferencias pendientes. |
| 1.0.0 | 2026-10-21 | Envoltura y códigos iniciales de diseño. |
