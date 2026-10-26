# Feature Specification: Crear enlaces cortos

**Feature Branch**: `001-create-short-link`

**Created**: 2026-10-21

**Status**: Draft

**Input**: User description: "Crear enlaces cortos: el usuario introduce una URL
válida y recibe un enlace corto único que puede compartir. Se debe validar el
formato y el esquema de la URL, generar un código corto único, conservar la
relación entre código y URL de forma duradera, devolver el código y la URL
corta, y rechazar las entradas inválidas con un error claro sin confirmar el
enlace si el guardado falla. Fuera de alcance en esta iteración: generación de
códigos QR, redirección de enlaces, estadísticas de uso y autenticación
institucional."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Crear un enlace corto a partir de una URL válida (Priority: P1)

Como usuario, quiero introducir una URL válida para obtener un enlace corto
única que pueda compartir.

**Why this priority**: Es la única historia que entrega el valor principal del
producto. Sin ella no hay producto que ofrecer, y todas las demás historias
pertenecen a mejoras, errores o comprobación. Si solo se implementa esta
historia, el usuario ya puede acortar un enlace y compartirlo.

**Independent Test**: Enviar una URL válida y comprobar que la respuesta
incluye el código corto, la URL corta y la URL original, y que el enlace quedó
conservado de forma duradera.

**Acceptance Scenarios**:

1. **Given** una URL válida con esquema `https` y host correcto, **When** el
   usuario solicita crear el enlace, **Then** la respuesta contiene el código
   corto, la URL corta y la URL original, y el enlace queda almacenado.
2. **Given** un enlace recién creado, **When** el servicio se reinicia,
   **Then** la relación entre el código corto y la URL original sigue existiendo
   y el enlace no se pierde.
3. **Given** una creación satisfactoria, **When** se observa el código corto
   recibido, **Then** es distinto de todos los códigos ya emitidos.
4. **Given** una URL original que ya fue acortada anteriormente, **When** el
   usuario envía la misma URL de nuevo, **Then** se genera un enlace nuevo con
   su propio código corto, distinto del enlace anterior.
5. **Given** que una persona crea un enlace, **When** se revisa qué
   información conserva el sistema sobre ella, **Then** no se ha guardado ningún
   dato personal, identificador de sesión ni cookie de seguimiento.

---

### User Story 2 - Recibir un error claro cuando la creación no puede completarse (Priority: P2)

Como usuario, quiero un mensaje claro cuando mi solicitud no puede atenderse
para saber si debo corregir la entrada o volver a intentarlo más tarde.

**Why this priority**: Es imprescindible antes de exponer la funcionalidad al
usuario. Sin errores claros, las entradas inválidas llegan al almacén y el
usuario no sabe qué corregir. Es posterior a P1 porque solo tiene sentido
valorar los errores cuando existe la operación que los produce.

**Independent Test**: Enviar entradas inválidas y provocar un fallo de guardado,
comprobando en cada caso que la respuesta es un error de cliente o de servidor
con un mensaje identificable y que no se crea ningún enlace.

**Acceptance Scenarios**:

1. **Given** una cadena vacía, **When** se solicita crear el enlace, **Then**
   la respuesta es un error 4xx que identifica el campo inválido y no se crea
   ningún enlace.
2. **Given** una URL con un esquema distinto de `http` o `https`
   (por ejemplo `ftp://` o `javascript:`), **When** se solicita crear el enlace,
   **Then** la respuesta es un error 4xx con un mensaje que explica el motivo y
   no se crea ningún enlace.
3. **Given** una URL sin host (por ejemplo `https://`), **When** se solicita
   crear el enlace, **Then** la respuesta es un error 4xx con un mensaje que
   explica el motivo y no se crea ningún enlace.
4. **Given** una URL que incluye credenciales embebidas
   (`https://usuario:clave@host`), **When** se solicita crear el enlace,
   **Then** la respuesta es un error 4xx con un mensaje que explica el motivo y
   no se crea ningún enlace.
5. **Given** una URL que supera la longitud máxima admitida, **When** se
   solicita crear el enlace, **Then** la respuesta es un error 4xx con un
   mensaje que indica que la URL es demasiado larga y no se crea ningún
   enlace.
