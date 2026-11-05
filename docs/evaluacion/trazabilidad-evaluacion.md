# Trazabilidad de la Evaluación Sumativa 1

**Proyecto:** UniShort QR - Servicio de Enlaces Académicos
**Fecha:** 2026-11-05
**Alcance:** incremento funcional sobre el MVP existente.

## 1. Fuentes de requisitos

| Fuente | Ubicación | Estado |
|--------|-----------|--------|
| Especificación de creación de enlaces | `specs/001-create-short-link/spec.md` | Disponible |
| Especificación de QR | `specs/002-generate-qr/spec.md` | Disponible |
| Contratos | `specs/001-create-short-link/contracts/`, `specs/002-generate-qr/contracts/` | Disponible |
| Constitución del proyecto | `.specify/memory/constitution.md` | Disponible |
| Guía oficial de la Evaluación Sumativa 1 | Fuera del repositorio | **Pendiente de incorporar** |

> No se inventan requisitos de la guía oficial. Los requisitos trazados son los
> que aparecen en las especificaciones del repositorio y en el enunciado
> registrado por el equipo. La guía oficial queda como fuente externa pendiente.

## 2. Requisitos funcionales y evidencia

| ID | Requisito | Implementación | Prueba / evidencia | Estado |
|----|-----------|----------------|--------------------|--------|
| FR-001 | Crear enlace corto | `POST /api/v1/links`, `services.create_short_link` | `tests/contract/test_v1_links_contract.py` | Cumplido |
| FR-002 | Validar URL `http`/`https`, host y 2048 | `domain.validate_destination_url` | `tests/unit/test_domain.py` | Cumplido |
| FR-003 | Código único | Restricción única + `repository.create_link` | `tests/unit/test_repository.py`, 10 000 códigos | Cumplido |
| FR-004 | Persistencia duradera | SQLite + `database.py` | `tests/integration/test_persistence_restart.py` | Cumplido |
| FR-005 | Devolver código, URL corta y original | `services.link_to_data`, envelope v1 | Contrato v1 | Cumplido |
| FR-006 | Rechazar entradas inválidas sin enlace | `errors.py`, `main.py`, `api/schemas.py` | Contrato v1 | Cumplido |
| FR-007 | No confirmar guardado fallido | Rollback en `repository.py` | `test_persistence_failure_rolls_back_and_raises` | Cumplido |
| FR-008 | No recopilar datos personales | `models.py` sin columnas PII | `tests/security/test_admin_access.py` | Cumplido a nivel de esquema |
| FR-009 | Límite de tasa efímero | `rate_limit.py`, `api/deps.py` | `tests/unit/test_rate_limit.py`, contrato | Cumplido |
| FR-010 | Verificación desde navegador | `frontend/index.html`, README | Verificación manual | **Parcial** |

### QR

| ID | Requisito | Implementación | Prueba / evidencia | Estado |
|----|-----------|----------------|--------------------|--------|
| QR FR-001 | Endpoint de QR | `GET /api/v1/links/{code}/qr` | `tests/contract/test_v1_links_contract.py` | Cumplido |
| QR FR-002 | PNG válido | `qr.generate_qr_png` | `tests/integration/test_qr.py` | Cumplido |
| QR FR-003 | Codificar URL corta | `services.build_short_url` | Decodificación OpenCV | Cumplido |
| QR FR-004 | Decodificable | qrcode + Pillow | `test_generated_qr_is_decodable...` | Cumplido |
| QR FR-005 | 404/410 sin imagen | `resolve_link_for_redirect` | Pruebas de QR | Cumplido |
| QR FR-006 | No contar clics al consultar QR | Solo valida estado | Revisión de código | Cumplido |
| QR FR-007 | Sin consultar destino ni PII | Generación local | Revisión de código | Cumplido |
| QR FR-008 | Tamaño configurable | `UNISHORT_QR_BOX_SIZE`, `QR_BORDER` | `tests/unit/test_config.py` | Cumplido |
| QR FR-009 | Frontend muestra/descarga | `frontend/index.html` | Revisión manual | Cumplido |

## 3. Historias de usuario

| Historia | Prioridad | Implementación | Evidencia | Estado |
|----------|-----------|----------------|-----------|--------|
| US1 Crear enlace | P1 | `POST /api/v1/links` | Contrato v1 | Cumplida |
| US2 Errores claros | P2 | Envelope, i18n, rate limit | Contrato + unitarias | Cumplida |
| US3 Código propio | P3 | Reintentos y unicidad | Repositorio + 10 000 códigos | Cumplida |
| US4 Navegador | P4 | Frontend + README | Sin sesión cronometrada | **Parcial** |
| QR US1 Obtener QR | P1 | Endpoint QR | Integración QR | Cumplida |
| QR US2 Usar QR en frontend | P2 | `frontend/index.html` | Revisión manual | Cumplida |

## 4. Criterios de éxito

