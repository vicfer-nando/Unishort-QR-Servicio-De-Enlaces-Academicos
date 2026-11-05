# Research: Crear enlaces cortos (Feature 1)

**Date**: 2026-10-21 | **Plan**: [plan.md](./plan.md) | **Spec**: [spec.md](./spec.md)

Consolida las decisiones de la Fase 0. Resuelve los cuatro
`NEEDS CLARIFICATION` del *Technical Context* del plan (R-01 a R-04), documenta
las mejores prácticas y patrones adoptados para cada tecnología y para la
arquitectura (R-05 a R-10) y registra la decisión de motor de datos y destino
de despliegue (R-11). Cada entrada indica decisión, justificación y
alternativas descartadas.

---

## R-01 Política de límite de tasa sobre la creación

**Decision**: ventana fija de 60 segundos por cliente con un máximo de 60
creaciones. El contador vive en un diccionario en memoria; la clave es la IP
del cliente tomada de la conexión, con un TTL máximo de 60 s, nunca persistida
ni asociada a un enlace. Al superar el umbral se responde `429`. Umbles
configurables por entorno: `UNISHORT_RATE_LIMIT_MAX` (60) y
`UNISHORT_RATE_LIMIT_WINDOW_SECONDS` (60). Al agotarse el TTL la entrada se
elimina; un reinicio del proceso reinicia los contadores.

**Rationale**: la constitución permite usar la IP como clave efímera en memoria
con TTL ≤ 60 s y exige que el límite de tasa cubra la creación; FR-009 lo
exige igualmente. Una ventana fija es O(1) en tiempo y memoria, no necesita
infraestructura y 60 enlaces por minuto están muy por encima del uso humano
normal, así que no afecta al caso feliz.

**Alternatives considered**:
- *Token bucket*: control más preciso, pero añade estado y código sin ganar
  nada a esta escala.
- *Límite por clave de API*: requeriría autenticación, que está fuera de
  alcance.
- *Limitador en el proxy o CDN*: mejor en producción, no existe en desarrollo
  local y no es comprobable con las pruebas de la Feature 1.
- *Redis o almacenamiento compartido*: introduciría infraestructura nueva sin un
  requisito que la pida (YAGNI).

## R-02 Generación del código corto

**Decision**: alfabeto de 32 símbolos sin ambigüedad y en una sola caja:
las 24 letras minúsculas sin `l` ni `o`, más los dígitos `2` a `9`
(`abcdefghijkmnpqrstuvwxyz23456789`). Longitud fija de 7 caracteres, lo que
da 32^7 = 2^35 ≈ 3,44 × 10^10 códigos posibles. Generación con
`secrets.SystemRandom` (fuente criptográfica). Unicidad garantizada por la
restricción de la base de datos; ante un `IntegrityError` el repositorio pide
un código nuevo y reintenta hasta 10 veces, y solo si se agota se devuelve un
error interno. El generador es una interfaz inyectable para que las pruebas
sean deterministas.

**Rationale**: con 1.000.000 de enlaces, la probabilidad de que una nueva
inserción colisione es ≈ 2,9 × 10^-5; con hasta 10 intentos la probabilidad de
fallar es del orden de 10^-47, es decir despreciable. Excluir `0`, `O`, `1` y
`l` y normalizar a minúsculas responde al Principio IV de convenciones de la
constitución y hace que los códigos se lean y se transcriban sin errores.
El reintento cubre el requisito de la constitución de que la ruta de colisión
exista y esté probada.

**Alternatives considered**:
- *base62 completo*: usa caracteres ambiguos, prohibido por la constitución.
- *Las 7 primeras letras de un UUID*: peor distribución en el trozo usado y
  sigue sin resolver la normalización.
- *Código determinista a partir de la URL*: haría que la misma URL diera
  siempre el mismo código, lo que contradice el supuesto de no deduplicar
  (US1.4) y convertiría las colisiones en sistemáticas.
- *nanoID u otra librería externa*: dependencia nueva sin necesidad; la
  generación son 30 líneas comprobables unitariamente.

## R-03 Base pública de la URL corta

