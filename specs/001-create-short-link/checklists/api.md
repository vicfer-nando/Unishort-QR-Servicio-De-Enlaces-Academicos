# Lista de comprobación de calidad de requisitos: API y privacidad — Crear enlaces cortos

**Purpose**: Evaluar la calidad de los requisitos escritos (spec, contratos y
modelo de datos) como si fueran pruebas unitarias del texto, no verificar la
implementación.
**Created**: 2026-10-21
**Feature**: [spec.md](../spec.md) | [plan.md](../plan.md) |
[contracts/](../contracts/) | [data-model.md](../data-model.md)

**Note**: Esta lista personalizada la genera `/speckit.checklist` a partir del
contexto de la funcionalidad.
**Review Ownership**: Artefacto de revisión de calidad de requisitos propiedad
del revisor. Marca un ítem `[x]` solo cuando el revisor determina que el
criterio de calidad del requisito está cumplido.
**Marker Semantics**: `[x]` significa que el criterio de calidad del requisito
fue revisado y satisfecho. No significa que la implementación esté completa.

Profundidad: estándar. Audiencia: revisor en revisión de requisitos. Foco:
calidad del contrato de API, privacidad, cobertura de casos límite y
medibilidad de los criterios de éxito.

## Completitud de requisitos

- [ ] CHK001 ¿Está definido el formato y el estado de la respuesta de éxito para cada salida posible de FR-005? [Completitud, Spec §FR-005]
- [ ] CHK002 ¿Están definidos requisitos de error para todos los modos de fallo de la lista de casos límite, incluido el fallo del almacén? [Completitud, Spec §Edge Cases; §FR-007]
- [ ] CHK003 ¿Están especificados los requisitos de localización de los mensajes (idiomas y comportamiento por defecto)? [Completitud, Spec §Assumptions]
- [ ] CHK004 ¿Está definido el resultado exigible cuando dos creaciones simultáneas generan el mismo código corto? [Completitud, Spec §Edge Cases; §US3.2]
- [ ] CHK005 ¿Están definidos los requisitos de conservación tras reinicio de forma verificable y no solo declarativa? [Completitud, Spec §FR-004; §SC-005]
- [ ] CHK006 ¿Está documentado en un artefacto versionado qué interfaz difiere el spec al plan (ruta, nombres de campos, longitud del código)? [Completitud, Spec §Assumptions]

## Claridad de requisitos

- [ ] CHK007 ¿Está cuantificado el límite de creaciones con umbral y duración de ventana explícitos? [Claridad, Spec §FR-009]
- [ ] CHK008 ¿Tiene "longitud máxima admitida" un valor numérico único y el mismo en todos los lugares donde aparece? [Claridad, Spec §FR-002]
- [ ] CHK009 ¿Está definido "código corto único" de forma verificable (longitud, conjunto de caracteres, normalización)? [Claridad, Spec §FR-003; §Assumptions]
- [ ] CHK010 ¿Está definido qué es una "URL válida" más allá de los ejemplos (host, credenciales, espacios)? [Claridad, Spec §FR-002; §Edge Cases]
- [ ] CHK011 ¿Es "dato personal" en FR-008 un concepto cerrado y comprobable? [Claridad, Spec §FR-008; §SC-008]
- [ ] CHK012 ¿Está sin ambigüedad definido el resultado de reenviar la misma URL en ráfaga? [Claridad, Spec §Assumptions; §Edge Cases]

## Consistencia de requisitos

- [ ] CHK013 ¿Son consistentes los estados de error entre US2 y la envolvente documentada en el contrato? [Consistencia, Spec §US2; contracts/errors.md]
- [ ] CHK014 ¿Es consistente la longitud del código corto entre el supuesto de caracteres sin ambigüedad y la longitud fija decidida? [Consistencia, Spec §Assumptions; data-model.md]
- [ ] CHK015 ¿Coinciden los campos de la respuesta entre FR-005, el contrato y el modelo de datos? [Consistencia, Spec §FR-005; contracts/shorten.md; data-model.md]
- [ ] CHK016 ¿Es consistente el tratamiento de las credenciales embebidas entre el supuesto y el requisito de error? [Consistencia, Spec §Assumptions; §US2.4]
- [ ] CHK017 ¿Es consistente la no deduplicación entre US1.4, los supuestos y la ausencia de restricción única de URL en el modelo? [Consistencia, Spec §US1.4; data-model.md]

## Calidad de los criterios de aceptación

