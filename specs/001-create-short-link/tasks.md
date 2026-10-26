---

description: "Task list template for feature implementation"
---

# Tasks: Crear enlaces cortos (001-create-short-link)

**Input**: Design documents from `/specs/001-create-short-link/`

**Prerequisites**: [plan.md](./plan.md), [spec.md](./spec.md),
[research.md](./research.md), [data-model.md](./data-model.md),
[contracts/](./contracts/), [quickstart.md](./quickstart.md)

**Tests**: obligatorios por la constitución (Principio V): TDD rojo-verde-refactor,
cobertura ≥ 85 % sobre `src/unishort` y 100 % sobre `rate_limit.py` y
`logging_config.py`. Cada escenario de aceptación en alcance debe tener su
prueba.

**Organization**: las tareas están agrupadas por historia de usuario para poder
implementarlas y probarlas de forma independiente.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: puede ejecutarse en paralelo (archivos distintos, sin dependencias de
  tareas incompletas)
- **[Story]**: historia de usuario a la que pertenece (US1, US2, US3, US4)
- Rutas de archivo exactas en cada descripción

## Path Conventions

- **Single project**: `src/`, `tests/` en la raíz del repositorio
- Estructura concreta en [plan.md](./plan.md) > Project Structure

## Puertas humanas antes de implementar (no son tareas)

1. Aprobación de `spec.md` por mayoría del equipo (Principio I de la
   constitución).
2. Enmienda MINOR de la constitución que retire el marcador de destino de
   despliegue y ratifique el motor de datos de producción decidido
   (ver pendientes de [plan.md](./plan.md)).

## Phase 1: Setup (Infraestructura compartida)

**Purpose**: inicialización del proyecto y estructura básica

- [ ] T001 Create directory structure per plan.md (src/unishort con __init__.py y subpaquetes api/, domain/, services/, persistence/; tests/unit, tests/integration, tests/contract; docs/adr; alembic/versions)
- [ ] T002 Create pyproject.toml with project metadata, exact-pinned runtime dependencies (fastapi, pydantic, pydantic-settings, sqlalchemy, alembic, uvicorn), optional [dev] extras (pytest, pytest-cov, httpx, mypy, ruff) and src-layout package discovery in pyproject.toml
- [ ] T003 Configure ruff, mypy --strict over src/unishort, and pytest (testpaths, --cov=src/unishort, --cov-fail-under=85) in pyproject.toml
- [ ] T004 [P] Create .gitignore covering unishort.db, .env, .venv/, __pycache__/, .coverage and htmlcov/ in .gitignore
- [ ] T005 [P] Generate requirements.lock from a clean venv with `pip freeze` and record the exact command in requirements.lock header comment
- [ ] T006 [P] Create README.md skeleton with installation, execution, tests and migrations sections for Windows in README.md

---

## Phase 2: Foundational (Bloqueantes)

**Purpose**: infraestructura común que DEBE estar lista antes de cualquier historia

**⚠️ CRITICAL**: no puede comenzar trabajo de historia de usuario hasta completar esta fase

- [ ] T007 [P] Implement Settings in src/unishort/config.py with pydantic-settings and env prefix UNISHORT_, declaring database_url default "sqlite:///./unishort.db", base_url default "http://localhost:8000", rate_limit_max default 60 and rate_limit_window_seconds default 60
- [ ] T008 [P] Implement the es/en message catalog with one key per error code of contracts/errors.md in src/unishort/i18n.py
- [ ] T009 [P] Implement structured JSON logging without IP, user-agent or full destination URL plus tests/unit/test_logging_config.py at 100% coverage in src/unishort/logging_config.py
- [ ] T010 [P] Implement domain exception hierarchy with code and field attributes in src/unishort/domain/errors.py (InvalidSchemeError, InvalidHostError, EmbeddedCredentialsError, CollisionExhaustedError, PersistenceError)
- [ ] T011 Implement engine and session factory (autoflush=False, expire_on_commit=False) plus get_session dependency with yield and guaranteed close, reading Settings.database_url in src/unishort/persistence/session.py
- [ ] T012 [P] Implement ShortLink ORM model in src/unishort/persistence/models.py with short_code as "String(7) PRIMARY KEY, sin 0/O/1/l", original_url as "String(2048) NOT NULL, almacenada completa e inmodificada", created_at as "DateTime(timezone=True) NOT NULL, UTC consciente de zona" with default utc_now(), index ix_short_links_created_at and metadata naming convention pk_short_links
- [ ] T013 Configure Alembic (alembic.ini and alembic/env.py reading UNISHORT_DATABASE_URL) and write the initial reversible migration from data-model.md with upgrade creating table short_links and downgrade dropping it in alembic/versions/
- [ ] T014 [P] Implement X-Request-Id handling that accepts, generates and echoes the header in src/unishort/api/deps.py
- [ ] T015 Implement the error envelope schema and the single exception handler mapping domain errors and an overridden RequestValidationError to contracts/errors.md, resolving Accept-Language (es default, en fallback), in src/unishort/api/schemas.py and src/unishort/main.py
- [ ] T016 [P] Write tests/unit/test_domain_layer_purity.py asserting that importing unishort.domain.* does not import fastapi or sqlalchemy in sys.modules
- [ ] T017 [P] Write tests/integration/test_app_smoke.py asserting the app imports, serves /openapi.json and uses SQLite file unishort.db by default

