# Contract: `GET /api/v1/links/{short_code}/qr`

**Contract version**: 1.0.0 | **API version**: 1.0.0 | **Fecha**: 2026-11-05 | **Estado**: implementado

Genera bajo demanda un PNG cuyo contenido es la URL corta del enlace.

## Petición

```http
GET /api/v1/links/abc2345/qr
Accept: image/png
```

- No requiere autenticación.
- No requiere cuerpo.
- `short_code` es el código devuelto al crear el enlace.

## Respuesta de éxito

**Estado:** `200 OK`

```http
Content-Type: image/png
Content-Disposition: inline; filename="unishort-abc2345.png"
Cache-Control: no-store
X-Request-Id: <identificador>
```

El cuerpo es una imagen PNG válida. El texto decodificable es exactamente:

```text
{UNISHORT_BASE_URL}/s/{short_code}
```

Ejemplo con la configuración por defecto:

```text
http://localhost:8000/s/abc2345
```

Nunca se codifica la URL de destino original.

## Errores

Los errores usan el envelope común de `/api/v1`:

| Caso | Estado | `code` |
|------|--------|--------|
| Código inexistente | `404` | `link_not_found` |
| Enlace desactivado | `410` | `link_inactive` |
| Enlace caducado | `410` | `link_expired` |
| Fallo interno de generación | `500` | `internal_error` |

Ejemplo `404`:

```json
{
  "success": false,
  "message": "Enlace corto no encontrado.",
  "data": null,
  "errors": [
    {
      "code": "link_not_found",
      "message": "Enlace corto no encontrado.",
      "field": null
    }
  ],
  "meta": {
    "request_id": "5f0c...",
    "api_version": "1.0.0",
    "language": "es"
  }
}
```

## Garantías

- El QR no se persiste; se genera en memoria en cada petición.
- Consultar el QR **no** incrementa `click_count`; solo la redirección efectiva
  cuenta como clic.
- No se consulta la URL de destino.
- No se registran IP, User-Agent ni otros datos personales.
- El tamaño del módulo y el borde se configuran con `UNISHORT_QR_BOX_SIZE` y
  `UNISHORT_QR_BORDER`.

## Implementación y pruebas

- Generación: `backend/app/qr.py` (`generate_qr_png`).
- Endpoint: `backend/app/api/v1.py` (`get_link_qr`).
- Pruebas: `tests/integration/test_qr.py` (decodificación con OpenCV),
  `tests/contract/test_v1_links_contract.py` (contrato HTTP).

## Registro de cambios

| Versión | Fecha | Cambio |
|---------|-------|--------|
| 1.0.0 | 2026-11-05 | Contrato inicial implementado: PNG, URL corta codificada, 404/410 y sin incremento de clics. |