**Decision**: `short_url = UNISHORT_BASE_URL` sin barras finales + `/` +
`short_code`. `UNISHORT_BASE_URL` usa `http://localhost:8000` como valor por
defecto en desarrollo; en producción se fija por variable de entorno sin tocar
código, siguiendo el destino de despliegue decidido en R-11.

**Rationale**: el dominio público del servicio no está ratificado en esta fase.
Hacerlo configurable evita reescribir el código cuando se despliegue y mantiene
el contrato de respuesta estable: el campo `short_url` siempre contiene una URL
absoluta y compartible.

**Alternatives considered**:
- *Derivarlo de la cabecera `Host` de la petición*: permite inyectar un host
  arbitrario en el enlace que se devuelve y comparte, lo que es un vector de
  suplantación.
- *Valor fijo en el código*: obligaría a cambiar el código en cada cambio de
  entorno.
- *URL relativa en la respuesta*: no es una URL corta compartible, que es el
  producto.

## R-04 Formato y localización de los errores

**Decision**: envolvente única para todos los errores:

```json
{ "error": { "code": "invalid_host", "message": "…", "field": "url" } }
```

Códigos: `invalid_payload`, `url_too_long`, `invalid_scheme`, `invalid_host`
(host ausente o mal formado), `embedded_credentials`, `rate_limit_exceeded`,
`collision_unresolved`, `persistence_failure`, `internal_error`. Estados:
`422` para fallos de esquema (como exige la constitución), `400` para datos de
dominio inválidos, `409` si la colisión no se resuelve, `429` por límite de
tasa y `500` para fallo de guardado o error desconocido. El orden de
comprobación es fijo: límite de tasa, esquema del cuerpo, reglas de dominio y
persistencia. El idioma se elige con `Accept-Language` (`es` por defecto, `en`
como alternativa) y los mensajes residen en `i18n.py`. Se sobrescribe el
manejador de `RequestValidationError` para que el `422` use la misma
envolvente. El detalle completo está en `contracts/errors.md`.

**Rationale**: la constitución exige códigos HTTP precisos y prohíbe exponer
trazas o detalles internos; la especificación asume mensajes en `es` y `en`. Una
envolvente única evita que el cliente trate distinto un error de validación de
un error de dominio.

**Alternatives considered**:
- *`problem+json` (RFC 7807)*: más estándar, pero añade miembros que todavía
  no se usan; la migración futura es compatible porque `code` y `message` se
  pueden mapear.
- *Dejar el `detail` por defecto de FastAPI*: mezcla dos formatos distintos en
  la misma API y no se puede localizar.

## R-05 Sesión y transacciones con SQLAlchemy 2.x

**Decision**: un único `engine` creado al importar; `sessionmaker` con
`autoflush=False` y `expire_on_commit=False`; la dependencia `get_session` hace
`yield` y cierra la sesión al terminar la petición. El caso de uso abre
explícitamente una transacción, hace `commit` si todo va bien y `rollback` en
cualquier excepción. El repositorio recibe la sesión creada fuera y no la
genera. El `IntegrityError` de la restricción única se traduce en un reintento
con código nuevo.

**Rationale**: es el patrón documentado de FastAPI para aplicaciones
sincrónicas; el cierre garantizado evita fugas de conexión, y pasar la sesión
al repositorio mantiene la transacción bajo el control del caso de uso, que es
donde se decide si la operación tiene éxito o se revierte (FR-007).

**Alternatives considered**:
- *SQLAlchemy asíncrono con `aiosqlite`*: añade complejidad y otra dependencia
  sin ganar rendimiento medible sobre SQLite en desarrollo; se reconsiderará
  al migrar a PostgreSQL.
- *Unit of Work completo*: justificado con varias entidades; con una sola es
  abstracción sin uso.
- *Sesión global compartida*: fuga de estado entre pruebas y entre peticiones.

## R-06 Privacidad del registro y ejecución en Windows

