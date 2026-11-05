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