- [ ] CHK018 ¿Puede SC-001 verificarse objetivamente, con un universo de "URLs válidas probadas" definido? [Medibilidad, Spec §SC-001]
- [ ] CHK019 ¿Puede SC-004 medirse con un método definido (qué se cronometra y con cuántas muestras)? [Medibilidad, Spec §SC-004]
- [ ] CHK020 ¿Puede SC-002 verificarse con un criterio de unicidad reproducible? [Medibilidad, Spec §SC-002]
- [ ] CHK021 ¿Puede SC-008 verificarse con un procedimiento de inspección definido? [Medibilidad, Spec §SC-008]
- [ ] CHK022 ¿Tiene SC-007 un procedimiento de medición definido para una persona no técnica? [Medibilidad, Spec §SC-007]

## Cobertura de escenarios

- [ ] CHK023 ¿Están los cinco escenarios de US1 escritos de forma que cada uno sea automatizable sin interpretación? [Cobertura, Spec §US1]
- [ ] CHK024 ¿Está cubierto el fallo de almacenamiento (US2.6) con su resultado observable completo, incluida la no existencia de enlaces parciales? [Cobertura, Spec §US2.6]
- [ ] CHK025 ¿Están cubiertos los flujos alternativos y de recuperación (reintento por colisión y superación del límite)? [Cobertura, Spec §US2.7; §US3.2]
- [ ] CHK026 ¿Están cubiertos los criterios de la historia de menor prioridad (US4) con pasos verificables? [Cobertura, Spec §US4]

## Cobertura de casos límite

- [ ] CHK027 ¿Tiene cada caso límite listado un resultado esperado explícito (vacío, esquema, host, credenciales, longitud, guardado, colisión, ráfaga, límite)? [Casos límite, Spec §Edge Cases]
- [ ] CHK028 ¿Está definido el resultado de una URL con espacios dentro del host, no solo la etiqueta "malformada"? [Casos límite, Spec §Edge Cases]
- [ ] CHK029 ¿Está definido el resultado cuando el cuerpo no es JSON o contiene campos desconocidos? [Casos límite, Gap]

## Requisitos no funcionales

- [ ] CHK030 ¿Están cuantificados por separado el rendimiento de la capa de aplicación y el percibido por el usuario? [Requisitos no funcionales, Spec §SC-004; plan.md]
- [ ] CHK031 ¿Están definidos los requisitos de privacidad de quien crea el enlace de forma comprobable (qué no se conserva)? [Privacidad, Spec §FR-008; §US1.5]
- [ ] CHK032 ¿Están definidos los requisitos de internacionalización aplicables a todo texto visible al usuario? [Internacionalización, Spec §Assumptions]

## Dependencias y supuestos

- [ ] CHK033 ¿Está validado el supuesto de no deduplicación, o queda registrado como decisión revisable? [Supuesto, Spec §Assumptions]
- [ ] CHK034 ¿Está documentado el supuesto del dominio público de la URL corta con su estado de decisión? [Supuesto, Spec §Assumptions; research.md R-11]
- [ ] CHK035 ¿Están identificadas las dependencias externas de las que depende el cumplimiento de los criterios de éxito? [Dependencia, Gap]

## Ambigüedades y conflictos

- [ ] CHK036 ¿Está resuelta la relación entre "error 4xx identificable" (FR-006) y los estados concretos que exige la constitución? [Ambigüedad, Spec §FR-006]
- [ ] CHK037 ¿Hay conflicto aparente entre SC-001 ("en la primera petición") y el límite de tasa que devuelve 429? [Conflicto, Spec §SC-001; §FR-009]
- [ ] CHK038 ¿Está resuelta la decisión de destino de despliegue que el spec difiere al plan? [Supuesto, Spec §Assumptions; research.md R-11]
- [ ] CHK039 ¿Existe un esquema de identificadores (FR, US, SC) que permita trazar requisitos con criterios, contratos y modelo de datos? [Trazabilidad, Spec §Requirements]

## Notes

- Marca `[x]` solo tras confirmar que el criterio de calidad del requisito se
  cumple; deja el ítem sin marcar si necesita aclaración o corrección.
- `/speckit.implement` lee el estado de las casillas como puerta y no debe
  modificarlas.
- `checklists/requirements.md` tiene un ciclo de vida propio y separado,
  mantenido por `/speckit.specify` y `/speckit.clarify`.
- Ítems con marcador `[Gap]` señalan requisitos ausentes en el texto escrito,
  no defectos de implementación.
