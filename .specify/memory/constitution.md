<!--
INFORME DE IMPACTO (Sync Impact Report) - material de trabajo temporal para la
revisión humana de esta enmienda. Este bloque DEBE eliminarse antes de
confirmar (commit) la constitución enmendada.

Cambio de versión: 1.0.0 -> 1.1.0 (MINOR)
Justificación del incremento: se incorpora un principio nuevo (IV. Protección
de Datos y Privacidad), se resuelve TODO(TECH_STACK) y el stack tecnológico
pasa a ser una restricción vinculante, y se amplían varias secciones. No se
elimina ninguna regla: el contenido de integridad de datos de v1.0.0 se
traslada a "Restricciones Adicionales > Modelo de Datos y Persistencia" y el
contenido de seguridad de URL se traslada a "III. Validación de Entradas".
Un MAJOR (2.0.0) solo sería exigible si se hubiera cambiado la intención de
algún principio vigente, lo cual no ocurrió.

Principios modificados (título anterior -> título nuevo):
  - I. Spec-Driven Development (NON-NEGOTIABLE)
      -> I. Especificación Antes que Código (NO NEGOCIABLE)
  - II. Test-First Verification (NON-NEGOTIABLE)
      -> V. Pruebas Automatizadas (Test-First, NO NEGOCIABLE) [reordenada; su
         contenido se mantiene íntegro y se amplía con cobertura, aislamiento y
         ejecución en CI]
  - III. Stable & Versioned HTTP Contract
      -> III. Validación de Entradas y Contrato de API [ampliada: se incorpora
         la validación estricta de entradas y la validación de URLs de destino]
  - IV. Deterministic Short Codes & Data Integrity
      -> IV. Protección de Datos y Privacidad (principio nuevo). Las reglas de
         unicidad, transacciones y migraciones NO se eliminan: se trasladan
         íntegra a "Restricciones Adicionales > Modelo de Datos y Persistencia"
  - V. Security by Default
      -> absorbido por III (validación de entradas y de URLs) e IV (protección
         de datos). Sus reglas se conservan íntegras, ahora de forma explícita

Secciones añadidas:
  - Restricciones Adicionales > Convenciones de Código (nueva)
  - Restricciones Adicionales > Documentación (nueva)
  - Restricciones Adicionales > Accesibilidad e Internacionalización (nueva)
  - Restricciones Adicionales > Stack Tecnológico (nueva; resuelve
    TODO(TECH_STACK) de v1.0.0)

Secciones eliminadas:
  - Ninguna. Se conservan todas las secciones del patrón: Principios
    Fundamentales, Restricciones Adicionales, Flujo de Desarrollo y Gobernanza.

Elementos diferidos (marcadores TODO dejados intencionalmente en el documento):
  - TODO(DEPLOY_TARGET): el destino de despliegue y el motor de datos en
    producción no están ratificados. SQLite queda ratificado solo para
    desarrollo inicial y pruebas. Debe decidirse en el Technical Context del
    plan y ratificarse por enmienda MINOR. Comando de seguimiento: /speckit.plan
  - La fecha de ratificación se infirió como 2026-10-21 a partir de la marca de
    instalación de Spec Kit en .specify/workflows/workflow-registry.json, ya
    que no existía una constitución previa ratificada. Confirmar antes de
    confirmar (commit).

Supuestos registrados para revisión:
  - "UniShort QR" designa un acortador de URLs con generación de códigos QR.
    Los requisitos de QR (ISO/IEC 18004, zona de silencio, contraste, texto
    alternativo, prueba de decodificación) se derivan del nombre del producto y
    no de una decisión explícita del equipo.
  - Idioma del documento: español, por ser el idioma de trabajo del equipo. Los
    identificadores del código permanecen en inglés (ver Convenciones de
    Código).
  - Se elimina el supuesto "Grupo 7 / mayoría de 4 de 7" de v1.0.0: el nombre
    del producto cambió y no hay evidencia de un tamaño fijo de equipo. Ahora
    se dice "mayoría del equipo".
  - Las versiones indicadas son mínimos aceptables, no pins. La versión exacta
    DEBE fijarse en pyproject.toml y bloquearse en el lockfile.
  - "Prioriza las especificaciones antes de implementar" se materializa como el
    Principio I y como Puerta de Calidad A.