**Decision**: registros estructurados en JSON por stdout con
`request_id`, `method`, `route`, `status`, `duration_ms`, `short_code` y el
host de destino. Nunca se registra la IP, el agente de usuario ni la URL
completa. Uvicorn se arranca con `--no-access-log` para que su registro de
acceso no incluya la IP del cliente. Se acepta `X-Request-Id` de entrada y se
devuelve en la respuesta.

En Windows: `py -3.11 -m venv .venv`, `.venv\Scripts\Activate.ps1` (con
`Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass` si la política lo
bloquea), instalación con `pip install -e .` por el layout `src`, y arranque con
`uvicorn unishort.main:app --reload --host 127.0.0.1 --port 8000 --no-access-log`.
La URL de la base de datos usa ruta relativa (`sqlite:///./unishort.db`) para
evitar las barras inversas de Windows.

**Rationale**: la constitución prohíbe conservar la IP y los datos personales
de quien crea el enlace, y prohíbe registrar URL completas. `--no-access-log`
es la forma explícita y comprobable de cumplirlo, y la ruta relativa de SQLite
elimina la causa más común de fallo del arranque en Windows.

**Alternatives considered**:
- *Middleware propio que sanea el registro de acceso*: más código y más puntos
  de fallo que desactivarlo.
- *Filtrar la IP en un procesador de registros*: la línea ya se construye con
  la IP y cualquier olvido la filtra.
- *Confiar en cabeceras de proxy*: no aplica en desarrollo local y añadiría
  confianza en cabeceras manipulables.

## R-07 Estrategia de pruebas y aislamiento

**Decision**: cada prueba crea su propia base SQLite en memoria con
`StaticPool` y sobrescribe la dependencia `get_session`; no hay estado
compartido y ninguna prueba toca la red pública. El generador de códigos se
inyecta con un doble determinista cuando hace falta controlar el valor. La
cobertura mínima es del 85 % sobre `src/unishort` y del 100 % sobre
`rate_limit.py` y `logging_config.py`. SC-002 se comprueba con un test unitario
que genera 10.000 códigos y exige unicidad, más un test de integración que crea
enlaces por la API y también exige unicidad.

**Rationale**: la constitución exige base de datos aislada por prueba,
determinismo y cobertura del 100 % en los módulos que aplican el Principio IV.
Ejecutar 10.000 peticiones HTTP sería lento y frágil en integración continua,
mientras que la fuente real de la unicidad es el generador, que sí se puede
probar a esa escala en milisegundos.

**Alternatives considered**:
- *Base de datos compartida entre pruebas*: dependencia del orden de ejecución.
- *10.000 peticiones HTTP*: coste alto y fallos de tiempo límite por causas
  ajenas al comportamiento.
- *Dobles de la base de datos*: no comprueban la restricción real de unicidad.

## R-08 No deduplicación de URL (confirmación del supuesto)

**Decision**: cada `POST` crea un enlace nuevo; la misma URL original puede
generar varios códigos cortos distintos. No existe índice ni búsqueda por URL
original.

**Rationale**: es el supuesto documentado en el spec y cubierto por el escenario
US1.4. Simplifica el esquema y el caso de uso, y evita una consulta previa
que además introduciría una condición de carrera entre comprobar y guardar.

**Alternatives considered**:
- *Deduplicar y devolver el enlace existente*: cambia el contrato de la
  respuesta, exige índice y lógica de búsqueda, y no está pedido.
- *Índice único sobre la URL original*: rompería el escenario US1.4.

## R-09 Migraciones del esquema con Alembic

**Decision**: Alembic se inicializa con una migración inicial reversible que
crea la tabla `short_links`, su restricción única sobre `short_code` y sus
índices, con `upgrade` y `downgrade` simétricos. El arranque de la aplicación
no modifica el esquema: las migraciones se aplican con un único comando
documentado (`alembic upgrade head`). Solo las pruebas crean el esquema por
metadatos, sobre su base aislada. La migración se escribe solo con
constructos portables de SQLAlchemy, para que sirva igual en SQLite hoy y en
PostgreSQL en el despliegue decidido en R-11.

