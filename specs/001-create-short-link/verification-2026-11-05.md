# Verificación y correcciones del incremento existente

## Alcance y aclaraciones

Se mantienen los contratos v1 y heredado. Esta revisión corrige FR-002
(entradas inválidas), FR-008/009 (privacidad y TTL), FR-010 (navegador) y
QR FR-009 (descarga entre orígenes). No incorpora otro framework ni modifica
datos reales. Las respuestas JSON de rutas desconocidas y métodos no
permitidos bajo `/api/v1` también deben usar el envelope existente; se
conserva la cabecera `Allow` en 405. Los errores internos no exponen datos.

Given una URL con IPv6 malformado, When se crea un enlace, Then responde
400 sin almacenar una fila. Given una cabecera administrativa no ASCII,
When no coincide, Then responde 403, sin un error interno. Given una clave
efímera sin nuevas peticiones, When vence su ventana, Then se elimina de
memoria. Given una petición con PII en ruta, identificador o excepción,
When se registra, Then los logs solo contienen ruta de plantilla y metadatos
seguros. No se registra el identificador recibido del cliente.

## Plan

La ruta heredada `/shorten` también debe rechazar credenciales embebidas con
422 y compartir el límite efímero de creación (429), conforme a FR-008/009.
Mantiene éxito 200, deduplicación, seis caracteres y campos adicionales
ignorados. Se corrige una omisión de seguridad del MVP, sin cambiar la forma
de las respuestas exitosas. Se añaden regresiones antes de implementarlo.

1. Añadir regresiones y observar los fallos antes de corregir producción.
2. Corregir dominio, handlers, autenticación y logs conservando contratos.
3. Eliminar ventanas vencidas también en inactividad, con temporizador daemon
   y reloj inyectable; no persistirlas ni asociarlas a enlaces.
4. Alinear índices ORM/Alembic y verificar con SQLite temporal y copia de la
   base existente. No ejecutar migraciones en el original.
5. Descargar QR mediante fetch y Blob local para respetar `download` entre
   puertos. Verificar navegador real además del contrato HTTP.
6. Verificar Docker/Quarto si están disponibles y registrar límites reales.

## Tareas de esta revisión

- [x] R001 Regresiones de URL, autenticación, envelope y privacidad.
- [x] R002 Correcciones backend, TTL e índices compatibles.
- [ ] R003 Descarga QR entre orígenes y comprobación del navegador.
- [x] R004 Migración conservadora de copia y arranque HTTP real.
- [ ] R005 Docker/Quarto, UTF-8, diagramas y calidad completa.
- [x] R006 Evidencias, guía de demostración y limpieza segura del índice Git.

R003: descarga corregida y comprobada con DOM simulado; navegador bloqueado.
R005: calidad, UTF-8, enlaces, YAML y referencias XML pasan; Docker/Quarto y
render de diagramas no disponibles. No se marcan completadas sus ejecuciones.

Las aprobaciones formales del equipo, las sesiones Spec Kit anteriores y la
prueba con una persona no técnica no se presuponen ni se certifican aquí.