**Checkpoint**: fundación lista; las historias pueden empezar en paralelo

---

## Phase 3: User Story 1 - Crear un enlace corto a partir de una URL válida (Priority: P1) 🎯 MVP

**Goal**: una URL válida produce un enlace corto único persistente con código, URL corta y URL original

**Independent Test**: enviar una URL válida y comprobar que la respuesta incluye el código corto, la URL corta y la URL original, y que el enlace quedó almacenado (US1.1)

### Tests for User Story 1 (TDD: escribir primero y ver fallar)

- [ ] T018 [P] [US1] Write tests/unit/test_domain_code.py asserting short codes are 7 characters, lowercase, drawn only from abcdefghijkmnpqrstuvwxyz23456789 and free of 0/O/1/l
- [ ] T019 [P] [US1] Write tests/contract/test_shorten_contract.py asserting POST /shorten returns 201 with short_code, short_url and original_url per contracts/shorten.md and echoes X-Request-Id
- [ ] T020 [P] [US1] Write tests/integration/test_create_shorten.py asserting a valid URL returns 201, the row exists in the database, and resending the same URL produces a different short_code (US1.1, US1.4)
- [ ] T021 [P] [US1] Write tests/integration/test_persistence_restart.py asserting that after disposing the engine and rebuilding the app over the same SQLite file the link still resolves to its original_url (US1.2, SC-005)

### Implementation for User Story 1

- [ ] T022 [P] [US1] Implement short code generation with secrets.SystemRandom, the alphabet constant and length 7 in src/unishort/domain/code.py
- [ ] T023 [P] [US1] Implement destination URL validation accepting only absolute http/https URLs with a non-empty host, stripping outer whitespace and rejecting embedded credentials, raising the domain exceptions in src/unishort/domain/url.py
- [ ] T024 [US1] Implement ShortenRequest with extra="forbid", url string with min_length 1 and max_length 2048, and ShortenResponse with short_code, short_url and original_url in src/unishort/api/schemas.py
- [ ] T025 [US1] Implement save in src/unishort/persistence/repository.py inserting the row and committing, rolling back on any exception
- [ ] T026 [US1] Implement the create_short_link use case validating the URL, generating the code, persisting the link and composing short_url from settings.base_url in src/unishort/services/shorten.py
- [ ] T027 [US1] Implement POST /shorten returning 201 with the three contract fields in src/unishort/api/routes.py
- [ ] T028 [US1] Wire the router in the app factory and confirm the generated OpenAPI matches contracts/shorten.md (route, 201, fields, error envelope) in src/unishort/main.py

**Checkpoint**: la historia 1 debe funcionar y probarse de forma independiente

---

## Phase 4: User Story 2 - Recibir un error claro cuando la creación no puede completarse (Priority: P2)

**Goal**: toda entrada inválida recibe un error 4xx localizado sin crear enlace; el fallo de guardado responde 5xx sin enlaces parciales; el límite de tasa responde 429

**Independent Test**: enviar entradas inválidas y provocar un fallo de guardado, comprobando en cada caso el estado, el código de error y que no se crea ningún enlace (US2.1-US2.7)