**Rationale**: la constitución exige migraciones reversibles aplicadas por un
comando único y prohíbe la edición manual de datos; `create_all` en el arranque
no versiona el esquema ni permite retroceder. Escribirla con constructos
portables evita rehacerla al cambiar de motor.

**Alternatives considered**:
- *`Base.metadata.create_all` al arrancar*: sin versionado, no reversible.
- *Esquema gestionado por la aplicación*: mismo problema y además oculta los
  cambios de estructura.

## R-10 Arquitectura por capas y calidad estática

**Decision**: capas `api` → `services` → `domain`, y `services` →
`persistence`; `domain` no importa FastAPI ni SQLAlchemy. La regla se comprueba
con una prueba unitaria que importa los paquetes de `domain` y exige que
`fastapi` y `sqlalchemy` no aparezcan en `sys.modules`, sin añadir
herramientas nuevas. `ruff` cubre formato y reglas de estilo; `mypy --strict`
se ejecuta sobre `src/unishort`; las funciones se limitan a 50 líneas y 6 ramas;
los docstrings usan estilo NumPy en español. Las dependencias de ejecución se
fijan con `==` en `pyproject.toml` y el conjunto resuelto se bloquea en
`requirements.lock`.

**Rationale**: hacer cumplir la dirección de las dependencias con una prueba
evita añadir una herramienta de comprobación adicional, y el límite de
complejidad es comprobable de forma mecánica. Al tratarse de una aplicación y no
de una librería, fijar versiones exactas hace reproducible el entorno.

**Alternatives considered**:
- *`import-linter`*: dependencia y configuración nuevas para una regla que una
  prueba cubre.
- *Comprobación solo manual en revisión*: no se ejecuta en cada cambio.
- *Versiones mínimas sin fijar*: no es reproducible y la constitución exige
  fijarlas.

## R-11 Motor de datos y destino de despliegue

**Decision** (equipo, 2026-10-21): el destino de producción del servicio es un
contenedor con Uvicorn detrás de un proxy que termina HTTPS, y el motor de
datos de producción será **PostgreSQL**. En esta fase solo se implementan y
prueban SQLite y el desarrollo local: no se añade el cliente de PostgreSQL, no
se escribe configuración específica de ese motor y no se despliega nada. La
migración se prevé portable desde su origen (R-09 y `data-model.md`), y el
motor se elige por la variable de entorno `UNISHORT_DATABASE_URL`, cuyo valor
por defecto sigue siendo `sqlite:///./unishort.db`.

La constitución obliga a retirar el marcador de destino de despliegue y a
fijar la versión exacta del stack mediante una enmienda MINOR aprobada por
mayoría; esa enmienda queda como pendiente del plan.

**Rationale**: SQLite cumple de sobra el desarrollo y las pruebas exigidas, que
la constitución además obliga a ejecutar sobre SQLite. PostgreSQL aporta en
producción concurrencia de escritura, copias de seguridad y réplica, que
SQLite no ofrece. Conducir el motor por configuración y tipos portables deja
toda la parte costosa resuelta ahora, sin cargar con el despliegue en una
feature de producto.

**Alternatives considered**:
- *SQLite también en producción con un ADR que lo justifique*: permitido por la
  constitución, pero descartado por el equipo por sus límites de escritura
  concurrente y de respaldo.
- *MySQL o MariaDB*: mismo papel que PostgreSQL, sin ventaja para el equipo y
  con una comunidad menor en el ecosistema SQLAlchemy que usa el proyecto.
- *Base de datos gestionada en la nube como primera opción*: añade coste y una
  dependencia externa antes de existir siquiera tráfico.
- *Implementar ya el contenedor y el cliente PostgreSQL*: añadiría complejidad
  y pruebas sin entregar valor funcional de la Feature 1, y la constitución
  exige que las pruebas se ejecuten sobre SQLite.

**Consequences**: el contrato de la API, el modelo de datos y el dominio no
cambian; solo cambia el valor de `UNISHORT_DATABASE_URL` cuando exista el
despliegue. Quedan diferidos a una especificación futura el cliente de
PostgreSQL, el contenedor, el proxy con HTTPS y la enmienda de la
constitución.
