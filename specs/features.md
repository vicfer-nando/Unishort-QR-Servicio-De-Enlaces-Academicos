# Funcionalidades de UniShort QR

**Fecha de actualización:** 2026-10-26  
**Tipo de documento:** inventario funcional para planificación y exposición.  
**Alcance:** consolida las features F01–F09 y contrasta cada una con el código,
los contratos y las pruebas existentes.

> Este documento no reemplaza la especificación detallada de
> `specs/001-create-short-link/`. Tampoco modifica `tasks.md` ni declara tareas
> completadas. Las casillas de los criterios de aceptación son controles
> funcionales, no tareas de Spec Kit.

## Cómo leer el estado

| Estado | Significado |
|--------|-------------|
| **Implementada y verificada** | Todos sus criterios principales tienen implementación y evidencia de prueba o comprobación manual. |
| **Parcialmente implementada** | Existe una parte funcional, pero faltan requisitos o verificaciones para considerar la feature terminada. |
| **Pendiente de implementación** | No existe la funcionalidad en el código actual. |
| **Pendiente de verificar** | Existe implementación, pero no hay evidencia suficiente para afirmar que cumple sus criterios. |

**Regla para la exposición:** una feature planificada no debe presentarse como
una funcionalidad terminada. El estado refleja la evidencia disponible al
2026-10-26.

## Resumen de estado

| ID | Feature | Estado | Qué existe hoy | Brecha principal |
|----|---------|--------|----------------|------------------|
| F01 | Crear enlaces cortos | **Parcialmente implementada** | `POST /shorten`, validación básica, código único, persistencia SQLite y respuesta con URL corta | Diferencias con el diseño objetivo: deduplicación, respuesta 200, código de 6 caracteres y manejo incompleto de fallos |
| F02 | Redirigir al destino original | **Parcialmente implementada** | `GET /s/{short_code}` con redirección 307 y 404 para códigos inexistentes | No existen estados de enlace ni comprobación de enlace desactivado o vencido |
| F03 | Generar códigos QR | **Pendiente de implementación** | Ninguna generación de QR; el frontend la anuncia como etapa posterior | No hay generación, endpoint ni visualización PNG |
| F04 | Validar URLs y códigos | **Parcialmente implementada** | Validación de URL con Pydantic, campo obligatorio, esquema http/https y unicidad en base de datos | Longitud máxima distinta de la especificada, credenciales aceptadas, validación de códigos y colisiones no verificadas a escala |
| F05 | Desactivar y caducar enlaces | **Pendiente de implementación** | Solo existe `created_at` | No hay estado, fecha de expiración, desactivación ni autorización |
| F06 | Contabilizar clics | **Pendiente de implementación** | Ningún contador ni consulta de métricas | No se registran accesos ni existen métricas protegidas |
| F07 | Administrar permisos | **Pendiente de implementación** | Ninguna autenticación ni rol | No se pueden autorizar desactivaciones ni consultas de métricas |
| F08 | Gestionar errores y estados | **Parcialmente implementada** | 422 de validación, 404 de código inexistente y errores 500 aislados | Faltan estados desactivado/vencido, envolvente de error, localización y tratamiento uniforme de fallos |
| F09 | Comprobar disponibilidad | **Pendiente de implementación** | `GET /` devuelve un mensaje informativo | No existe `GET /health`; la raíz no es un health check |

**Conteo:** 0 implementadas y verificadas, 4 parcialmente implementadas,
5 pendientes de implementación y 0 pendientes de verificar.

**Ninguna de las nueve features está terminada por completo.** El MVP actual es
un acortador de URLs con creación, deduplicación, redirección, validaciones
básicas y una interfaz web; la generación de QR, la autenticación, los permisos,
la expiración, las métricas y el health check todavía no forman parte del
servicio.

## Estado real del servicio

La implementación actual está formada por un backend FastAPI en `backend/app` y
un frontend estático en `frontend/index.html`.

Endpoints existentes:

| Método y ruta | Comportamiento actual | Features relacionadas |
|---------------|-----------------------|-----------------------|
| `POST /shorten` | Crea o reutiliza un código para una URL y devuelve `short_code`, `short_url` y `original_url` con estado 200 | F01, F04, F08 |
| `GET /s/{short_code}` | Redirige con 307 a la URL original o responde 404 si el código no existe | F02, F08 |
| `GET /` | Devuelve `{"message": "UniShort QR API", "docs": "/docs"}` | Informativo; no es F09 |
| `GET /docs` y `GET /openapi.json` | Documentación automática de FastAPI | Soporte |

No existen endpoints implementados para QR, desactivación, expiración,
estadísticas, autenticación, permisos ni salud del servicio.

Modelo de datos real (`short_urls`): `id`, `short_code` (único), `original_url`
y `created_at`. No hay columnas para estado, expiración, propietario, permisos ni
contadores de clics. La base es SQLite (`unishort.db`) y la tabla se crea
automáticamente al importar la aplicación.

### Evidencia utilizada

- Código: `backend/app/main.py`, `backend/app/schemas.py`,
  `backend/app/models.py`, `backend/app/utils.py`, `backend/app/database.py`.
- Contratos: `specs/001-create-short-link/contracts/shorten.md` y
  `specs/001-create-short-link/contracts/errors.md`.
- Pruebas: `tests/test_basic.py`, `tests/test_shorten.py` y `tests/conftest.py`;
  la auditoría previa reportó **13 pruebas aprobadas**.
- Interfaz: `frontend/index.html`.
- Guía de ejecución: `specs/001-create-short-link/quickstart.md`.

---

## F01 — Crear enlaces cortos

**Estado:** Parcialmente implementada.

**Objetivo:** recibir una URL, validarla, asignarle un código único, guardar la
relación y devolver la URL corta para compartirla.

### Requisitos funcionales

- **RF-F01-01:** aceptar una petición con el campo obligatorio `url`.
- **RF-F01-02:** admitir únicamente URLs absolutas con esquema `http` o `https`
  y host válido.
- **RF-F01-03:** generar un código que no coincida con otro código almacenado;
  si hay colisión, reintentar sin sobrescribir el enlace existente.
- **RF-F01-04:** persistir la relación entre código, URL original y fecha de
  creación.
- **RF-F01-05:** devolver al menos el código corto, la URL corta y la URL
  original.
- **RF-F01-06:** conservar los enlaces después de reiniciar el backend.
- **RF-F01-07:** no confirmar la creación si el guardado falla.
- **RF-F01-08:** no almacenar datos personales del creador.

### Criterios de aceptación verificables

- [x] **CA-F01-01:** una URL `https` válida devuelve los tres campos esperados.
  Evidencia: `test_create_short_url_returns_expected_contract`.
- [x] **CA-F01-02:** el código devuelto cumple el formato actual de 6 caracteres
  alfanuméricos. Evidencia: `test_create_short_url_returns_expected_contract`.
- [x] **CA-F01-03:** dos URLs distintas reciben códigos distintos. Evidencia:
  `test_different_urls_return_different_short_codes`.
- [x] **CA-F01-04:** el código creado puede resolverse mediante
  `GET /s/{short_code}`. Evidencia: `test_short_code_redirects_to_original_url`.
- [ ] **CA-F01-05:** dos envíos de la misma URL generan enlaces nuevos, según el
  supuesto de `spec.md`. Hoy se devuelve el mismo código por deduplicación.
- [ ] **CA-F01-06:** un enlace creado sigue existiendo después de reiniciar el
  servicio. La persistencia SQLite está implementada, pero no hay una prueba de
  reinicio en la suite.
- [ ] **CA-F01-07:** si falla la persistencia, la respuesta es 5xx y no queda un
  enlace parcial. No está cubierto por pruebas.
- [ ] **CA-F01-08:** la respuesta de creación usa el código HTTP acordado. Hoy
  responde 200; el diseño objetivo preveía 201 y la decisión sigue pendiente.