-->

# Constitución de UniShort QR

> Convención de lenguaje normativo: **DEBE** (MUST) y **NO DEBE** (MUST NOT)
> son obligaciones verificables; **PUEDE** (MAY) es una facultad explícita; y
> **DEBERÍA** (SHOULD) es una recomendación que exige justificación escrita si
> no se cumple. "Visitante" designa a cualquier persona que usa un enlace corto
> sin ser propietaria del enlace.

## Principios Fundamentales

### I. Especificación Antes que Código (NO NEGOCIABLE)

Toda funcionalidad DEBE originarse en una especificación escrita en
`specs/<NNN>-<nombre-funcionalidad>/spec.md`, generada por `/speckit.specify` y
aprobada por la mayoría del equipo antes de escribir una sola línea de código
de producción. Cada especificación DEBE declarar historias de usuario
priorizadas, y cada historia DEBE contener al menos un escenario de aceptación
escrito en formato Given/When/Then.

El trabajo DEBE seguir el orden `spec.md` -> `plan.md` -> `tasks.md` -> código.
Todo cambio que altere un requisito declarado DEBE actualizar `spec.md`
primero; el código de producción NO DEBE escribirse por adelantado a una tarea
aprobada en `tasks.md`.

Las ambigüedades DEBEN resolverse con `/speckit.clarify` antes de pasar a
`/speckit.plan`, y la preparación para implementar DEBE verificarse con
`/speckit.checklist`.

Justificación: en un acortador de URLs con códigos QR, la corrección vive en
los casos límite (colisiones de código, enlaces vencidos o deshabilitados,
destinos malformados, QR ilegibles). Escribirlos primero es la única forma
fiable de hacerlos revisables y verificables.

### II. Código Mantenible y Tipado

Todo el código de producción DEBE estar escrito en Python moderno, tipado de
forma explícita y organizado en capas con dependencias en un solo sentido.
Las anotaciones de tipo DEBEN estar presentes en toda función, clase y
módulo público, y `mypy --strict` DEBE pasar sin errores sobre el paquete de
aplicación. El formateador y el linter acordados (`ruff`) DEBEN pasar sin
errores usando la configuración compartida del repositorio.

Las capas DEBEN organizarse de forma que `api` dependa de `services`, `services`
dependa de `domain` y `services` dependa de la capa de persistencia, y la
capa de dominio NO DEBE importar FastAPI, SQLAlchemy ni la capa `api`. Una
función NO DEBE superar 50 líneas ni 6 ramas; la lógica compleja DEBE
extraerse a funciones puras y verificables de forma unitaria.

La configuración DEBE obtenerse de variables de entorno mediante
`pydantic-settings`. Los secretos NO DEBEN aparecer en el código ni en el
control de versiones, y los archivos `.env` NO DEBEN confirmarse. El manejo de
errores DEBE apoyarse en excepciones de dominio mapeadas a
respuestas HTTP por un único manejador; los detalles internos y las trazas de
pila NO DEBEN exponerse en las respuestas.

Justificación: el proyecto arranca con un único equipo y va a crecer en
funcionalidades. Un monolito modular con tipado estricto reduce el coste de
cada cambio posterior mucho más de lo que cuesta el andamiaje inicial.

### III. Validación de Entradas y Contrato de API

Toda entrada externa (cuerpo, parámetros de ruta, parámetros de consulta y
cabeceras) DEBE validarse con modelos Pydantic v2 en el borde de la
aplicación, antes de alcanzar la lógica de negocio. Los modelos de entrada
DEBEN rechazar campos desconocidos y declarar explícitamente el valor por
defecto de todo campo opcional. Las restricciones de longitud, formato y rango
DEBEN expresarse en el modelo, y los validadores personalizados DEBEN ser
funciones puras con su prueba unitaria correspondiente.

