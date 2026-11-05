# ADR 0003: Generación y formato del código corto

- **Estado:** Aceptado
- **Fecha:** 2026-11-05
- **Incremento:** Evaluación Sumativa 1

## Contexto

La especificación `001-create-short-link` exige códigos únicos, legibles y sin
deduplicación de URL. La implementación heredada usaba 6 caracteres
alfanuméricos con `random.choice` y un código de 6 posiciones.

## Decisión

- Alfabeto de 32 símbolos sin ambigüedad visual:
  `abcdefghijkmnpqrstuvwxyz23456789`.
- Longitud por defecto: **7 caracteres** (`32^7 ≈ 3,44 × 10^10` combinaciones).
- Generación con `secrets.choice` (fuente criptográfica).
- Unicidad garantizada por la restricción única de la base de datos, no solo por
  una consulta previa.
- Ante colisión, reintento hasta 10 veces; si se agota, `409
  collision_unresolved`.
- Cada creación genera un enlace nuevo; no se deduplica la URL original.

## Motivos

- Se eliminan `0/O` y `1/l`, que causan errores de transcripción.
- La probabilidad de colisión con un millón de enlaces es despreciable.
- El reintento cubre la ruta de colisión exigida por la constitución.
- No deduplicar evita condiciones de carrera y cumple el escenario US1.4.

## Alternativas descartadas

- **Base62 completo:** incluye caracteres ambiguos.
- **Código determinista por URL:** convertiría colisiones en sistemáticas y
  contradice el supuesto de enlaces nuevos.
- **UUID truncado:** peor distribución y longitud variable.

## Consecuencias

- La API heredada `/shorten` conserva el código de 6 caracteres por
  compatibilidad; la API v1 usa 7.
- El frontend muestra el código emitido sin asumir longitud fija en v1.
