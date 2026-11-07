# Auditoría final contra la rúbrica oficial — UniShort QR

Fecha: **2026-11-06, America/Guayaquil**. Fuente principal:
[PDF oficial de 11 páginas](../../Asignaci%C3%B3n_Y_Rubrica_Evaluaci%C3%B3n_Sumativa_1.pdf).
Se leyó íntegramente su texto mediante pypdf, con salida UTF-8. No quedaron páginas
sin contenido textual verificable. No se hizo render visual: Poppler no está disponible.
Los descriptores de la rúbrica están en pp. 9–10; la finalización en pp. 10–11.

Esta auditoría revisa el árbol local con cambios, **no solo HEAD**. Rama conservada:
feature/panel-administrativo; HEAD 543701cb62a644f270c7d6344386f5f4a23ea6bf.
El panel, el PDF y documentos recibidos ya contenían cambios sin commit. Se hizo
una instantánea de 161 archivos antes de editar, con manifiesto de hashes en
.verification/rubrica-baseline-582b9471dbd54604bda13f74e19c19d5. No commits/pushes.

## Lectura y contradicciones resueltas

- PDF pp. 3–4: stack de referencia y justificación de tecnologías adicionales.
  Se conserva FastAPI/SQLAlchemy/SQLite mediante ADR 0001/0002, sin atribuir
  aprobación docente de esa alternativa. PDF p. 8 no exige reconstruir el proyecto.
- PDF pp. 4–5: errors:null es referencia; se documenta errors:[] consistente en
  v1 y lista de errores en fallo. Se conservan clientes. JSON heredado plano no es
  excepción HTTP: queda identificado como compatibilidad/deuda, ADR 0005.
- Los documentos previos que decían «PDF ausente» se actualizaron o se marcaron
  históricos; no constituyen la fuente vigente de esta auditoría.
- El BPMN recibido ya separa crear/QR/redirigir/administrar. Su análisis y Quarto
  aún decían «generar PNG al crear»; se corrigieron para representar el software real.
- C4 excluye OIDC/proxy futuros de la vista actual, incorpora visitante/destino
  y refleja que el navegador sigue Location; el backend no descarga el destino.
- PDF pp. 8/10 exige evidencia individual y declaración de IA: se añadieron
  instrucciones y una declaración del apoyo observado, sin escribir reflexiones
  ni atribuciones personales ficticias.

## Matriz de cumplimiento

Estados: **Cumplido y verificado**, **Implementado, pendiente de verificación**,
**Pendiente**, **No aplicable, con justificación**. Las pruebas automáticas no
equivalen a una aprobación del equipo, inspección visual, carga o producción.