Los errores DEBEN mapearse a códigos HTTP precisos: 422 para fallos de
esquema, 400 para datos de dominio inválidos, 404 para un código corto
desconocido o vencido, 409 para colisiones de código y 429 cuando aplique un
límite de tasa. Las respuestas de error NO DEBEN incluir trazas de pila ni
detalles internos.

Las URLs de destino DEBEN validarse antes de almacenarse: solo se aceptan los
esquemas `http` y `https`, la URL DEBE ser absoluta y tener host no vacío, y
las URL con credenciales embebidas (`usuario:clave@host`) DEBEN rechazarse. El
servidor NO DEBE resolver, sondear ni descargar la URL de destino, ni durante
la validación ni durante la redirección.

El contrato público DEBE documentarse en
`specs/<NNN>-<nombre-funcionalidad>/contracts/` antes de implementarlo, y ese
contrato es una superficie de compatibilidad. Un cambio que elimine un campo,
estreche un valor aceptado o altere un código de estado o la forma del error
es incompatible: DEBE incrementar la versión mayor de la API e incluir una
nota de migración en la especificación. La redirección DEBE responder con un
estado 3xx y la cabecera `Location`, sin hacer proxy del contenido de
destino.

Justificación: la validación en el borde es la única barrera que separa la
entrada del atacante de la lógica de negocio. Y los enlaces cortos publicados
son artefactos permanentes insertados en contenido de terceros, por lo que el
formato en el cable debe evolucionar más despacio que los internos.

### IV. Protección de Datos y Privacidad (NO NEGOCIABLE)

El servicio NO DEBE almacenar la dirección IP de los visitantes, ni
identificadores de dispositivo, ni ningún dato personal de los visitantes
(nombre, correo electrónico, teléfono, documento de identidad, geolocalización,
agente de usuario, cookies). NO DEBE usar cookies de seguimiento, técnicas de
huella digital ni píxeles de terceros en el flujo de redirección.

Las métricas de clics DEBEN ser agregadas y no trazables: como máximo el
código corto, una marca de tiempo en UTC y un contador. NO DEBEN persistirse
eventos individuales de clic. El límite de tasa PUEDE usar la IP como clave
efímera en memoria, con un TTL máximo de 60 segundos, y esa clave NO DEBE
persistirse ni asociarse a un enlace almacenado; la alternativa preferida es
aplicar el límite en el proxy.

Los registros de acceso del servidor DEBEN desactivarse o anonimizarse para
que no registren la IP del cliente, y los logs NO DEBEN contener datos
personales ni URLs de destino completas. El código QR NO DEBE codificar
datos personales ni URLs con credenciales. La analítica de terceros NO DEBE
integrarse sin una decisión de privacidad documentada en la especificación y
un registro de decisión arquitectónica (ADR). En producción, todo el tráfico
DEBE servirse sobre HTTPS.

Cualquier infracción de este principio DEBE bloquear la fusión del cambio,
con independencia del resto de los criterios.

Justificación: el acortador es un servicio público que acepta URLs de
cualquier origen y redirige usuarios hacia ellas. Guardar IPs o datos de los
visitantes introduce una responsabilidad legal y de seguridad que no aporta
valor funcional: las métricas agregadas responden las mismas preguntas de
producto.

### V. Pruebas Automatizadas (Test-First, NO NEGOCIABLE)

Las pruebas DEBEN escribirse antes de la implementación que cubren y DEBEN
observarse fallando por la razón esperada antes de que esa implementación
exista (Rojo -> Verde -> Refactor). Cada escenario de aceptación de la
especificación DEBE tener al menos una prueba automatizada, y la correspondencia
DEBE ser trazable desde el nombre o la ruta del archivo de prueba.

`pytest` DEBE ser el ejecutor de pruebas. Las pruebas DEBEN organizarse en
`tests/unit`, `tests/integration` y `tests/contract`, reflejando la estructura
del paquete de aplicación. La suite completa DEBE pasar antes de dar por
terminada una tarea y antes de fusionar cualquier cambio.