### Evidencia y brechas

Implementado en `POST /shorten` (`backend/app/main.py`). Usa `URLBase`
(`backend/app/schemas.py`), `generate_short_code` (`backend/app/utils.py`) y el
modelo `ShortURL` (`backend/app/models.py`).

Brechas: deduplicación en lugar de un enlace nuevo por envío; respuesta 200 en
lugar de 201; código de 6 caracteres alfanuméricos en lugar de un alfabeto sin
ambigüedad; sin rate limiting; sin prueba de recuperación tras fallo de guardado.

### Dependencias y decisiones pendientes

- Depende de F04 para la validación definitiva y de F02 para que la URL corta sea
  utilizable.
- Decidir si la misma URL debe reutilizar el código o generar uno nuevo.
- Decidir el código HTTP de creación y el formato definitivo del código corto.
- Definir el dominio público de despliegue; la URL corta usa el header `Host` de
  la petición.

---

## F02 — Redirigir al destino original

**Estado:** Parcialmente implementada.

**Objetivo:** buscar el código corto y redirigir a la URL original solo cuando el
enlace pueda utilizarse.

### Requisitos funcionales

- **RF-F02-01:** resolver un código mediante una ruta HTTP de lectura.
- **RF-F02-02:** redirigir a la URL original cuando el código existe y el enlace
  está activo.
- **RF-F02-03:** responder con un error adecuado cuando el código no existe.
- **RF-F02-04:** no redirigir enlaces desactivados o vencidos.
- **RF-F02-05:** no registrar datos personales durante la redirección.

### Criterios de aceptación verificables

- [x] **CA-F02-01:** un código existente responde 307 con la URL original exacta
  en `Location`. Evidencia: `test_short_code_redirects_to_original_url`.
- [x] **CA-F02-02:** un código inexistente responde 404 con un mensaje JSON.
  Evidencia: `test_unknown_short_code_returns_404`.
- [ ] **CA-F02-03:** un enlace desactivado no redirige y devuelve un estado
  diferenciado. Depende de F05.
- [ ] **CA-F02-04:** un enlace vencido no redirige y devuelve un estado
  diferenciado. Depende de F05.
- [ ] **CA-F02-05:** la redirección comprueba la usabilidad del enlace antes de
  emitir la respuesta. Hoy solo comprueba que el código exista.
- [ ] **CA-F02-06:** la redirección no almacena IP, cookies ni identificadores
  personales. El código actual no los guarda, pero falta una prueba específica.

### Evidencia y brechas

Implementado en `GET /s/{short_code}` (`backend/app/main.py`). La ruta no estaba
incluida en el alcance original de `spec.md` de la Feature 1 y quedó documentada
en `contracts/shorten.md`.

Brechas: el modelo no tiene estado ni expiración; por tanto, todo código
existente se considera utilizable. Tampoco existe conteo de clics.

### Dependencias y decisiones pendientes

- Depende de F05 para distinguir enlaces activos, desactivados y vencidos.
- Depende de F06 si la redirección debe contabilizar accesos.
- Decidir los códigos HTTP para enlaces desactivados o vencidos y si se
  devolverá una página explicativa o solo JSON.
- Decidir si los enlaces pueden reactivarse o renovarse.

---

## F03 — Generar códigos QR

**Estado:** Pendiente de implementación.

**Objetivo:** generar y proporcionar una imagen PNG que contenga la URL corta.

### Requisitos funcionales

- **RF-F03-01:** generar un PNG a partir de la URL corta emitida por F01.
- **RF-F03-02:** entregar la imagen con el tipo de contenido correcto y permitir
  su descarga o visualización.
- **RF-F03-03:** rechazar la generación para códigos inexistentes o no
  utilizables.
- **RF-F03-04:** no incluir datos personales en el QR ni en la respuesta.
- **RF-F03-05:** mostrar o descargar el QR desde el frontend cuando la feature
  esté disponible.

### Criterios de aceptación verificables

