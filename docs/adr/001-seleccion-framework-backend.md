# ADR 001: Selección de Framework Backend y Estrategia de Persistencia

* **Estado:** Aprobado
* **Fecha:** 2026-11-05
* **Autores:** MariaCVR, vicfer-nando

## Contexto
Se requiere implementar el servicio de acortador de enlaces académicos y generación de código QR para la UNL. El sistema requiere alto rendimiento en lectura (redirección) y documentación interactiva automática.

## Decisión
Se decide seleccionar **FastAPI (Python 3.11)** como framework backend principal y **SQLite / SQLAlchemy** para la capa de persistencia inicial.

## Consecuencias
* **Positivas:** 
  - Generación automática de especificación OpenAPI / Swagger UI.
  - Alto rendimiento asíncrono y rápida validación de datos mediante Pydantic.
  - Facilidad de ejecución y pruebas locales mediante `pytest`.
* **Negativas / Restricciones:**
  - Migración futura a PostgreSQL requerida cuando el volumen de concurrencia aumente en producción.