La cobertura DEBE ser de al menos 85 % sobre el código de aplicación y del
100 % sobre los módulos que manejen datos de visitantes o apliquen las reglas
del Principio IV. Las pruebas NO DEBEN acceder a la red pública, DEBEN usar
una base de datos SQLite aislada y temporal por prueba, y NO DEBEN depender del
orden de ejecución. Una prueba NO DEBE marcarse como omitida o attendu sin una
incidencia vinculada y una fecha de expiración. Los casos que dependan del
reloj o del azar DEBEN ser deterministas.

El lint, el verificador de tipos y la suite completa DEBEN ejecutarse en
integración continua en cada pull request.

Justificación: la resolución de códigos cortos es un contrato con terceros. Una
regresión silenciosa en la semántica de redirección, en los códigos de estado
o en el vencimiento rompe enlaces ya publicados y no se puede reparar sin
que nadie lo note.

## Restricciones Adicionales

### Stack Tecnológico

El stack DEBE ser el siguiente, y sus versiones mínimas aceptables son:

- Python >= 3.11
- FastAPI >= 0.110
- Pydantic >= 2.7
- SQLAlchemy >= 2.0
- Alembic >= 1.13
- Uvicorn (servidor ASGI)
- pytest >= 8.0 y httpx >= 0.27 (cliente de pruebas)
- SQLite 3.x como motor de datos para el desarrollo inicial y las pruebas

Las versiones indicadas son mínimos, no pins. La versión exacta DEBE fijarse en
`pyproject.toml` y bloquearse en el lockfile del proyecto. Cada dependencia
nueva en tiempo de ejecución DEBE justificarse en la tabla Complexity Tracking
del plan y en un ADR. NO DEBE introducirse un segundo framework web, un segundo
ORM ni una segunda librería de validación.

### Convenciones de Código

- Los identificadores del código (módulos, funciones, clases, variables) DEBEN
  estar en inglés y seguir PEP 8: `snake_case` para funciones y módulos,
  `PascalCase` para clases, `UPPER_SNAKE_CASE` para constantes.
- La documentación, los docstrings y los comentarios DEBEN estar en español.
- Todo módulo, clase y función pública DEBE tener un docstring con propósito,
  parámetros, valor de retorno y excepciones lanzadas, en estilo NumPy.
- Los comentarios DEBEN explicar el porqué, nunca el qué; el qué ya está en el
  código.
- Los nombres DEBEN ser descriptivos y explícitos; las abreviaturas y los
  nombres de un solo carácter NO DEBEN usarse salvo en índices de bucle
  triviales.
- La lógica de negocio NO DEBE duplicarse: el comportamiento compartido DEBE
  residir en el dominio o en la capa de servicios, nunca copiado entre
  endpoints.
- El código DEBE seguir PEP 8 y las convenciones de `ruff` acordadas; el
  formateador NO DEBE entrar en conflicto con el linter.

### Modelo de Datos y Persistencia

- El acceso a datos DEBE hacerse con SQLAlchemy 2.x (ORM), con una sesión por
  petición creada mediante inyección de dependencias y cierre garantizado.
- El código corto DEBE ser globalmente único, y esa unicidad DEBE estar
  garantizada por una restricción de base de datos, no solo por lógica de
  aplicación.
- La generación del código DEBE usar un conjunto de caracteres inequívoco (sin
  `0`/`O`, sin `1`/`l`) y DEBE normalizarse a una sola caja. La generación
  aleatoria está permitida, pero la ruta de colisión (reintento, longitud
  alternativa o error de conflicto explícito) DEBE existir y DEBE estar
  cubierta por una prueba que fuerce la colisión.
- Las marcas de tiempo DEBEN guardarse en UTC y ser conscientes de zona
  horaria.
- Los cambios de esquema DEBEN entregarse con una migración de Alembic
  reversible, aplicada por un único comando documentado. Una migración NO DEBE
  exigir la edición manual de datos.