- [ ] **CA-F03-01:** al solicitar el QR de un código existente se recibe una
  imagen PNG válida.
- [ ] **CA-F03-02:** al decodificar el PNG se obtiene exactamente la URL corta
  correspondiente.
- [ ] **CA-F03-03:** un código inexistente no produce una imagen y recibe un
  error adecuado.
- [ ] **CA-F03-04:** un enlace desactivado o vencido no produce un QR utilizable,
  según la decisión de F05.
- [ ] **CA-F03-05:** el frontend muestra la imagen y permite descargarla.
- [ ] **CA-F03-06:** no se generan códigos QR reales en la suite de pruebas sin
  comprobar antes que el PNG es decodificable.

### Evidencia y brechas

No hay generación de QR en el backend ni en el frontend. `frontend/index.html`
indica expresamente que la generación de QR se incorporará en una etapa
posterior. No existen dependencias de generación de imágenes en el alcance
actual.

### Dependencias y decisiones pendientes

- Depende de F01 y F02 para disponer de una URL corta válida y resoluble.
- Decidir si el QR se genera bajo demanda o se almacena.
- Definir tamaño, margen, nivel de corrección de errores y formato de descarga.
- Elegir la librería de generación y el endpoint o mecanismo de entrega.
- Definir el comportamiento para enlaces desactivados o vencidos (F05).

---

## F04 — Validar URLs y códigos

**Estado:** Parcialmente implementada.

**Objetivo:** validar esquemas, entradas, campos obligatorios y unicidad de los
códigos antes de crear o resolver un enlace.

### Requisitos funcionales

- **RF-F04-01:** exigir el campo `url` en la creación.
- **RF-F04-02:** aceptar solo URLs absolutas con esquema `http` o `https`.
- **RF-F04-03:** rechazar URLs malformadas, sin host o con esquema no permitido.
- **RF-F04-04:** aplicar la longitud máxima acordada para la URL.
- **RF-F04-05:** rechazar credenciales embebidas en la URL, según el diseño
  objetivo del proyecto.
- **RF-F04-06:** garantizar que un código no se reutilice para otro enlace.
- **RF-F04-07:** no crear enlaces cuando la validación falla.
- **RF-F04-08:** validar el formato de los códigos cuando se incorporen entradas
  de códigos personalizados o consultas específicas.

### Criterios de aceptación verificables

- [x] **CA-F04-01:** un cuerpo sin `url` responde 422 con un error de campo
  faltante. Evidencia: caso `missing` de `test_invalid_payloads_return_422`.
- [x] **CA-F04-02:** una cadena no URL responde 422. Evidencia: caso
  `url_parsing`.
- [x] **CA-F04-03:** `javascript:alert(1)` responde 422 por esquema no permitido.
  Evidencia: caso `url_scheme`.
- [x] **CA-F04-04:** una URL de más de 2083 caracteres responde 422. Evidencia:
  caso `url_too_long`.
- [ ] **CA-F04-05:** una URL de más de 2048 caracteres se rechaza según el
  límite de `spec.md`. Hoy el límite efectivo es 2083 y la prueba usa 3000.
- [ ] **CA-F04-06:** una URL con credenciales embebidas se rechaza. Hoy
  `HttpUrl` la acepta; no hay una validación adicional ni una prueba que exija
  rechazarla.
- [x] **CA-F04-07:** dos URLs distintas reciben códigos distintos. Evidencia:
  `test_different_urls_return_different_short_codes`.
- [ ] **CA-F04-08:** una colisión de códigos se resuelve sin sobrescribir el
  enlace existente en una prueba controlada. El código reintenta hasta 10 veces,
  pero la suite no fuerza una colisión.
- [ ] **CA-F04-09:** una ronda de 10.000 creaciones no repite códigos. No hay
  prueba de carga.
- [x] **CA-F04-10:** las validaciones de Pydantic ocurren antes del handler y no
  crean un enlace; la suite confirma el 422, aunque no consulta el conteo en la
  base de datos.

### Evidencia y brechas

