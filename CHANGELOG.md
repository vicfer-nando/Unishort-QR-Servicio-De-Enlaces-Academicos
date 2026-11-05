# Registro de cambios

## Revisión del 2026-11-05 (sin publicar)

- Corregidos validación IPv6, clave administrativa no ASCII, envelope 404/405,
  OpenAPI 422 y CORS/trazabilidad 500. Se añade `X-Log-Request-Id` sin alterar
  la forma de respuestas v1 ni su versión 1.0.0.
- Logs sin rutas arbitrarias, cabeceras del cliente ni texto de excepciones
  SQL; eliminación de claves del limitador durante inactividad.
- `/shorten` rechaza credenciales y comparte límite de tasa (429) con v1.
  Conserva formato, estado 200, deduplicación y código de seis caracteres.
- QR descargable entre orígenes mediante Blob local.
- Índices ORM alineados con Alembic; migración aditiva `0003`.
- Docker usa lock y Alembic al arrancar; healthchecks y CORS revisados.
- Scripts de comprobación HTTP real, migración de copia, JavaScript y portal;
  workflow de calidad. Docker, navegador y render Quarto pendientes de ejecución.
- Base local y diez `.pyc` retirados solo del índice; archivos e historial intactos.