6. **Given** que el almacén de datos no está disponible, **When** se solicita
   crear un enlace, **Then** la respuesta es un error 5xx, la operación no se
   confirma como creada y no queda un enlace a medias.
7. **Given** que una persona supera el número de creaciones permitidas en una
   ventana de tiempo, **When** intenta crear otro enlace, **Then** la respuesta
   es un error 4xx que indica que se superó el límite y no se crea ningún
   enlace.

---

### User Story 3 - Confiar en que cada enlace tiene un código corto propio (Priority: P3)

Como usuario, quiero que mi enlace corto sea único para no compartir dirección
con otra persona que acortó un enlace distinto.

**Why this priority**: Un código compartido haría que dos personas enlazaran a
destinos distintos desde la misma dirección, lo cual es un fallo silencioso y
grave. Va después de P1 y P2 porque solo afecta a la calidad del resultado que
ya se entrega, no a la posibilidad de obtenerlo.

**Independent Test**: Crear una ronda numerosa de enlaces, incluidos dos con la
misma URL original, y comprobar que todos los códigos emitidos son distintos
entre sí.

**Acceptance Scenarios**:

1. **Given** dos URLs originales distintas, **When** se crean los dos enlaces,
   **Then** los códigos cortos obtenidos son distintos entre sí.
2. **Given** una generación que por azar coincide con un código ya emitido,
   **When** se detecta la colisión, **Then** el sistema entrega un código
   distinto sin sobrescribir el enlace existente y la petición termina
   satisfactoriamente.
3. **Given** una ronda de 10.000 creaciones sucesivas, **When** se inspeccionan
   todos los códigos emitidos, **Then** ninguno se repite.

---

### User Story 4 - Comprobar la funcionalidad desde el navegador sin escribir código (Priority: P4)

Como persona evaluadora, quiero crear y verificar un enlace corto desde el
navegador siguiendo las instrucciones de arranque, para validar la
funcionalidad sin preparar un entorno de desarrollo.

**Why this priority**: Responde al resultado esperado de la entrega y facilita
la verificación por parte del equipo y de cualquier evaluador. Es la última
prioridad porque depende de que las operaciones anteriores ya funcionen.

**Independent Test**: Seguir únicamente las instrucciones de arranque en un
navegador y comprobar que se puede crear un enlace y observar su respuesta.

**Acceptance Scenarios**:

1. **Given** que la funcionalidad está en ejecución y se siguen las
   instrucciones de arranque, **When** la persona abre la documentación del
   servicio en el navegador, **Then** puede crear un enlace y ver la respuesta
   completa sin escribir código propio.
2. **Given** que la persona no técnica sigue las instrucciones paso a paso,
   **When** se le pide crear un enlace de prueba, **Then** lo consigue en menos
   de 10 minutos.

---

### Edge Cases

- Cadena vacía o compuesta solo por espacios.
- URL con un esquema no permitido (`ftp://`, `javascript:`, `data:`).
- URL malformada o sin host (`https://`, `https://exa mple.com`).
- URL con credenciales embebidas en la dirección.
- URL que supera la longitud máxima admitida.
- Fallo del almacén de datos durante el guardado: no se confirma el enlace y no
  queda un enlace parcialmente creado.
- Dos creaciones simultáneas que generan por azar el mismo código corto.
- Reenvío de la misma URL por la misma persona en ráfaga: cada petición produce
  un enlace nuevo.
- Superación del número de creaciones permitidas por ventana de tiempo.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: El sistema DEBE permitir crear un enlace corto a partir de la URL
  original que suministra el usuario.
- **FR-002**: El sistema DEBE aceptar como válida únicamente una URL absoluta
  con esquema `http` o `https`, host no vacío y una longitud máxima de 2.048
  caracteres.
- **FR-003**: El sistema DEBE asignar a cada enlace un código corto que NO
  pueda coincidir con el de ningún otro enlace almacenado.
- **FR-004**: El sistema DEBE conservar de forma duradera la relación entre
  cada código corto y su URL original, de modo que el enlace siga existiendo
  tras un reinicio del servicio.