| Criterio | Requisito específico / PDF | Estado real | Archivo que lo implementa | Prueba que lo verifica | Documento que lo respalda | Evidencia para el docente | Pendiente o riesgo residual |
|---|---|---|---|---|---|---|---|
| 1 | Problema, contexto, actores, alcance, restricciones y riesgos (p. 2) | Cumplido y verificado | specs/001–003; docs/evaluacion/contexto-y-trazabilidad.md | Contratos, dominio, integración admin; cotejo documental | Contexto y trazabilidad; seguridad-y-riesgos.md | Relacionar un actor con su flujo y necesidad | Contexto académico, sin patrocinio ni estudio institucional acreditado. |
| 1 | RF/RNF, historias y aceptación trazable (p. 2) | Cumplido y verificado | specs/001-create-short-link, 002-generate-qr, 003-admin-dashboard | tests/unit, integration, contract, security; admin.test.mjs | spec/plan/tasks/contracts y matriz de capas | Mostrar requisito → petición → servicio → SQL → respuesta → prueba | SC-004 visual, SC-007 persona no técnica y revisión manual pendientes. |
| 1 | Constitution, specify, clarify, plan, tasks (p. 2) | Implementado, pendiente de verificación | .specify; specs; clarificaciones-y-desviaciones.md | checklists y evidencia de archivos; no se simula ejecución CLI | Plan de auditoría y clarificaciones | Abrir documentos y explicar decisiones | Clarificaciones retrospectivas; comandos, ratificación y firmas no acreditados. |
| 1 | Análisis previo y BPMN 2.0.2 con infinitivos (p. 3) | Implementado, pendiente de verificación | docs/procesos/analisis-bpmn.md; creacion-enlace.bpmn; scripts/build_process_models.py | 3 tests en test_documentation_models.py: nombres, DI, referencias, orden y alcance | quarto/procesos.qmd | Cuatro procesos editables; explicar creación sin PNG | Validación XSD/semántica completa y apertura visual en modelador no realizadas. |
| 1 | C1/C2/C3 actuales y C4 código UML (p. 3) | Implementado, pendiente de verificación | unishort-c4.dsl; c4-codigo.puml | Revisión de rutas, imports y funciones frente a fuentes; sin parser de diagramas | quarto/arquitectura.qmd | Personas/sistema, contenedores, componentes y módulos/clases con relaciones | Render Structurizr/PlantUML y comprobación visual pendientes; Mermaid es síntesis. |
| 1 | Decisiones tecnológicas justificadas (pp. 3–4) | Cumplido y verificado | docs/adr/0001–0006 y 0007 | Implementación, tipos, contrato y pruebas | ADR 0001, 0002, 0004, 0005 | Explicar continuidad FastAPI y SQLite para este incremento | El docente decide admisibilidad; PostgreSQL/OIDC no se afirman implementados. |
| 2 | Flujo funcional extremo a extremo (pp. 7–9) | Cumplido y verificado | api/v1.py → services.py → domain.py/repository.py → SQLite | verify_runtime.py; contratos; integración de creación/QR/reinicio | Contratos 001/002/003 y contexto-y-trazabilidad | Crear enlace, decodificar PNG, redirigir, consultar visitas y editar estado | HTTP real loopback; aceptación visual y carga concurrente no acreditadas. |
| 2 | Recursos, /api/v1, métodos, códigos y validación (p. 4) | Cumplido y verificado | api/v1.py, api/schemas.py, main.py | test_v1_links_contract, test_regressions, admin contracts | quarto/api.qmd; ADR 0005 | Swagger y casos 201/400/401/403/404/409/410/422/429/500/503 | Legacy conserva 200/deduplicación y no sigue toda la arquitectura nueva. |
| 2 | Envelope consistente y excepciones (pp. 4–5) | Cumplido y verificado | api/envelope.py; handlers; modelos de respuesta | Contratos y regresiones de framework/errores | ADR 0005 y contracts/errors.md | Cinco claves v1/health; [] en éxito, lista en error; PNG/307 sin envelope | JSON heredado plano/detail es deuda de compatibilidad explícita; podría afectar interpretación estricta. |
| 2 | OpenAPI exacto y panel administrativo | Cumplido y verificado | FastAPI app.openapi; scripts/render_portal.py; admin.mjs | test_documentation_export; contratos OpenAPI; 19 pruebas JS | admin.md y quarto/administracion.qmd | openapi.json generado con BD temporal; panel usa API real | Render visual del panel pendiente; JSON exportado no ejecuta interacciones de navegador. |
| 2 | 204/304 o endpoints artificiales para la rúbrica | No aplicable, con justificación | No hay operación que necesite estos estados | No se fuerzan cuerpos JSON en PNG/307 | ADR 0005, contrato de redirección/QR | Explicar representaciones HTTP según cada operación | No añadir funciones para aparentar cobertura de estados irrelevantes. |
| 3 | Autenticación/autorización pertinente (p. 5) | Cumplido y verificado | api/deps.py, rutas protegidas; admin.mjs | tests/security, admin contracts, JS 401/403/503/logout | ADR 0004; seguridad-y-riesgos.md | Sin clave no se lista ni modifica; backend valida cada operación | Clave compartida sin roles, MFA, identidad ni auditoría por persona. |
| 3 | Secretos, memoria, caché y errores seguros (p. 5) | Cumplido y verificado | config.py repr=False; logging_config; main.py; admin.mjs | test_settings_representation_never_exposes_admin_key; logging; JS | Seguridad y guía Windows | Mostrar lectura oculta y explicación de no-store; nunca revelar la clave | No registrar model_dump de configuración; no se afirma auditoría forense de todo Git. |
| 3 | XSS, inyección, URLs, tasa y privacidad (pp. 4–5/7) | Cumplido y verificado | DOM seguro/CSP; dominio; SQL parametrizado; limitador | Dominio, queries literales, rate_limit, security, JS | Modelo de riesgos y ADR | Rechazar entrada inválida, comprobar búsqueda literal y 429 | Abuso de enlaces, Host en legacy, límite por proceso, URLs con datos sensibles; HTTPS remoto pendiente. |
| 3 | Modularidad, cohesión, bajo acoplamiento y SOLID pertinente (p. 4) | Cumplido y verificado | API/servicios/dominio/repositorio/configuración | mypy estricto, Ruff, pruebas aisladas por capa | C4/UML; contexto; ADR | Dominio sin FastAPI/SQLAlchemy; inyección de sesión y reloj/generador | Legacy conserva acceso directo ORM; no se declara cumplimiento absoluto de todas las reglas constitucionales. |
| 3 | Identidad institucional nueva | No aplicable, con justificación | No implementada | La clave provisional está probada | ADR 0004; límite explícito de la solicitud | Explicar su carácter académico | No ampliar alcance ni crear integración institucional ficticia. |
| 4 | Unitarias, integración, API, reglas y seguridad (p. 5) | Cumplido y verificado | tests/; scripts/verify_frontend.mjs | **148 Python, 19 JS**, regresión pública JS y HTTP real aprobados | README, esta auditoría | Ejecutar comandos y casos de aceptación relevantes | DOM simulado no prueba render ni teclado real. |
| 4 | Cobertura y análisis estático reproducibles | Cumplido y verificado | pyproject.toml; configuración de herramientas | **95,22 %**, umbral 85 %; Ruff; mypy sin errores | Guía Windows y resultados abajo | Reporte term-missing y comandos | Un aviso de deprecación AnyIO/Starlette; no es fallo. |
| 4 | Migraciones, persistencia y conservación | Cumplido y verificado | alembic 0001–0003; repository; database | test_migrations; restart; verify_database_copy | README, ADR 0002 y datos abajo | Copia migrada: 9 registros e integrity_check OK | Originales intactos; no se probó PostgreSQL ni restauración de producción. |
| 4 | SC-004 visual y SC-007 con persona no técnica | Pendiente | Frontend implementado | No hay sesión visual/cronometraje nueva | spec 001; tasks 002/003; guion de demostración | Registrar demostración real, no reconstruir evidencia | Criterios de aceptación pendientes; no confundir p95 HTTP con presentación visual. |
| 5 | Preparación/ejecución desde fuentes y dependencias (pp. 6–7) | Cumplido y verificado | README; locks; verify_clean_copy.py | pip check; copia sin BD/.env/.git/.venv, suite y JS; instalación de lock aprobada en CI publicado | ejecucion-windows-y-entrega.md | Ejecutar desde copia y usar BD temporal | Se reutilizaron dependencias locales; instalación Windows desde cero no repetida. |
| 5 | Quarto como portal, OpenAPI y documentación (p. 6) | Implementado, pendiente de verificación | quarto/; render_portal.py; PDF/OpenAPI exportados a sources | Preparación y verify_docs; exportación aislada probada | quarto/auditoria.qmd y guía Windows | Fuentes coherentes y comando de render exacto | Quarto ausente: no hay render final ni enlace publicado del portal de esta entrega. |
| 5 | Docker e inicialización reproducible (pp. 6–7) | Implementado, pendiente de verificación | Dockerfile; docker-compose.yml; Nginx | Revisión estática y YAML; migraciones y health probados fuera de Docker | Guía Windows, README | Proyecto/volumen de demo independiente; config --quiet | Docker ausente: no se ejecutaron build, Compose ni healthchecks de contenedores actuales. |
| 5 | Observabilidad mínima (p. 7) | Cumplido y verificado | logging_config.py; servicios; /health; request IDs | Logging al 100 %, health y errores probados | Seguridad, README y API | Logs de operaciones sin destinos/IP ni claves; /health consulta BD | No equivale a monitoreo de producción. |
| 5 | GitHub Actions real y separación de evidencias | Cumplido y verificado | .github/workflows/quality.yml | Run **42091635246**, quality success para **543701c**, evento push | Consulta pública autorizada y enlace abajo | Ver ejecución y pasos de pip/pytest/Ruff/mypy/JS/documentación | No incluye panel ni auditoría locales; pendiente CI del SHA final publicado. |
| 5 | Ramas, PR, revisión y contribución (pp. 5–6/8) | Implementado, pendiente de verificación | Historia Git; rama feature; PR #2 fusionado y aprobado | Consulta remota de PR/revisión; git log/shortlog | CONTRIBUTING.md | PR de Martina y aprobación de vicfer-nando | Panel/auditoría sin commit/PR; equivalencia simplificada a GitFlow documentada, no historia fabricada. |
| 5 | Declaración IA y evidencia/reflexión individual (pp. 8/10) | Implementado, pendiente de verificación | uso-ia-y-contribucion.md | Evidencia de conversación y comandos; sin prueba de reflexión personal | Declaración y campos exigidos por el PDF | Cada integrante explicar cambios, decisión, pruebas y reflexión | Falta completar/validar aportes personales y su explicación por cada estudiante. |
| 5 | Enlaces EVA, documentación generada y demostración (pp. 7–8) | Pendiente | Repositorio público existente; guía preparada | PR/CI antiguos verificados; entrega EVA no observada | Guion Windows y apartado de intervención humana | Publicar cambios autorizados y facilitar enlaces al docente | No se presentó EVA, publicó portal ni realizó demostración en nombre del equipo. |

