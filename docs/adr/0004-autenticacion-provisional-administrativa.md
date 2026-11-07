# ADR 0004: Autenticación administrativa provisional por clave

- **Estado:** Aceptado como mecanismo provisional de desarrollo
- **Fecha:** 2026-11-05
- **Incremento:** Evaluación Sumativa 1

## Contexto

El producto requiere controlar quién puede desactivar enlaces y consultar
métricas. No existe una especificación aprobada de integración institucional
(proveedor de identidad, roles, sesiones) ni credenciales de la universidad. No
se debe inventar una integración externa.

## Decisión

Se implementa una **clave administrativa compartida** enviada en la cabecera
`X-Admin-API-Key` y comparada con la variable de entorno
`UNISHORT_ADMIN_API_KEY` usando `secrets.compare_digest`.

- Sin clave configurada en el servidor: `503 admin_not_configured`.
- Sin cabecera: `401 admin_authentication_required`.
- Clave incorrecta: `403 admin_forbidden`.
- La creación de enlaces sigue siendo pública.

## Motivos

1. Permite demostrar control de acceso real y probado sin bloquear el incremento.
2. No incorpora secretos al repositorio: el valor vive en el entorno.
3. Es fácil de sustituir por OAuth2/OIDC institucional en una especificación
   futura, manteniendo las dependencias `require_admin`.

## Alternativas descartadas

- **Usuarios y contraseñas en base de datos:** almacenaría datos personales sin
  especificación ni necesidad.
- **JWT propio:** añade emisión, rotación y gestión de claves sin proveedor
  institucional.
- **Dejar los endpoints administrativos abiertos:** inaceptable para desactivar
  enlaces y consultar métricas.

## Consecuencias

- La clave es compartida, no identifica personas y no permite roles múltiples.
- Debe rotarse por entorno y nunca confirmarse en Git.
- El mecanismo se documenta como provisional; la autenticación institucional es
  un requisito pendiente y bloqueado hasta que exista especificación aprobada.

## Ampliación 003: panel web (2026-11-05)

La pantalla admin.html valida la clave contra GET /api/v1/links paginado,
endpoint protegido preexistente, y luego consulta GET /api/v1/admin/stats. La clave
vive únicamente en un cierre léxico de JavaScript, nunca en Web Storage, cookies,
HTML o URLs. Al cerrar sesión o abandonar la página se vacía y se abortan peticiones;
las respuestas tardías de otra generación de sesión se descartan. Cada operación
sigue validando require_admin; no se añade una sesión ni permiso decidido por cliente.

Se usa cache no-store, redirect error y credentials omit; el QR se obtiene por una
ruta construida del mismo backend, sin enviar clave ni confiar en qr_url del registro.
Los mensajes de error se seleccionan de un catálogo local y no reflejan respuestas
arbitrarias del servidor. La página tiene CSP restrictiva y no carga terceros.

Alternativas descartadas: persistir la clave para recordar acceso o emitir cookies
propias en esta fase. Consecuencias: recargar exige otra autenticación y cerrar
sesión no revoca la clave compartida global. Se conserva el riesgo de identidad
compartida y exposición ante scripts comprometidos; HTTPS y frontend de confianza
son necesarios. La ampliación está implementada localmente; revisión humana pendiente.