La validación de URL está en `backend/app/schemas.py` mediante `HttpUrl`. La
unicidad se apoya en `short_code` único y en la comprobación de
`backend/app/main.py` antes de insertar. La generación está en
`backend/app/utils.py`.

Brechas: límite de 2083 frente a 2048; credenciales embebidas aceptadas;
alfabeto de 6 caracteres con ambigüedad visual; sin prueba de colisión ni de
volumen; sin validación de códigos personalizados porque esa entrada no existe.

### Dependencias y decisiones pendientes

- Depende de F01 para el flujo de creación y de F02 para la resolución.
- Decidir el límite definitivo de longitud y si se aplica antes o después de la
  normalización de Pydantic.
- Decidir si se rechazan siempre las credenciales embebidas.
- Decidir el alfabeto, longitud y estrategia de colisión del código corto.

---

## F05 — Desactivar y caducar enlaces

**Estado:** Pendiente de implementación.

**Objetivo:** permitir la desactivación autorizada de enlaces y controlar fechas
de expiración.

### Requisitos funcionales

- **RF-F05-01:** representar el estado de un enlace (activo, desactivado o
  vencido).
- **RF-F05-02:** permitir desactivar un enlace solo a una persona autorizada.
- **RF-F05-03:** admitir una fecha de expiración y dejar de redirigir cuando se
  alcance.
- **RF-F05-04:** conservar el registro y su historial sin borrar datos de forma
  accidental.
- **RF-F05-05:** informar de forma diferenciada cuando un enlace está
  desactivado o vencido.
- **RF-F05-06:** no exigir datos personales innecesarios para gestionar el
  estado.

### Criterios de aceptación verificables

- [ ] **CA-F05-01:** un enlace activo puede desactivarse con autorización y deja
  de redirigir.
- [ ] **CA-F05-02:** una persona sin permiso no puede desactivar el enlace y
  recibe 401 o 403, según la decisión de F07.
- [ ] **CA-F05-03:** un enlace con fecha de expiración pasada no redirige.
- [ ] **CA-F05-04:** antes de la fecha de expiración, el enlace sigue
  redirigiendo.
- [ ] **CA-F05-05:** el estado se conserva tras reiniciar el servicio.
- [ ] **CA-F05-06:** la respuesta distingue enlace inexistente, desactivado y
  vencido.
- [ ] **CA-F05-07:** la gestión del estado no incorpora IP, cookies ni otros
  datos personales innecesarios.

### Evidencia y brechas

No hay columnas de estado ni de expiración en `short_urls`. Tampoco existen
endpoints de desactivación o renovación ni autenticación. `GET /s/{short_code}`
redirige cualquier código existente.

### Dependencias y decisiones pendientes

- Depende de F07 para autorizar la desactivación.
- Depende de F02 para impedir la redirección de enlaces no utilizables.
- Requiere una migración o cambio de esquema, que no forma parte de esta
  documentación.
- Decidir la representación del estado, la zona horaria, la expiración por
  defecto y el código HTTP para enlaces desactivados o vencidos.
- Decidir si se permite reactivar o renovar enlaces y quién puede hacerlo.

---

## F06 — Contabilizar clics

**Estado:** Pendiente de implementación.

**Objetivo:** contar accesos y permitir consultar métricas con autorización, sin
almacenar datos personales innecesarios.

### Requisitos funcionales

- **RF-F06-01:** incrementar un contador cuando se produzca un acceso
  contabilizable.
- **RF-F06-02:** asociar el contador al enlace correspondiente.
- **RF-F06-03:** permitir consultar métricas solo a una persona autorizada.
- **RF-F06-04:** no almacenar IP, cookies, identificadores de sesión ni datos
  personales innecesarios.
- **RF-F06-05:** definir si los intentos fallidos, desactivados o vencidos
  cuentan como clic.
- **RF-F06-06:** conservar métricas agregadas sin comprometer la privacidad.

### Criterios de aceptación verificables

- [ ] **CA-F06-01:** una redirección válida incrementa el contador del enlace
  exactamente una vez.