## Resultados ejecutados

- Línea base recibida: **145 Python**, 95,22 %, 19 JS. Los dos tests BPMN recibidos
  explican la diferencia frente al informe anterior de 143; no eran pruebas fallidas.
- Final: **148 Python aprobadas**, cero fallidas/omitidas; cobertura **95,22 %**
  (896/941 sentencias), umbral 85 % intacto. Tres casos añadidos en esta auditoría:
  representación segura de Settings, alcance/orden BPMN y exportación OpenAPI aislada.
- El caso Settings se observó fallando antes de corregir repr=False; el caso
  exportación falló antes de añadir export_openapi. No se alteraron aserciones para ocultar defectos.
- **19 pruebas JavaScript** y regresión pública verify_frontend.mjs aprobadas.
- Ruff check y formato aprobados en **54 archivos**; mypy estricto sin errores en **20 módulos**.
- pip check: sin dependencias rotas. Copia limpia de fuentes comprobada con pytest
  y JS, sin bases ni .env ni .git ni .venv copiados. Reutiliza las dependencias actuales.
- Recorrido TCP real: API/frontend, módulo .mjs, autenticación, resumen/filtros,
  QR decodificado, CORS, estado/caducidad y persistencia tras reinicio aprobados.
  p95 loopback observado: **9,64 ms** creación y **7,82 ms** redirección,
  100 muestras por operación, concurrencia 1, SQLite temporal; sin afirmación de carga/SC-004 visual.
