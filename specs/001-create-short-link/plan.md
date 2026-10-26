# Implementation Plan: Crear enlaces cortos (Feature 1)

**Branch**: `001-create-short-link` | **Date**: 2026-10-21 | **Spec**: [spec.md](./spec.md)

**Input**: Feature specification from `/specs/001-create-short-link/spec.md`

**Note**: This plan is filled in by the `/speckit.plan` command; its definition describes the execution workflow. No source code has been written yet: este documento y sus artefactos de diseño son la salida de la Fase 0 y Fase 1.

## Summary

La especificación pide una operación única de creación de enlaces cortos: el
usuario envía una URL original, el sistema la valida (`http`/`https`, absoluta,
sin credenciales, máximo 2.048 caracteres), genera un código corto único de
7 caracteres, persiste la relación código ↔ URL en SQLite y devuelve
`short_code`, `short_url` y `original_url`. Las entradas inválidas devuelven
un error 4xx localizado sin crear enlace, y un fallo de guardado nunca se
presenta como éxito.

Enfoque técnico: API REST en FastAPI con separación en cuatro capas
(`api` → `services` → `domain`, y `services` → `persistence`), validación en el
borde con Pydantic v2 estricto, persistencia con SQLAlchemy 2.x sobre SQLite y
migraciones con Alembic. El código corto se genera con un alfabeto de 32
caracteres sin ambigüedad y reintento ante colisión, con la unicidad garantizada
por una restricción a nivel de base de datos. El límite de tasa es efímero en
memoria y no se registran direcciones IP, conforme a la constitución.

## Technical Context

**Language/Version**: Python 3.11+ (mínimo del proyecto: `Python >= 3.11`)

**Primary Dependencies**: `fastapi >= 0.110`, `pydantic >= 2.7`,
`pydantic-settings` (configuración por entorno), `sqlalchemy >= 2.0`,
`alembic >= 1.13`, `uvicorn[standard]` (servidor ASGI). Dependencias de
desarrollo y prueba: `pytest >= 8.0`, `httpx >= 0.27`, `pytest-cov`, `mypy`,
`ruff`.

**Storage**: SQLite 3.x en archivo local (`unishort.db`) a través del ORM de
SQLAlchemy 2.x, con esquema versionado por Alembic. Es el único motor
implementado y probado en esta fase. El motor se elige por configuración
(`UNISHORT_DATABASE_URL`), con tipos portables y sin SQL en crudo, de modo que
PostgreSQL pueda ocupar su lugar en producción sin reescribir el dominio
(decisión de despliegue: [research.md](./research.md) R-11 y
`docs/adr/0002-motor-de-datos-y-despliegue.md`).

**Testing**: `pytest` con el cliente de pruebas de FastAPI (`httpx`), fixtures
con base de datos SQLite aislada e in-memory por prueba, como exige la
constitución. Cobertura mínima 85 % sobre `src/unishort` y 100 % sobre
`rate_limit` y `logging_config` (constitución > Pruebas Automatizadas).
Verificación estática: `ruff` y `mypy --strict`.

**Target Platform**: Windows 10/11 para desarrollo (PowerShell, `py -3.11`,
rutas relativas de SQLite) con servidor ASGI Uvicorn en
`127.0.0.1:8000 --no-access-log`. Destino de producción decidido y
diferido: contenedor con Uvicorn detrás de un proxy con HTTPS y PostgreSQL como
motor de datos, sin implementarlo en esta fase.

**Project Type**: web-service (API REST con OpenAPI generado por FastAPI).

**Performance Goals**: creación con p95 < 150 ms en la capa de aplicación
(constitución); el usuario ve el resultado en < 1 s p95 (SC-004); el modelo de
datos soporta 1.000.000 de enlaces.

**Constraints**: URL máxima de 2.048 caracteres; solo esquemas `http`/`https`
sin credenciales embebidas; límite de tasa sobre la creación; cero datos
personales de quien crea el enlace; mensajes de error en `es` y `en`;
identificadores del código en inglés y docstrings en español; `mypy --strict`
y `ruff` sin errores; funciones de ≤ 50 líneas y ≤ 6 ramas.

**Scale/Scope**: 1 endpoint (`POST /shorten`), 1 entidad persistente, 10 FR,
4 historias de usuario, 17 escenarios de aceptación, 8 criterios de éxito.
Fuera de alcance: QR, redirecciones, estadísticas y autenticación.

