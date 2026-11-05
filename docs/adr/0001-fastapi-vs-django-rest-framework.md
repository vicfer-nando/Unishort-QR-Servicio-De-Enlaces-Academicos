# ADR 0001: FastAPI frente a Django REST Framework

- **Estado:** Aceptado
- **Fecha:** 2026-11-05
- **Incremento:** Evaluación Sumativa 1

## Contexto

El proyecto ya existe como servicio FastAPI con SQLAlchemy, SQLite y frontend
estático. La guía de la evaluación menciona Django, Django REST Framework (DRF)
y PostgreSQL como stack de referencia, pero admite justificar tecnologías
alternativas. Migrar a Django implicaría reescribir endpoints, esquemas,
pruebas y el frontend ya integrado, con riesgo alto y valor funcional nulo para
este incremento.

## Decisión

Se mantiene **FastAPI** con **Pydantic v2** y **SQLAlchemy 2.x**. La API se
versiona en `/api/v1` y se conservan los endpoints heredados.

## Motivos

1. **Continuidad:** el MVP, las 13 pruebas originales y el frontend ya funcionan.
2. **Tipado y validación:** Pydantic v2 valida el borde HTTP y genera OpenAPI
   exacto desde el código.
3. **Rendimiento ASGI:** Uvicorn ofrece latencia baja para redirecciones, que
   son el camino caliente del producto.
4. **Superficie mínima:** no se necesita ORM distinto, panel administrativo ni
   sistema de plantillas de Django.
5. **Trazabilidad:** los contratos y pruebas existentes siguen siendo válidos.

## Alternativas descartadas

- **Django + DRF:** migración destructiva, mayor superficie y reescritura de
  pruebas; no aporta valor al flujo crear → redirigir → QR.
- **Flask:** validación y OpenAPI requieren piezas adicionales.
- **Litestar:** ecosistema y familiaridad menores para el equipo.

## Consecuencias

- Se debe documentar explícitamente la diferencia frente al stack de referencia.
- La autenticación institucional futura deberá integrarse como dependencia
  FastAPI o middleware, sin acoplar el dominio.
- La generación de OpenAPI se mantiene automática; no se edita a mano.