### Tests for User Story 2 (TDD: escribir primero y ver fallar)

- [ ] T029 [P] [US2] Write tests/unit/test_domain_url.py asserting rejection of empty or whitespace-only input, ftp/javascript/data schemes, missing or malformed hosts and embedded credentials, each raising its own exception type
- [ ] T030 [P] [US2] Write tests/unit/test_rate_limit.py asserting 60 requests are allowed per window, the 61st is refused, the window resets, entries expire within the TTL and different client keys are counted separately, at 100% coverage
- [ ] T031 [P] [US2] Write tests/integration/test_shorten_errors.py asserting each invalid input returns its 422 or 400 with the envelope code, field and localized message in es and en, and that no row is created (US2.1-US2.5)
- [ ] T032 [P] [US2] Write tests/integration/test_rate_limit_api.py asserting the request over the limit returns 429 rate_limit_exceeded with field null and creates no link (US2.7)
- [ ] T033 [P] [US2] Write tests/integration/test_persistence_failure.py asserting that a failing session yields 500 persistence_failure with no partial row (US2.6, FR-007)

### Implementation for User Story 2

- [ ] T034 [P] [US2] Implement the fixed-window in-memory limiter with a TTL no longer than 60 seconds, keyed by client IP that is never persisted nor associated with a stored link in src/unishort/rate_limit.py
- [ ] T035 [US2] Implement the rate-limit dependency so the 429 is decided before the request body is validated, in src/unishort/api/deps.py
- [ ] T036 [US2] Map the domain exceptions to 400 and the Pydantic failures to 422 with codes invalid_payload and url_too_long through the single handler with i18n messages in src/unishort/main.py and src/unishort/i18n.py
- [ ] T037 [US2] Map a failed commit to 500 persistence_failure with a full rollback and no success response in src/unishort/services/shorten.py

**Checkpoint**: las historias 1 y 2 deben funcionar de forma independiente

---

## Phase 5: User Story 3 - Confiar en que cada enlace tiene un código corto propio (Priority: P3)

**Goal**: ningún código emitido se repite y una colisión se resuelve sin sobrescribir enlaces existentes

**Independent Test**: crear una ronda numerosa de enlaces, incluidos dos con la misma URL original, y comprobar que todos los códigos emitidos son distintos (US3.1-US3.3)

### Tests for User Story 3 (TDD: escribir primero y ver fallar)

- [ ] T038 [P] [US3] Write tests/unit/test_code_uniqueness.py asserting 10000 successive generated codes contain no repetition (US3.3, SC-002)
- [ ] T039 [P] [US3] Write tests/integration/test_uniqueness.py asserting that an injected generator that repeats an existing code causes a retry without overwriting the stored link, and that exhausting the retries returns 409 collision_unresolved (US3.2)

### Implementation for User Story 3

- [ ] T040 [US3] Implement collision retry requesting a fresh code up to 10 times on IntegrityError and raising CollisionExhaustedError after that in src/unishort/persistence/repository.py
- [ ] T041 [US3] Map CollisionExhaustedError to 409 with the envelope in src/unishort/main.py

**Checkpoint**: las cuatro historias deben funcionar de forma independiente

---

## Phase 6: User Story 4 - Comprobar la funcionalidad desde el navegador (Priority: P4)

**Goal**: una persona evaluadora crea y verifica un enlace desde el navegador sin escribir código

**Independent Test**: seguir únicamente las instrucciones de arranque en un navegador y comprobar que se puede crear un enlace y ver su respuesta (US4.1, US4.2)

### Implementation for User Story 4

- [ ] T042 [US4] Add the browser verification steps for POST /shorten in /docs, the expected 201 example and the invalid-input example to README.md linking quickstart.md
- [ ] T043 [US4] Follow quickstart.md end to end in a clean environment, correcting any discrepancy until a non-technical person finishes in under 10 minutes (SC-007)

---

## Phase 7: Polish & Cross-Cutting Concerns

**Purpose**: mejoras y documentación que afectan a varias historias

