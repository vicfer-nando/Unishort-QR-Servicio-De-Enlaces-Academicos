# Plan de QR: reconciliación de la implementación existente

Fecha: 2026-11-05. Especificación: [spec.md](spec.md).

Se conserva FastAPI y la tabla `short_urls`. `GET /api/v1/links/{code}/qr`
resuelve el estado mediante servicios, compone la URL pública configurada y
genera un PNG en memoria con qrcode y Pillow. No consulta el destino ni
incrementa el contador. No requiere otra tabla ni una migración de QR.

El frontend muestra `qr_url` y descarga con fetch → Blob → enlace local. Los
errores de fetch se muestran mediante el mecanismo existente de mensajes.
El contrato HTTP permanece en [contracts/qr.md](contracts/qr.md).

Validación: contratos 404/410, decodificación con OpenCV, ausencia de clics al
consultar QR, JavaScript real con DOM simulado y prueba HTTP con procesos reales.
La verificación visual pendiente está registrada en `tasks.md`.

## Constitution Check y complejidad

| Decisión | Justificación | Alternativa descartada |
|----------|---------------|------------------------|
| qrcode + Pillow | Dependencias ya existentes; PNG local y zona de silencio ≥4 | Servicio externo: consulta/red y riesgo de privacidad |
| OpenCV en desarrollo | Decodifica el PNG de verdad | Inspeccionar solo la firma PNG no acredita contenido |
| Conservar backend/app y JS existente | Evitar reconstrucción del MVP | Migrar a src o a otro framework sin necesidad |

No se certifica aprobación histórica ni cumplimiento integral de la
constitución: la interfaz sigue principalmente en español, faltan revisión
humana y prueba con usuario no técnico. Son pendientes, no aprobaciones
implícitas. ADR: [0006](../../docs/adr/0006-qr-local.md).