- Alembic sobre copia de unishort.db: **0003, 9 registros conservados**, integridad OK.
- Quarto/Docker no encontrados en PATH ni ubicaciones habituales. Java existe,
  pero no se dispone de ejecutable/jar de PlantUML o Structurizr verificado.
  No hubo instalaciones, publicación ni operaciones destructivas.
- Preparación del portal y comprobación de **61 fuentes** UTF-8, enlaces, YAML
  y referencias BPMN aprobadas. El host del navegador volvió a informar que no
  está disponible el 2026-11-06; no se acreditó una nueva prueba visual.

Comandos y pasos reproducibles: [guía Windows y entrega](ejecucion-windows-y-entrega.md).
Preparar Quarto ahora también exporta el OpenAPI real en un subproceso con SQLite
temporal, probado frente a una variable DATABASE_URL que no debía tocarse.

### GitHub verificado en lectura autorizada

Repositorio público: [UniShort QR](https://github.com/vicfer-nando/Unishort-QR-Servicio-De-Enlaces-Academicos).
[PR #2](https://github.com/vicfer-nando/Unishort-QR-Servicio-De-Enlaces-Academicos/pull/2):
fusionado desde feature/martina, un commit 8df95a3; revisión APPROVED de vicfer-nando
registrada el 2026-11-05 13:59:35 UTC. Es una contribución real previa, no la del panel.

[Actions run 42091635246](https://github.com/vicfer-nando/Unishort-QR-Servicio-De-Enlaces-Academicos/actions/runs/42091635246):
completed/success, push, SHA 543701cb62a644f270c7d6344386f5f4a23ea6bf; trabajo quality
aprobó instalación de lock, pytest/cobertura, Ruff, formato, mypy, Node público y
preparación/verificación documental. **No incluye el panel/auditoría sin commit.**

La primera consulta del conector devolvió workflow_runs=[] porque filtra eventos
PR, y statuses=[] porque no incluye todos los check-runs. Se completó la lectura
con GET público de /actions/runs, total_count=1, y trabajos vía conector. El primer
intento de red local fue bloqueado por el sandbox; la lectura autorizada se pudo
ejecutar mediante revisión automática. No se modificó configuración remota.

## Correcciones realizadas en esta continuación

1. Ocultar clave en repr/str de Settings conservando su valor y autorización.
2. Añadir exportación real de OpenAPI aislada al preparar Quarto y copiar PDF oficial.
3. Añadir verificación de copia de fuentes sin datos/configuración local.
4. Corregir ADR de stack/SQLite/envelope con el PDF y límites de compatibilidad.
5. Reconciliar análisis BPMN y Quarto con QR diferido, colisiones acotadas y panel.
6. Corregir C4 actual: visitante, destino externo, panel y exclusión de futuros ficticios.
7. Documentar riesgos/OWASP pertinentes, uso de IA, contribución y entrega individual.
8. Añadir esta matriz y guía Windows, instalación pendiente de Quarto/Docker y demostración.
9. Corregir formato Ruff de los archivos BPMN/tests recibidos y verificar todos los controles.

Archivos de código/pruebas cambiados: backend/app/config.py,
scripts/render_portal.py, scripts/verify_clean_copy.py (nuevo),
scripts/build_process_models.py (formato), tests/unit/test_config.py,
tests/unit/test_documentation_models.py, tests/integration/test_documentation_export.py (nuevo).
Fuentes/documentación: README, CHANGELOG, ADR 0001/0002/0005, CONTRIBUTING,
C4 DSL/PlantUML, análisis BPMN, documentos de evaluación y páginas Quarto actualizadas.
Las funcionalidades del panel recibidas se conservaron; no se presentan como
implementadas por primera vez en esta auditoría ni se cambiaron contratos/endpoints.

### Inventario exacto de esta continuación

**27 archivos recibidos modificados**, frente al manifiesto previo:

- Raíz: README.md, CHANGELOG.md.
- Backend: backend/app/config.py.
- Gobierno/ADR: docs/CONTRIBUTING.md,
  docs/adr/0001-fastapi-vs-django-rest-framework.md,
  docs/adr/0002-sqlite-desarrollo-postgresql-futuro.md,
  docs/adr/0005-api-versionada-envelope-errores.md.
- Modelos: docs/arquitectura/unishort-c4.dsl, docs/arquitectura/c4-codigo.puml,
  docs/procesos/analisis-bpmn.md.
- Evaluación: docs/evaluacion/clarificaciones-y-desviaciones.md,
  docs/evaluacion/contexto-y-trazabilidad.md, docs/evaluacion/plan-auditoria-2026-11-06.md,
  docs/evaluacion/trazabilidad-evaluacion.md.
- Quarto: quarto/_quarto.yml, quarto/api.qmd, quarto/arquitectura.qmd,
  quarto/entrega.qmd, quarto/index.qmd, quarto/procesos.qmd, quarto/pruebas.qmd,
  quarto/requisitos.qmd.
- Herramientas: scripts/build_process_models.py, scripts/render_portal.py.
- Especificaciones: specs/001-create-short-link/plan.md.
- Pruebas: tests/unit/test_config.py, tests/unit/test_documentation_models.py.

**7 archivos creados:** este informe, docs/evaluacion/ejecucion-windows-y-entrega.md,
docs/evaluacion/seguridad-y-riesgos.md, docs/evaluacion/uso-ia-y-contribucion.md,
quarto/auditoria.qmd, scripts/verify_clean_copy.py,
tests/integration/test_documentation_export.py. Los recursos generados en
quarto/sources están ignorados y se reconstruyen con el script.

## Conservación del trabajo y datos

Sin cambios de rama ni HEAD, commits, pushes, reset/clean, borrados de evidencia
o migraciones sobre originales. El PDF y todos los archivos recibidos se conservan.
La instantánea previa permite inspeccionar también versiones de documentos corregidos.
SHA-256 de las bases antes y después:

| Base | SHA-256 intacto |
|---|---|
| unishort.db | 5DF7AD7C0231CD8F042FE0843132BA9FA6C084B1EF7B38E5925CCACF36768585 |
| demo-unishort.db | 1DA10E7949B1F5794E9FEB9699AD36D2FE6545A24ABC90CE444C9078F92B64E3 |

## Intervención humana antes de entregar

**P0:** revisar y autorizar incorporar/publicar los cambios locales. El docente no
puede evaluar el panel desde main si aún no está allí. Completar evidencia individual,
reflexiones y explicación técnica; revisar las decisiones de stack y privacidad.
No se hicieron esas acciones en nombre del equipo.

**P1:** instalar/renderizar Quarto y facilitar documentación generada; verificar
Docker si corresponde al entorno; demostrar el producto con navegador/QR y persona
no técnica, guardar evidencia real y ejecutar CI del SHA final. Revisar visualmente
diagramas BPMN/Structurizr/PlantUML. Entregar en EVA los cuatro elementos exigidos.

**P2 diferido:** OIDC/roles, PostgreSQL, auditoría individual, optimización y
endurecimiento público. No se desarrollaron funciones grandes ajenas al incremento.

## Estimación técnica conservadora (no calificación oficial)

| Criterio oficial | Estimación sobre 2 | Justificación |
|---|---:|---|
| 1. Especificación, trazabilidad y arquitectura | **1,7** | Coherencia mejorada y fuentes completas; render/validación visual de modelos y puertas formales pendientes. |
| 2. Funcionamiento y diseño de API | **1,9** | Flujo real, contratos y OpenAPI probados; compatibilidad legacy explícita aún heterogénea. |
| 3. Seguridad y calidad de implementación | **1,8** | Controles y pruebas sólidos para alcance académico; clave compartida y riesgos remotos delimitados. |
| 4. Pruebas y verificación | **1,8** | Suite/cobertura, copia aislada y HTTP real aprobados; aceptación visual/no técnica pendiente. |
| 5. Documentación, despliegue y contribución | **1,3** | README/portal/fuentes, PR y CI reales; falta publicación de cambios actuales, render, Docker y evidencia individual completa. |
| Total estimado | **8,5 / 10** | No se afirma 10/10 con entregables humanos y verificaciones pendientes. |

Los decimales son orientación técnica, no una predicción garantizada ni una
modificación de los descriptores 0/1/2 de la rúbrica. La calificación definitiva
y el crédito individual pertenecen al docente. Resolver los pendientes puede
mejorar el cumplimiento; no se asegura una nota por cantidad de pruebas o código.