**Unknowns resolved in Phase 0** (ver [research.md](./research.md)): los cuatro
marcadores de aclaración iniciales quedan cerrados — R-01 política de límite de
tasa, R-02 generación y longitud del código corto, R-03 base pública de
`short_url`, R-04 formato y localización de los errores.

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| # | Exigencia de la constitución | Estado | Evidencia / medida de cumplimiento |
|---|------------------------------|--------|------------------------------------|
| 1 | I. Especificación Antes que Código (NO NEGOCIABLE) | PASS | `spec.md` con 4 historias priorizadas y 17 escenarios Given/When/Then; orden `spec.md` → `plan.md` → `tasks.md` respetado. **Pendiente antes de implementar**: aprobación de `spec.md` por mayoría del equipo (Principio I). |
| 2 | II. Código Mantenible y Tipado | PASS | `mypy --strict` y `ruff` obligatorios; capas con dependencias en un solo sentido; funciones ≤ 50 líneas y ≤ 6 ramas; ajustes con `pydantic-settings`; sin secretos en el repositorio; un único manejador de errores. |
| 3 | III. Validación de Entradas y Contrato de API | PASS | Modelos Pydantic v2 con `extra="forbid"` y defaults explícitos en la frontera; estados 422/400/409/429/500 según el caso (el 404 no aplica: esta feature no resuelve códigos); validación de URL (esquema, host, sin credenciales, ≤ 2.048); el servidor nunca descarga el destino; contrato en `contracts/shorten.md` y `contracts/errors.md` antes de implementar. |
| 4 | IV. Protección de Datos y Privacidad (NO NEGOCIABLE) | PASS | Ninguna tabla ni log conserva IP o PII; Uvicorn con `--no-access-log`; limitador de tasa en memoria con TTL ≤ 60 s, no persistido ni asociado a enlaces; sin cookies, analítica de terceros ni huella digital. |
| 5 | V. Pruebas Automatizadas (NO NEGOCIABLE) | PASS | `pytest` con `tests/unit`, `tests/integration`, `tests/contract`; TDD rojo-verde-refactor; cobertura ≥ 85 % y 100 % en `rate_limit` y `logging_config`; BD SQLite aislada por prueba; sin acceso a red pública; CI ejecuta `ruff` + `mypy` + suite. |
| 6 | Stack Tecnológico | PASS | La decisión del usuario coincide exactamente con el stack ratificado (Python, FastAPI, Pydantic, SQLAlchemy, SQLite, pytest, Alembic, Uvicorn). Versiones fijadas en `pyproject.toml` y bloqueadas en lockfile. |
| 7 | Convenciones de Código | PASS | Identificadores en inglés (PEP 8), docstrings y comentarios en español (estilo NumPy), comentarios que explican el porqué, sin lógica duplicada, configuración por variables de entorno. |
| 8 | Modelo de Datos y Persistencia | PASS con una excepción justificada | Unicidad por restricción de la base de datos (no solo en la aplicación); timestamps en UTC conscientes de zona; migración inicial de Alembic reversible; escrituras en transacción con reversión ante fallo. Excepción: índice sobre `expires_at` → ver Complexity Tracking. |
| 9 | Rendimiento y Escalabilidad | PASS | Objetivo de creación p95 < 150 ms; modelo de datos con índice sobre `short_code` y `created_at`; 1.000.000 de enlaces sin cambio de modelo; límite de tasa sobre la creación. |
| 10 | Documentación | PASS | `README` (instalación, ejecución, pruebas, migraciones), carpeta `docs/adr/` con 5 ADR (`0001-stack-tecnologico`, `0002-motor-de-datos-y-despliegue`, `0003-generacion-codigo-corto`, `0004-limite-tasa-efimero`, `0005-contrato-errores-localizacion`), OpenAPI generado por FastAPI (no falseado a mano), contratos en `contracts/` con registro de cambios. |
| 11 | Accesibilidad e Internacionalización | PASS parcial por alcance | Mensajes de error en `es` y `en` (requisito asumido en el spec); conjunto de códigos sin ambigüedad y normalizado a una sola caja. Los puntos de interfaz de usuario y QR no aplican en esta iteración. |
| 12 | Flujo de Desarrollo (puertas A, B, C) y Revisión | PASS | Esta sección es la Puerta A; `/speckit.tasks` y la implementación ejecutan la Puerta B; `/speckit.analyze` ejecuta la Puerta C. Revisión por ≥ 1 miembro distinto del autor y aprobación por mayoría. |
| 13 | Gobernanza | PASS | La constitución no se edita en esta fase: la decisión de destino de despliegue y motor de producción se registra en el plan y se elevará como enmienda MINOR para su aprobación por mayoría. |

**Gate A resultado**: 13 PASS, 0 FAIL, 1 excepción justificada en la sección
*Complexity Tracking* (final del documento). La fase de investigación y diseño
puede continuar.

### Re-evaluación post-diseño (tras Fase 1)

Los artefactos de la Fase 1 (`research.md`, `data-model.md`, `contracts/`,
`quickstart.md`) se revisaron contra los 13 puntos anteriores:

- **Sin nuevos incumplimientos**: el diseño añade restricciones de la
  constitución, no las relaja (unicidad en la base de datos, UTC, Alembic
  reversible, límite de tasa efímero, logs sin IP, cobertura del 100 % en los
  módulos de privacidad).
- **El destino de despliegue quedó decidido** (PostgreSQL tras un contenedor
  con HTTPS) y registrado en [research.md](./research.md) R-11, sin
  implementarlo: esta fase solo usa SQLite. No se añade ninguna dependencia de
  ejecución nueva, así que no hay nada que justificar en esta tabla.
- **La excepción de `expires_at` se mantiene** con la misma justificación; no
  aparece ningún nuevo supuesto que la sustituya.
- **Pendientes explícitos antes de la Puerta B** (no bloquean esta fase):
  1. Aprobación de `spec.md` por mayoría del equipo (Principio I).
  2. Enmienda MINOR de la constitución: retirar el marcador de destino de
     despliegue y ratificar el motor de datos de producción decidido.
  3. Escritura de los 5 ADR listados en *Documentación* en `docs/adr/` — las
     decisiones ya están documentadas en `research.md` y deben promoverse.
  4. Actualización del `README` con instalación, ejecución, pruebas y
     migraciones en Windows.

## Project Structure

### Documentation (this feature)

```text
specs/001-create-short-link/
├── spec.md                 # especificación (entrada de esta fase)
├── plan.md                 # este archivo
├── research.md             # Fase 0: decisiones y alternativas
├── data-model.md           # Fase 1: entidad, campos, reglas
├── quickstart.md           # Fase 1: guía de validación ejecutable
├── checklists/
│   └── requirements.md     # calidad de la especificación
└── contracts/              # Fase 1: contratos de interfaz
    ├── shorten.md          # contrato de POST /shorten
    └── errors.md           # envolvente de errores compartida
```

`tasks.md` se genera con `/speckit.tasks`, no en esta fase.

### Source Code (repository root)

```text
pyproject.toml              # metadatos, dependencias, ruff, mypy, pytest
README.md                   # instalación, ejecución, pruebas, migraciones
alembic.ini                 # configuración de Alembic
alembic/
├── env.py
└── versions/               # migración inicial del esquema
docs/
└── adr/                    # 0001 stack, 0002 motor de datos y despliegue,
                            # 0003 generación de código, 0004 límite de tasa,
                            # 0005 contrato de errores
src/
└── unishort/
    ├── __init__.py
    ├── main.py             # factoría de la aplicación y composición
    ├── config.py           # ajustes (pydantic-settings, variables UNISHORT_*)
    ├── i18n.py             # catálogo de mensajes es/en
    ├── rate_limit.py       # limitador efímero en memoria (sin persistir IP)
    ├── logging_config.py   # logs estructurados sin IP ni URL completas
    ├── api/
    │   ├── routes.py       # POST /shorten
    │   ├── schemas.py      # modelos Pydantic de entrada y salida
    │   └── deps.py         # dependencias: sesión, ajustes, límite, request-id
    ├── domain/
    │   ├── url.py          # reglas de la URL destino (valor puro)
    │   ├── code.py         # reglas y generación del código corto (valor puro)
    │   └── errors.py       # excepciones de dominio (sin FastAPI ni SQLAlchemy)
    ├── services/
    │   └── shorten.py      # caso de uso: crear enlace
    └── persistence/
        ├── session.py      # motor, sesión y dependencia de inyección
        ├── models.py       # modelo ORM ShortLink
        └── repository.py   # guardado, unicidad y reintento ante colisión
tests/
├── conftest.py             # app, BD in-memory por prueba, fixtures
├── unit/
│   ├── test_domain_url.py
│   ├── test_domain_code.py
│   ├── test_rate_limit.py
│   └── test_logging_config.py
├── integration/
│   ├── test_create_shorten.py
│   ├── test_uniqueness.py
│   └── test_persistence_restart.py
└── contract/
    └── test_shorten_contract.py
```

**Structure Decision**: única aplicación Python con layout `src/` y cuatro
capas. Dependencias en un solo sentido: `api` → `services` → `domain`, y
`services` → `persistence`. `domain` no importa FastAPI ni SQLAlchemy, lo que
permite probarlo de forma unitaria sin base de datos. `persistence` y `api` se
componen únicamente en `main.py`.

## Complexity Tracking

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| Índice sobre `expires_at` (constitución > Modelo de Datos y Persistencia) no se crea en esta iteración. | El campo no existe porque la expiración queda fuera de alcance de la Feature 1; crear una columna o un índice sin consumidores rompe *Simplicity & Scope Control*. | Añadir `expires_at` preventivamente se descartó: habría que migrar, probar y mantener una capacidad muerta. Se añadirá junto con la funcionalidad que la use, en la misma migración. |
