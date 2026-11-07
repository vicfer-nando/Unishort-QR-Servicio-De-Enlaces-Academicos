# ADR 0002: SQLite en desarrollo y PostgreSQL como destino futuro

- **Estado:** Aceptado
- **Fecha:** 2026-11-05
- **Incremento:** Evaluación Sumativa 1

## Contexto

El servicio existente usa SQLite (`unishort.db`) y el PDF oficial incluye
PostgreSQL en el stack de referencia (pp. 3–4). No hay infraestructura de producción ni credenciales aprobadas. El
incremento debe conservar los datos existentes y evitar una migración
destructiva.

## Decisión

- **Desarrollo y pruebas:** SQLite con SQLAlchemy 2.x.
- **Producción futura:** PostgreSQL, seleccionado por configuración mediante
  `UNISHORT_DATABASE_URL`.
- **Evolución del esquema:** aditiva e idempotente. Las columnas nuevas
  (`is_active`, `expires_at`, `click_count`) se agregan con
  `ALTER TABLE ADD COLUMN`; nunca se recrea la tabla ni se borran filas.

## Motivos

1. SQLite no requiere servidor y permite pruebas rápidas y aisladas.
2. Los tipos usados son portables (`String`, `DateTime`, `Boolean`, `Integer`).
3. El acceso a datos pasa por SQLAlchemy, sin SQL específico del motor en el
   dominio.
4. PostgreSQL ofrece concurrencia de escritura, respaldo y réplica cuando exista
   despliegue real.

## Alternativas descartadas

- **PostgreSQL desde este incremento:** requiere infraestructura, credenciales y
  pruebas adicionales sin tráfico real.
- **SQLite en producción:** posible con ADR, pero limitado en escrituras
  concurrentes y respaldo.
- **Recrear la base existente:** prohibido por el alcance y por pérdida de
  enlaces ya publicados.

## Consecuencias

- Antes de desplegar PostgreSQL deben añadirse su controlador y pruebas sobre
  ese motor. Alembic formal ya existe con migraciones 0001–0003 para SQLite.
- El contador de clics agregado y los índices actuales son compatibles con
  ambos motores.
- La ruta `ensure_schema` es una medida de compatibilidad aditiva. El arranque
  Docker ya ejecuta Alembic; se deberá revisar el SQL específico de compatibilidad
  antes de afirmar portabilidad completa a otro motor. PostgreSQL no está probado.
