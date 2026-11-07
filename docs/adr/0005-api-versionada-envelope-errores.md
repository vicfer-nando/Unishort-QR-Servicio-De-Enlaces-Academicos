# ADR 0005: API versionada, envelope común y errores localizados

- **Estado:** Aceptado
- **Fecha:** 2026-11-05
- **Incremento:** Evaluación Sumativa 1

## Contexto

La implementación heredada devolvía respuestas planas, errores por defecto de
Pydantic y códigos `200`/`500`. La especificación objetivo exige una envolvente
común (`success`, `message`, `data`, `errors`, `meta`), códigos HTTP precisos,
localización `es`/`en` y una superficie estable para clientes.

## Decisión

- Nueva API versionada en **`/api/v1`**.
- Envelope común en respuestas JSON de v1.
- Redirecciones `3xx` sin cuerpo JSON.
- Códigos HTTP: `201` creación, `400` dominio, `401/403/503` administración,
  `404` inexistente, `409` colisión, `410` desactivado o caducado, `422`
  validación, `429` límite, `500` persistencia.
- La API heredada `/shorten` y `/s/{code}` conserva su contrato para no romper
  clientes ni enlaces publicados.
- `X-Request-Id` se acepta o genera y se devuelve en todas las respuestas.

## Motivos

- Un único formato de error simplifica el frontend y las pruebas.
- La versión en la ruta permite evolucionar sin romper enlaces ya compartidos.
- La compatibilidad heredada evita una migración destructiva.
- OpenAPI se genera desde FastAPI; no se falsea a mano.

## Alternativas descartadas

- **Sustituir `/shorten` por `/api/v1/links`:** rompería clientes y pruebas
  existentes.
- **Mantener errores por defecto de Pydantic:** impide localizar y unificar.
- **`problem+json` (RFC 7807):** válido, pero sus miembros no se usan todavía;
  la migración futura es compatible.

## Consecuencias

- Existen dos contratos documentados: heredado y v1.
- Toda evolución incompatible de v1 deberá incrementar la versión mayor.
- Los contratos en `specs/` deben actualizarse junto con la implementación.

## Cotejo con el contrato oficial — 2026-11-06

El PDF, pp. 4–5, presenta errors:null como referencia y permite extensiones
justificadas. v1 conserva errors:[] en éxito y una lista tipada en error:
evita ramas null/list en clientes y no rompe los contratos existentes. Mantiene
las cinco claves universales. Es una decisión documentada, no aprobación docente.

PNG (image/png) y 307 sin JSON son representaciones/protocolo HTTP, igual que
OpenAPI es un documento de esquema y Swagger una herramienta. No hay operaciones
de negocio que requieran 204/304: no se añaden artificialmente para la rúbrica.

Las rutas heredadas GET / y POST /shorten y algunos errores de GET /s/{code}
conservan JSON plano/detail. Son una **excepción de compatibilidad**, no una
excepción propia del protocolo. Su normalización queda para otra versión o
retirada planificada; el flujo recomendado y el panel consumen exclusivamente v1.
Se deja este riesgo explícito para evaluación, sin declarar universalidad absoluta.