- Las escrituras que afecten a varios registros DEBEN ejecutarse dentro de una
  transacción y DEBEN revertirse por completo ante un fallo.
- La URL de destino DEBE almacenarse una vez aceptada en su forma completa e
  inmodificada. Repuntar un enlace a otro destino DEBE ser una operación
  explícita, auditada y nunca un efecto secundario implícito de otra petición.
- Los índices DEBEN cubrir el código corto (único), la fecha de creación y la
  fecha de vencimiento.

### Rendimiento y Escalabilidad

- La resolución de un enlace DEBE completarse en menos de 50 ms en el percentil
  95 de la capa de aplicación, excluyendo el tiempo de red del cliente hacia el
  destino.
- La creación de un enlace DEBE completarse en menos de 150 ms en el percentil
  95, incluida la persistencia.
- El modelo de almacenamiento DEBE soportar al menos 1.000.000 de enlaces
  guardados sin cambiar el modelo de datos.
- SQLite NO DEBE usarse en producción sin un ADR que lo justifique. La capa de
  persistencia NO DEBE depender de funcionalidades específicas de SQLite, de
  modo que el motor de datos pueda cambiarse sin reescribir el dominio.
- Los endpoints de creación DEBEN estar sujetos a un límite de tasa.

### Documentación

- El README del repositorio DEBE documentar la instalación, la ejecución, las
  pruebas y las migraciones, y DEBE estar actualizado con el estado real del
  proyecto.
- Cada funcionalidad DEBE tener su carpeta `specs/<NNN>-<nombre-funcionalidad>/`
  con la especificación, el plan, las tareas, el modelo de datos, la guía
  rápida y los contratos.
- Las decisiones arquitectónicas (stack, motor de datos, librería de QR,
  autenticación, límites de tasa) DEBEN registrarse como ADR en `docs/adr/`
  con contexto, decisión, alternativas descartadas y consecuencias.
- El esquema OpenAPI DEBE generarse desde FastAPI y DEBE ser exacto; NO DEBE
  falsearse a mano.
- Todo cambio de API pública DEBE actualizar `contracts/` y el registro de
  cambios del proyecto.
- La documentación DEBE describir el comportamiento observable, no la
  implementación interna.

### Accesibilidad e Internacionalización

- Los textos visibles al usuario DEBEN estar externalizados del código y NO
  DEBEN estar incrustados en handlers ni componentes.
- El conjunto inicial de idiomas es `es` y `en`; una funcionalidad que
  introduzca texto visible DEBE ofrecer ambos.
- Toda interfaz de usuario DEBE cumplir el nivel AA de WCAG 2.1 en contraste y
  navegación por teclado.
- Los códigos QR DEBEN cumplir ISO/IEC 18004: zona de silencio mínima de 4
  módulos, contraste suficiente con el fondo y tamaño legible a la distancia
  mínima soportada.
- El contenido de un QR DEBE ser verificable de forma automatizada: la
  generación DEBE estar cubierta por una prueba que decodifique el QR
  generado y compruebe que contiene la URL esperada.
- Los QR DEBEN incluir texto alternativo cuando se expongan como imagen.

## Flujo de Desarrollo

### Ciclo de Desarrollo Dirigido por Especificaciones

- Las funcionalidades DEBEN seguir `/speckit.specify` -> `/speckit.clarify` ->
  `/speckit.plan` -> `/speckit.tasks` -> `/speckit.implement`, y
  `/speckit.analyze` DEBE ejecutarse antes de cada publicación.
- Cada funcionalidad DEBE vivir en `specs/<NNN>-<nombre-funcionalidad>/` y
  contener `spec.md`, `plan.md`, `research.md`, `data-model.md`,
  `quickstart.md`, `contracts/` y `tasks.md`.
- `/speckit.checklist` DEBE usarse como puerta de preparación para implementar y
  DEBE pasar antes de generar tareas.
- La decisión de implementar NO DEBE tomarse sin una especificación aprobada.

### Puertas de Calidad

