# Matriz final de la rúbrica

Fuente: [PDF oficial](../../../Asignaci%C3%B3n_Y_Rubrica_Evaluaci%C3%B3n_Sumativa_1.pdf),
rúbrica pp. 9–10; entrega pp. 7–8 y uso de IA p. 10. Consultar el detalle por
requisito en la [auditoría previa](../auditoria-final-rubrica.md). Esta matriz
añade el paquete final; no convierte un archivo preparado en una actividad realizada.

Estados: **Cumplido y verificado**, **Implementado, pendiente de verificación**,
**Pendiente**, **No aplicable, con justificación**.

| Criterio oficial | Qué exige / evidencia existente | Archivo o enlace y verificación | Estado de cumplimiento | Riesgo pendiente |
|---|---|---|---|---|
| 1. Especificación, trazabilidad y arquitectura — 2 puntos | Problema, actores, RF/RNF, historias, aceptación, Spec Kit, análisis BPMN, C1–C4 y decisiones coherentes. | [Contexto y capas](../contexto-y-trazabilidad.md); [specs 001–003](../../../specs/features.md); [constitution](../../../.specify/memory/constitution.md); [BPMN](../../procesos/analisis-bpmn.md); [C4 DSL](../../arquitectura/unishort-c4.dsl); [UML](../../arquitectura/c4-codigo.puml); [ADR FastAPI](../../adr/0001-fastapi-vs-django-rest-framework.md). Tests `test_documentation_models.py`; generador de ocho SVG y manifiesto de hashes. | **Implementado, pendiente de verificación** de aceptación humana. Fuentes, trazabilidad y render local de ocho modelos verificados. | Ratificación constitucional/clarificaciones formales no acreditadas; validación BPMN XSD completa pendiente. FastAPI está justificado, sin aprobación docente inventada. |
| 2. Funcionamiento y diseño de la API — 2 puntos | Flujo requisito → HTTP → dominio/servicio → SQL → respuesta; `/api/v1`, métodos, validación, envelope, QR y administración. | [API del portal](../../../quarto/api.qmd); [contratos v1](../../../specs/001-create-short-link/contracts/v1-links.md); [contrato admin](../../../specs/003-admin-dashboard/contracts/admin.md); `backend/app/api/v1.py`; tests contract/integration; `scripts/verify_runtime.py`. | **Cumplido y verificado** mediante suite y recorrido HTTP previo; regresión final en [resultados](resultados-verificacion.md). | Legacy JSON plano preservado/documentado; `errors: []` es convención v1 consistente frente al ejemplo `null`. No presentar PNG/307 como JSON. |
| 3. Seguridad y calidad — 2 puntos | Autorización backend, entradas, secretos, errores, OWASP y separación de capas. | [Riesgos y controles](../seguridad-y-riesgos.md); [ADR 0004](../../adr/0004-autenticacion-provisional-administrativa.md); `api/deps.py`, dominio/repositorio y `frontend/admin.mjs`; tests security, JS, Ruff y mypy. `.env.example` sin clave predeterminada y con orígenes locales explícitos. | **Cumplido y verificado** en el alcance académico probado. | Clave compartida provisional: sin usuarios, roles, MFA ni atribución individual. HTTPS y controles de abuso de producción pendientes. No registrar la clave ni destinos completos. |
| 4. Pruebas y verificación — 2 puntos | Unitarias, integración, API/contratos, dominio, seguridad, frontend, cobertura y herramientas. | [Resultados efectivos](resultados-verificacion.md); `tests/`, `scripts/verify_frontend.mjs`, runtime/copia limpia; configuración en `pyproject.toml`, locks y workflow quality. | **Cumplido y verificado** para las ejecuciones documentadas; aceptación visual/no técnica **Pendiente**. | DOM simulado no equivale a revisión visual, accesibilidad completa, carga o producción. Conservar umbral 85 %. |
| 5. Documentación, despliegue y contribución — 2 puntos | Portal Quarto central, ejecución reproducible, Docker/CI, Git/PR, evidencia individual, demostración, IA y enlaces EVA. | [Índice](README.md); [reproducción](instrucciones-reproduccion.md); [publicación](publicacion-quarto.md); [fichas](contribuciones-individuales.md); [IA](declaracion-uso-ia.md); [guion](guion-demostracion.md); workflow documentation; [PR #2](https://github.com/vicfer-nando/Unishort-QR-Servicio-De-Enlaces-Academicos/pull/2); [CI histórico](https://github.com/vicfer-nando/Unishort-QR-Servicio-De-Enlaces-Academicos/actions/runs/42091635246). | **Implementado, pendiente de verificación** del SHA publicado/Pages, ejecución Docker y evidencia personal. Estado de render local en resultados. | No hay URL pública confirmada, entrega EVA ni demostración nueva. Los cambios siguen locales hasta integración humana. PR #1 abierto/con conflictos no equivale a contribución integrada. |

## Estimación técnica prudente

La auditoría anterior estimó **1,7 + 1,9 + 1,8 + 1,8 + 1,3 = 8,5/10**. Este paquete
reduce carencias de organización, publicación reproducible y evidencia identificable,
pero no sustituye publicación, revisión humana ni aportes personales. Se mantiene
esa referencia conservadora hasta cerrar tales pendientes; no se asigna 10/10.
Los decimales orientan, no cambian los descriptores oficiales ni garantizan nota.
La calificación grupal e individual pertenece al docente.