- [ ] **CA-F06-02:** dos redirecciones válidas incrementan el contador dos veces.
- [ ] **CA-F06-03:** un código inexistente no incrementa ningún contador.
- [ ] **CA-F06-04:** un enlace desactivado o vencido no incrementa el contador,
  salvo que se decida lo contrario.
- [ ] **CA-F06-05:** una persona autorizada puede consultar las métricas de un
  enlace.
- [ ] **CA-F06-06:** una persona sin permiso recibe 401 o 403 y no ve métricas.
- [ ] **CA-F06-07:** la base de datos no contiene IP, User-Agent, cookies ni
  identificadores personales asociados al clic.
- [ ] **CA-F06-08:** el contador sobrevive a un reinicio del servicio.

### Evidencia y brechas

No hay contadores, tablas de accesos ni endpoints de métricas. La redirección
actual no registra ninguna visita.

### Dependencias y decisiones pendientes

- Depende de F02 para el acceso y de F07 para la autorización.
- Depende de F05 para decidir qué ocurre con enlaces desactivados o vencidos.
- Requiere un cambio de esquema y una política de retención.
- Decidir qué se cuenta (accesos totales, visitantes únicos u otra métrica), si
  se agrega por día y durante cuánto tiempo se conservan los datos.
- Decidir si se excluyen bots o accesos automáticos, sin introducir datos
  personales.

---

## F07 — Administrar permisos

**Estado:** Pendiente de implementación.

**Objetivo:** controlar las operaciones según los permisos de cada usuario.

### Requisitos funcionales

- **RF-F07-01:** identificar al usuario o servicio que realiza una operación
  protegida.
- **RF-F07-02:** definir roles o permisos para desactivar enlaces y consultar
  métricas.
- **RF-F07-03:** impedir que una persona anónima realice operaciones
  administrativas.
- **RF-F07-04:** responder 401 cuando falte autenticación y 403 cuando falten
  permisos.
- **RF-F07-05:** no almacenar datos personales que no sean necesarios para la
  autorización.
- **RF-F07-06:** permitir que la creación anónima de enlaces siga funcionando si
  así se decide.

### Criterios de aceptación verificables

- [ ] **CA-F07-01:** una operación administrativa sin credenciales recibe 401.
- [ ] **CA-F07-02:** una persona autenticada sin rol suficiente recibe 403.
- [ ] **CA-F07-03:** una persona autorizada puede desactivar un enlace.
- [ ] **CA-F07-04:** una persona autorizada puede consultar métricas.
- [ ] **CA-F07-05:** un usuario no autorizado no puede modificar enlaces de otra
  persona.
- [ ] **CA-F07-06:** la creación anónima de enlaces no se rompe por la
  incorporación de permisos, si se mantiene ese alcance.
- [ ] **CA-F07-07:** los datos de autorización no incluyen información personal
  innecesaria.

### Evidencia y brechas

No existe autenticación, sesión, token, rol ni control de acceso. El backend no
tiene dependencias de autorización y todos los endpoints actuales son públicos.

### Dependencias y decisiones pendientes

- Depende de F05 y F06 para proteger sus operaciones.
- Requiere una decisión institucional sobre autenticación, que **no** está
  tomada en el repositorio.
- Decidir el proveedor de identidad, los roles, la propiedad de los enlaces, el
  mecanismo de sesión o token y cómo se asigna el primer administrador.
- Decidir si la creación de enlaces seguirá siendo anónima.

---

## F08 — Gestionar errores y estados de los enlaces

**Estado:** Parcialmente implementada.

**Objetivo:** distinguir errores de validación, enlaces inexistentes,
desactivados o vencidos, y responder con códigos HTTP adecuados.

### Requisitos funcionales

- **RF-F08-01:** responder 4xx ante entradas inválidas y no crear enlaces.
- **RF-F08-02:** responder 404 ante un código inexistente.
- **RF-F08-03:** distinguir un enlace desactivado o vencido de uno inexistente.
- **RF-F08-04:** responder 5xx ante fallos internos sin confirmar operaciones
  incompletas.