- [ ] T044 [P] Write docs/adr/0001-stack-tecnologico.md from research.md with context, decision, alternatives and consequences
- [ ] T045 [P] Write docs/adr/0002-motor-de-datos-y-despliegue.md from research.md R-11 including SQLite for development, PostgreSQL deferred for production and the portability rules
- [ ] T046 [P] Write docs/adr/0003-generacion-codigo-corto.md from research.md R-02
- [ ] T047 [P] Write docs/adr/0004-limite-tasa-efimero.md from research.md R-01
- [ ] T048 [P] Write docs/adr/0005-contrato-errores-localizacion.md from research.md R-04
- [ ] T049 [P] Inspect the unishort.db schema and captured logs asserting no IP, cookie, session identifier or personal data column exists (FR-008, SC-008) and record the finding in the feature folder
- [ ] T050 Run pytest with coverage, ruff check, ruff format --check and mypy --strict, fixing violations until the 85% and 100% thresholds and a clean static check are met
- [ ] T051 [P] Reconcile contracts/shorten.md and contracts/errors.md with the generated OpenAPI and update both change logs if the implementation drifted
- [ ] T052 Confirm every task file has no unresolved template markers and that README, quickstart and contracts match the shipped behaviour (Definición de Terminado)

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: sin dependencias; puede empezar de inmediato
- **Foundational (Phase 2)**: depende del Setup; BLOQUEA todas las historias
- **User Stories (Phase 3-6)**: todas dependen del Foundational
  - pueden avanzar en paralelo si hay capacidad, o en orden de prioridad (P1 → P2 → P3 → P4)
- **Polish (Phase 7)**: depende de las historias elegidas

### User Story Dependencies

- **User Story 1 (P1)**: arranca tras Foundational; sin dependencias de otras historias
- **User Story 2 (P2)**: arranca tras Foundational; se integra con US1 pero es comprobable por sí sola (añade los caminos de error)
- **User Story 3 (P3)**: arranca tras Foundational; añade la ruta de colisión sobre el repositorio de US1
- **User Story 4 (P4)**: requiere US1 (y conviene US2 para verificar los errores en el navegador)

### Within Each User Story

- Tests primero, observándolos fallar antes de la implementación
- Dominio antes de servicios, servicios antes de endpoints
- Endpoint antes de la integración y del cableado
- Historia completa antes de pasar a la siguiente prioridad

### Parallel Opportunities

- Todas las tareas marcadas [P] dentro de una fase, por usar archivos distintos
- Tras el Foundational, las historias 1, 2 y 3 pueden avanzar en paralelo
- Los tests de una misma historia marcados [P] pueden lanzarse juntos
- Los ADR (T044-T048) son independientes entre sí

---

## Parallel Example: User Story 1

```text
Task: "Write tests/unit/test_domain_code.py ..."              (T018)
Task: "Write tests/contract/test_shorten_contract.py ..."     (T019)
Task: "Write tests/integration/test_create_shorten.py ..."    (T020)
Task: "Write tests/integration/test_persistence_restart.py"   (T021)

Task: "Implement short code generation in src/unishort/domain/code.py"  (T022)
Task: "Implement URL validation in src/unishort/domain/url.py"          (T023)
```

---

## Implementation Strategy

### MVP First (solo User Story 1)

1. Completar Phase 1: Setup
2. Completar Phase 2: Foundational (CRITICAL)
3. Completar Phase 3: User Story 1
4. **PARAR y VALIDAR**: probar US1 de forma independiente
5. Demostrar si está listo

### Incremental Delivery

1. Setup + Foundational → fundación lista
2. US1 → probar por sí sola → MVP
3. US2 → probar por sí sola → errores claros
4. US3 → probar por sí sola → unicidad garantizada
5. US4 → verificación desde el navegador

### Parallel Team Strategy

1. El equipo completa Setup + Foundational
2. Después: desarrollador A en US1, B en US2, C en US3
3. Cada historia termina e integra de forma independiente

---

## Notes

- [P] = archivos distintos, sin dependencias de tareas incompletas
- La etiqueta [Story] traza la tarea a su historia
- Comprometer tras cada tarea o grupo lógico con Conventional Commits
  referenciando el identificador de la funcionalidad (por ejemplo
  `feat(short-link): add code generation (001)`)
- Parar en cada checkpoint para validar la historia de forma independiente
- Cambios que afecten a la privacidad (T049) requieren revisión de dos personas