- **FR-005**: El sistema DEBE devolver al crear un enlace el código corto, la
  URL corta y la URL original.
- **FR-006**: El sistema DEBE rechazar con un error 4xx identificable toda
  entrada que incumpla FR-002, sin crear ningún enlace.
- **FR-007**: El sistema NO DEBE responder como creado un enlace cuyo guardado
  no se haya completado; ante un fallo de guardado DEBE responder con un error
  5xx y no dejar enlaces parciales.
- **FR-008**: El sistema NO DEBE recopilar ningún dato personal de la persona
  que crea un enlace (dirección IP, nombre, correo electrónico, cookies o
  identificadores de sesión).
- **FR-009**: El sistema DEBE limitar el ritmo de creación de enlaces por
  cliente de forma efímera, sin conservar ningún dato del cliente.
- **FR-010**: El sistema DEBE permitir crear y comprobar un enlace desde el
  navegador siguiendo las instrucciones de arranque, sin escribir código
  propio.

### Key Entities *(include if feature involves data)*

- **Enlace corto**: relación única entre un código corto y una URL original.
  Atributos: código corto (único y visible en la dirección que se comparte),
  URL original y fecha de creación. Una URL original puede dar origen a varios
  enlaces cortos si el usuario la envía más de una vez.

*En esta iteración no existen entidades de visitante, estadísticas ni códigos
QR.*

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: El 100 % de las URLs válidas probadas (esquema `http` o `https`
  con host correcto) produce un enlace corto en la primera petición, sin
  reintentos por parte del usuario.
- **SC-002**: En una ronda de 10.000 creaciones sucesivas no se repite ningún
  código corto: 0 colisiones visibles para el usuario.
- **SC-003**: El 100 % de las URLs inválidas probadas recibe un error 4xx con
  un mensaje que identifica el problema, y en ningún caso se crea un enlace.
- **SC-004**: El usuario ve el resultado de una creación en menos de 1 segundo
  en el percentil 95 desde que envía la petición.
- **SC-005**: El 100 % de los enlaces creados antes de reiniciar el servicio
  sigue asociado a su URL original después del reinicio.
- **SC-006**: El 100 % de los escenarios de aceptación de esta especificación
  está cubierto por pruebas automatizadas que pasan de forma consistente en
  cada ejecución de la suite.
- **SC-007**: Una persona no técnica consigue crear y comprobar un enlace corto
  desde el navegador en menos de 10 minutos, siguiendo solo las instrucciones
  de arranque.
- **SC-008**: Ningún enlace creado conserva información personal de su creador:
  la comprobación manual y automatizada de los datos almacenados devuelve 0
  datos personales.

## Assumptions

- Cada envío de una URL genera un enlace nuevo; los envíos idénticos no se
  deduplican ni reutilizan un código existente.
- El código corto se presenta en una sola caja y usa caracteres sin ambigüedad
  visual (sin `0`/`O` ni `1`/`l`); su longitud fija se determina en la fase de
  planificación.
- La URL corta se construye sobre el dominio público del servicio, que se
  decidirá en la fase de planificación (ver `TODO(DEPLOY_TARGET)` de la
  constitución).
- Toda URL con credenciales embebidas se rechaza por decisión de la
  constitución del proyecto, aunque sea técnicamente una URL absoluta válida.
- El límite de creaciones por ventana de tiempo y la prohibición de recoger
  datos personales derivan de la constitución del proyecto.
- Los mensajes de error se ofrecen en español y en inglés según el idioma que
  acepte el cliente.
- El servicio no pide cuenta ni identificación en esta iteración: quien crea un
  enlace permanece anónimo.
- Fuera de alcance en esta iteración: generación de códigos QR, redirección de
  enlaces, estadísticas de uso y autenticación institucional. Cada uno se
  tratará en una especificación futura.
- Los detalles de implementación declarados por el usuario (lenguaje, marco de
  trabajo, base de datos, ruta de acceso y nombres exactos de los campos de
  respuesta) quedan fuera de este documento: se recogen en `plan.md >
  Technical Context` y en `contracts/` durante la fase de planificación.