| ID | Criterio | Evidencia | Estado |
|----|----------|-----------|--------|
| SC-001 | URL válida produce enlace al primer intento | Contrato | Cumplido en pruebas |
| SC-002 | 10 000 códigos sin repetición | `test_ten_thousand_codes_are_unique` | Cumplido |
| SC-003 | URL inválida recibe 4xx sin enlace | Contrato | Cumplido |
| SC-004 | Resultado en menos de 1 s (p95) | No medido | **Pendiente** |
| SC-005 | Enlaces sobreviven al reinicio | Prueba de reinicio | Cumplido |
| SC-006 | Escenarios cubiertos por pruebas | Suite | Parcial por US4 |
| SC-007 | Persona no técnica en menos de 10 min | No registrado | **Pendiente** |
| SC-008 | Cero datos personales | Inspección de esquema | Cumplido a nivel de esquema |

## 5. Decisiones de arquitectura

| ADR | Decisión | Estado |
|-----|----------|--------|
| `docs/adr/0001-fastapi-vs-django-rest-framework.md` | Mantener FastAPI | Aceptado |
| `docs/adr/0002-sqlite-desarrollo-postgresql-futuro.md` | SQLite ahora, PostgreSQL futuro | Aceptado |
| `docs/adr/0003-generacion-codigo-corto.md` | 7 caracteres sin ambigüedad | Aceptado |
| `docs/adr/0004-autenticacion-provisional-administrativa.md` | Clave administrativa provisional | Aceptado |
| `docs/adr/0005-api-versionada-envelope-errores.md` | `/api/v1` + envelope | Aceptado |

## 6. Modelado

| Artefacto | Ubicación | Estado |
|-----------|-----------|--------|
| Análisis BPMN | `docs/procesos/analisis-bpmn.md` | Completo |
| XML BPMN 2.0.2 | `docs/procesos/creacion-enlace.bpmn` | Validado como XML y referencias |
| C4 Contexto/Contenedores/Componentes | `docs/arquitectura/unishort-c4.dsl` | Completo |
| C4 Código | `docs/arquitectura/c4-codigo.puml` | Completo |
| Portal Quarto | `quarto/` | Completo; render no ejecutado (Quarto no instalado) |

## 7. Seguridad y privacidad

| Control | Evidencia | Estado |
|---------|-----------|--------|
| Validación estricta de URL | `domain.py` | Implementado |
| Rechazo de credenciales embebidas | `EmbeddedCredentialsError` | Implementado |
| Código no secuencial | `secrets.choice` | Implementado |
| Autenticación administrativa | `X-Admin-API-Key` con `compare_digest` | Implementado |
| Sin secretos en Git | `.env.example`, `.gitignore` | Implementado |
| Sin IP/User-Agent persistidos | `models.py`, pruebas de esquema | Implementado |
| Rate limit efímero | `rate_limit.py` | Implementado |
| Redirección sin cuerpo | `RedirectResponse` | Implementado |
| Errores sin trazas internas | Handler global | Implementado |

## 8. Evidencia de ejecución

```text
python -m pytest tests -q
84 passed in 1.23s

python -m pytest tests --cov=backend/app --cov-report=term-missing
84 passed; cobertura total 92.78 % (umbral 85 %; rate_limit.py 100 %)

python -m ruff check backend tests
All checks passed!

python -m ruff format --check backend tests
31 files already formatted

python -m mypy backend/app   # strict=true en pyproject.toml
Success: no issues found in 19 source files
```

- Fecha: 2026-11-05.
- Entorno: Python 3.13.14, pytest 9.1.1, ruff 0.6.9, mypy 1.11.2.
- Base de datos de pruebas: SQLite aislada.
- Sin acceso a red pública en las pruebas.
- Docker y Quarto no están instalados en este entorno: los archivos se entregan,
  pero no se ejecutaron `docker compose` ni `quarto render`.

## 9. Pendientes y riesgos

| Pendiente | Riesgo | Mitigación |
|-----------|--------|------------|
| Verificación manual US4/SC-007 | No hay evidencia de usuario no técnico | Ejecutar y registrar duración |
| SC-004 sin medición p95 | No se puede afirmar latencia | Medir con carga controlada |
| Docker/Quarto sin ejecutar | No se validó el arranque de contenedores ni el render | Ejecutar en un entorno con Docker y Quarto |
| Migración Alembic | Producción sin migraciones formales | Añadir en siguiente incremento |
| Logging JSON | Observabilidad parcial | Implementar sin PII |
| Autenticación institucional | Clave compartida provisional | OIDC cuando exista especificación |
| Guía oficial ausente | Requisitos externos no verificados | Incorporarla al repositorio |

## 10. Conclusión

El incremento cumple los requisitos funcionales de creación, unicidad,
persistencia, errores, privacidad, límite de tasa y QR, con 84 pruebas verdes,
cobertura total de 92.78 %, `ruff`/`mypy --strict` limpios y documentación de
arquitectura y procesos. Quedan pendientes explícitos de verificación manual,
medición de latencia p95, migración formal, logging JSON, validación de
Docker/Quarto y autenticación institucional; no se presentan como completados.