- **RF-F08-05:** mantener un formato de error comprensible y consistente.
- **RF-F08-06:** localizar los mensajes según el idioma aceptado por el cliente,
  cuando se implemente.
- **RF-F08-07:** no filtrar detalles internos ni datos personales en los errores.

### Criterios de aceptación verificables

- [x] **CA-F08-01:** un esquema no permitido responde 422 y no crea un enlace.
  Evidencia: `test_invalid_payloads_return_422`.
- [x] **CA-F08-02:** un código inexistente responde 404 con
  `{"detail": "Enlace corto no encontrado"}`. Evidencia:
  `test_unknown_short_code_returns_404`.
- [ ] **CA-F08-03:** un enlace desactivado responde un estado distinto de 404 y
  no redirige. Depende de F05.
- [ ] **CA-F08-04:** un enlace vencido responde un estado distinto de 404 y no
  redirige. Depende de F05.
- [ ] **CA-F08-05:** un fallo de persistencia responde 5xx y no deja un enlace
  parcial. No está cubierto por pruebas.
- [ ] **CA-F08-06:** una colisión no resuelta responde 500 de forma controlada.
  El código lo contempla, pero no hay prueba automatizada.
- [ ] **CA-F08-07:** todos los errores usan una envolvente común
  `{"error": {"code", "message", "field"}}`. No está implementada.
- [ ] **CA-F08-08:** los mensajes se ofrecen en español e inglés según
  `Accept-Language`. No está implementado.
- [ ] **CA-F08-09:** las respuestas de error no exponen trazas, consultas SQL ni
  datos personales.

### Evidencia y brechas

Los errores de validación son los de FastAPI/Pydantic: estado 422 y un arreglo
`detail` en inglés. El código inexistente usa 404 con un mensaje en español. Una
colisión no resuelta usa 500. El frontend transforma `detail` en un mensaje
legible y trata respuestas no JSON.

Brechas: no existe una envolvente de error única; no hay localización ni
`X-Request-Id`; no hay estados de enlace desactivado/vencido; el fallo de
persistencia y la colisión no están cubiertos por pruebas; los errores no
controlados pueden devolver un 500 que no sea JSON.

### Dependencias y decisiones pendientes

- Depende de F04 para los errores de validación y de F05 para los estados.
- Decidir la envolvente de error definitiva, los códigos internos y el formato
  de los mensajes.
- Decidir si se implementa localización y cómo se negocia el idioma.
- Decidir el código HTTP para enlaces desactivados y vencidos.
- Decidir si los errores internos incluyen un identificador de solicitud.

---

## F09 — Comprobar la disponibilidad del servicio

**Estado:** Pendiente de implementación.

**Objetivo:** proporcionar un endpoint `GET /health` con una respuesta JSON de
estado.

### Requisitos funcionales

- **RF-F09-01:** exponer `GET /health`.
- **RF-F09-02:** responder con estado 200 y `Content-Type: application/json`
  cuando el servicio esté disponible.
- **RF-F09-03:** incluir un campo JSON que indique el estado del servicio.
- **RF-F09-04:** no exponer secretos, rutas internas ni datos personales.
- **RF-F09-05:** si se comprueba la base de datos, reflejar su estado sin
  bloquear el servicio innecesariamente.

### Criterios de aceptación verificables

- [ ] **CA-F09-01:** `GET /health` responde 200.
- [ ] **CA-F09-02:** la respuesta es JSON válido con un campo de estado, por
  ejemplo `{"status": "ok"}`.
- [ ] **CA-F09-03:** la respuesta no requiere autenticación si así se decide.
- [ ] **CA-F09-04:** la respuesta no revela secretos ni detalles internos.
- [ ] **CA-F09-05:** si se incluye una comprobación de base de datos, un fallo de
  la base se refleja de forma controlada.
- [ ] **CA-F09-06:** existe una prueba automatizada de `GET /health`.