- Puerta A, antes de implementar: la sección Constitution Check del plan DEBE
  pasar. Toda violación DEBE quedar registrada en la tabla Complexity Tracking
  con el motivo de la necesidad y la alternativa más simple descartada.
- Puerta B, antes de fusionar: la suite completa, el linter y el verificador
  de tipos DEBEN pasar; el diff NO DEBE contener marcadores de plantilla sin
  resolver; cada escenario de aceptación en alcance DEBE tener su prueba
  superada; y el cambio NO DEBE violar el Principio IV.
- Puerta C, antes de publicar: `/speckit.analyze` NO DEBE informar de
  incidencias CRITICAL o HIGH sin resolver, y la lista de comprobación de
  cumplimiento de la constitución DEBE estar firmada.

### Revisión y Aprobación

- Todo cambio DEBE ser revisado por al menos un miembro del equipo distinto de
  su autor, y DEBE ser aprobado por la mayoría del equipo antes de fusionarse.
- Quien revisa DEBE verificar de forma explícita el cumplimiento de los
  Principios I a V, y DEBE rechazar un cambio con una violación sin justificar
  o sin justificación de complejidad.
- Los mensajes de confirmación DEBEN seguir Conventional Commits y DEBEN
  referenciar el identificador de la funcionalidad (por ejemplo,
  `feat(short-link): add code generation (001)`).
- Los cambios que afecten a la privacidad DEBEN ser revisados por al menos dos
  personas, y su justificación DEBE quedar documentada en la especificación.

### Definición de Terminado

Una funcionalidad está terminada solo cuando sus historias de usuario y sus
escenarios de aceptación están implementados y cubiertos por pruebas
superadas; las puertas de calidad anteriores están satisfechas; la API
pública, si la hay, está documentada y versionada; la guía rápida describe
cómo ejecutarla en local; el ADR correspondiente está escrito si hubo una
decisión arquitectónica; y ningún archivo versionado conserva un marcador de
plantilla sin resolver ni una marca `TODO(...)`.

## Gobernanza

- Esta constitución prevalece sobre cualquier otra guía en plantillas, planes,
  listas de tareas o prácticas informales. La única vía de escape es la tabla
  Complexity Tracking del plan, que DEBE aprobarse como cualquier otro cambio.
- Procedimiento de enmienda: las enmiendas DEBE proponerse por
  `/speckit.constitution`, DEBE incluir un informe de impacto con el cambio de
  versión, los principios modificados, las secciones añadidas y eliminadas y
  los elementos diferidos, y DEBE aprobarse por la mayoría del equipo. El
  archivo enmendado DEBE actualizar la versión y la fecha de última enmienda, y
  el bloque del informe de impacto DEBE eliminarse antes de confirmarlo.
- Política de versionado: MAJOR para la eliminación o redefinición
  incompatible de un principio; MINOR para un principio o sección nuevos, o
  para la ampliación material de una guía; PATCH para aclaraciones,
  redacción y correcciones tipográficas. La versión DEBE seguir el formato
  MAJOR.MINOR.PATCH y DEBE incrementarse en cada enmienda aprobada.
- Revisión de cumplimiento: la comprobación Constitution Check de
  `/speckit.plan` DEBE repetirse al inicio de cada funcionalidad y de nuevo
  tras la fase de diseño, y DEBE verificarse en cada puerta de publicación. Una
  violación que no esté justificada en Complexity Tracking DEBE bloquear la
  fusión.
- Un principio obsoleto DEBE marcarse como obsoleto con la versión que lo
  obsoleta y NO DEBE eliminarse en silencio; permanece vigente hasta que la
  versión que lo obsoleta esté completamente implementada.
- Una especificación que contradiga esta constitución DEBE enmendarse o DEBE
  registrar una excepción aprobada y fechada en su propio documento.
- En caso de conflicto entre esta constitución y la ley aplicable, en
  particular la normativa de protección de datos, prevalece la ley.

**Version**: 1.1.0 | **Ratified**: 2026-10-21 | **Last Amended**: 2026-10-21
