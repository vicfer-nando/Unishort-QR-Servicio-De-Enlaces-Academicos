# Contract: `POST /shorten` (implementación actual)

**Contract version**: 1.1.0 | **API version**: 1.0.0 | **Fecha**: 2026-10-26 | **Estado**: implementado

Este documento describe el contrato que expone hoy el backend real en
`backend/app/main.py`. El diseño objetivo de la Feature 1 sigue en
[spec.md](../spec.md), [plan.md](../plan.md) y [tasks.md](../tasks.md); algunas de
esas tareas todavía no están implementadas.

## Petición

```http
POST /shorten
Content-Type: application/json

{"url": "https://www.example.com/articulo?lang=es"}
```

- El cuerpo debe ser JSON.
- `url` es obligatorio y se valida con `pydantic.HttpUrl`.
- Solo se aceptan esquemas `http` y `https`.
- No se usan cabeceras especiales como `X-Request-Id` ni `Accept-Language`.
- Los campos adicionales se ignoran (comportamiento por defecto de Pydantic).

## Respuesta de éxito

**Estado real**: `200 OK` (no 201).

```json
{
  "short_code": "dfgBoG",
  "short_url": "http://localhost:8000/s/dfgBoG",
  "original_url": "https://www.example.com/articulo?lang=es"
}
```

| Campo | Tipo | Descripción |
|-------|------|-------------|
| `short_code` | string | Código de 6 caracteres alfanuméricos (`A-Z`, `a-z`, `0-9`). |
| `short_url` | string | URL absoluta construida con el host de la petición y la ruta `/s/{short_code}`. |
| `original_url` | string | URL normalizada por Pydantic. |

## Deduplicación

Si ya existe un enlace con la misma `original_url`, se devuelve el mismo
`short_code` y el mismo `short_url`. No se crean filas duplicadas para la misma
URL.

## Redirección

```http
GET /s/{short_code}
```

- Código existente: `307 Temporary Redirect` con la URL original en `Location`.
- Código inexistente: `404 Not Found` con `{"detail": "Enlace corto no encontrado"}`.

## Errores de validación

Los errores de Pydantic/FastAPI usan el formato por defecto:

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

Casos comprobados:

| Entrada | Estado | `type` de Pydantic |
|---------|--------|--------------------|
| `javascript:alert(1)` | 422 | `url_scheme` |
| `not-a-url` | 422 | `url_parsing` |
| Cuerpo sin `url` | 422 | `missing` |
| URL de más de 2083 caracteres | 422 | `url_too_long` |

No existe todavía la envolvente `{"error": ...}` descrita en el diseño objetivo.
El frontend transforma `detail` en un mensaje legible.

## Semántica adicional

- La base de datos es SQLite (`unishort.db`) y la tabla se crea automáticamente
  al arrancar la aplicación.
- La generación de códigos usa `random.choice` sobre letras y dígitos y reintenta
  hasta 10 veces si encuentra una colisión.
- No hay rate limiting, autenticación ni generación de códigos QR.
- No se consulta ni se descarga la URL de destino.

## Registro de cambios

| Versión | Fecha | Cambio |
|---------|-------|--------|
| 1.1.0 | 2026-10-26 | Documentado el comportamiento realmente implementado: 200, 6 caracteres, deduplicación, `/s/{code}` y errores por defecto de Pydantic. |
| 1.0.0 | 2026-10-21 | Contrato inicial de diseño. |