### Evidencia y brechas

Verificado por inspección de `backend/app/main.py`: las únicas rutas son
`POST /shorten`, `GET /s/{short_code}` y `GET /`. No existe `GET /health`.
`GET /` devuelve un mensaje informativo y la ruta de documentación; **no debe
presentarse como health check**. `tests/test_basic.py` prueba la raíz y OpenAPI,
no `/health`.

### Dependencias y decisiones pendientes

- La versión mínima no depende de otras features.
- Si se quiere un readiness check, depende de la base de datos.
- Decidir si será un liveness check simple o un readiness check con comprobación
  de SQLite.
- Decidir los campos exactos de la respuesta y si el endpoint será público.

---

## Brechas transversales

Estas brechas afectan a varias features y no deben confundirse con features ya
terminadas:

- **Rate limiting:** no implementado.
- **Autenticación y permisos:** no implementados; bloquean F05, F06 y F07.
- **Estado y expiración:** no existen en el modelo; bloquean F02, F03, F05 y F08.
- **Métricas:** no existen; F06 está pendiente.
- **QR:** no implementado; F03 está pendiente.
- **Health check:** no implementado; F09 está pendiente.
- **Formato de errores:** la envolvente `error.code/message/field`, la
  localización y `X-Request-Id` siguen pendientes.
- **Dominio público:** `TODO(DEPLOY_TARGET)` no está resuelto; la URL corta usa
  el `Host` de la petición.
- **Decisiones de contrato:** respuesta 200 frente a 201, deduplicación frente a
  enlace nuevo, y código de 6 caracteres frente al alfabeto sin ambigüedad.
- **Privacidad:** el código actual no almacena IP ni cookies, pero F05–F07
  deberán mantener esa minimización cuando se implementen.
- **Despliegue:** no hay migraciones ni configuración de producción; SQLite y
  `create_all` son el mecanismo actual.

## Trazabilidad con la documentación existente

- `specs/001-create-short-link/spec.md` formaliza principalmente la creación de
  enlaces (F01) y declara fuera de alcance QR, redirección, estadísticas y
  autenticación. La redirección existe hoy en el código, pero no estaba en ese
  alcance original.
- `specs/001-create-short-link/plan.md` y `tasks.md` conservan el diseño y la
  planificación de la Feature 1; **no se modificaron** en esta edición.
- `specs/001-create-short-link/contracts/shorten.md` y `contracts/errors.md`
  describen el contrato real y sus diferencias con el diseño objetivo.
- `specs/001-create-short-link/quickstart.md` describe el arranque y el alcance
  operativo actual.
- `tests/test_basic.py` y `tests/test_shorten.py` son la evidencia automatizada
  disponible.
- No existían documentos de especificación para F03–F09; este documento las
  deja identificadas como planificadas o parciales, sin convertirlas en tareas
  completadas.

## Guion breve para la exposición

1. **Presentar el alcance real:** UniShort QR es hoy un acortador de URLs con
   creación, deduplicación, redirección 307, validaciones básicas y frontend.
2. **Demostrar solo lo implementado:** crear una URL, repetirla para mostrar la
   deduplicación, abrir el enlace corto, provocar un 422 con una URL inválida y
   mostrar un 404 con un código inexistente.
3. **Separar el plan de lo real:** indicar que F01, F02, F04 y F08 son parciales;
   que F03, F05, F06, F07 y F09 están pendientes; y que ninguna feature está
   terminada y verificada por completo.
4. **Aclarar el nombre:** el proyecto se llama UniShort QR, pero la generación de
   QR (F03) todavía no está implementada. El propio frontend lo indica.
5. **No afirmar:** autenticación institucional, permisos, caducidad, métricas,
   rate limiting ni `GET /health` como funcionalidades existentes.
6. **Frase sugerida:** “Tenemos un MVP funcional de acortamiento y redirección;
   las demás capacidades están documentadas como alcance planificado y tienen
   dependencias y decisiones pendientes.”
