# Contribuciones individuales: evidencia y validación personal

Consulta local `git log --all` y lectura autorizada de GitHub el **2026-11-06**.
La cuenta propietaria, CODEOWNERS, un autor de commit o asistencia de IA no demuestran
por sí solos quién escribió cada línea. No se asignan porcentajes, horas ni notas.
Cada persona debe verificar su ficha, explicar el cambio y escribir su reflexión.

## Organización confirmada por el equipo

Fuente de nombres, perfiles y distribución: declaración expresa del equipo durante
la preparación final. No se publican correos personales. Las responsabilidades
asignadas orientan coordinación; no excluyen colaboración de los demás ni prueban
por sí solas realización o autoría técnica.

| Integrante / perfil | Responsabilidades académicas principales declaradas |
|---|---|
| [Victor Fernando Roa Carrión](https://github.com/vicfer-nando) | APE 5, AA 5, coordinación, desarrollo/integración backend, exposición y entrega. |
| [Martina Alejandra Maldonado Machuca](https://github.com/MartinaMaldonado) | APE 5, AA 5, colaboración backend y exposición. |
| [María del Cisne Valarezo Román](https://github.com/MariaCVR) | APE 2, APE 3 y APE 4. |
| [Servio Julián Vega Jiménez](https://github.com/ServioVega) | ACD 3, ACD 4 y ACD 5. |
| [Wilson Patricio Palma Samaniego](https://github.com/wilsonpalma) | AA 2, AA 3 y AA 4. |

**Participación inicial declarada:** los cinco participaron conjuntamente en ACD 1,
ACD 2, APE 1 y AA 1, según informa el equipo. No se encontró en la búsqueda del
repositorio un conjunto de entregables identificados por esos números y atribuibles
individualmente. Se conserva la declaración como tal y se solicita material de respaldo.
No se inventan títulos o contenidos técnicos de actividades cuyo número es lo único conocido.

Se distinguen tres ámbitos: participación académica grupal (declaración y prácticas),
implementación técnica (cambios rastreables) e integración final (revisión, pruebas,
documentación y presentación). Git es una evidencia, no la única forma válida de
participación; se debe complementar con materiales y explicación personal.

## Victor Fernando Roa Carrión — cuenta vicfer-nando

GitHub: [vicfer-nando](https://github.com/vicfer-nando). El equipo confirma su
responsabilidad principal en programación, coordinación e integración técnica.
El historial contiene dos variantes del acento asociadas a la misma identidad.

**Realización declarada por el equipo:** desarrollo e integración del backend,
supervisión de cambios, organización del repositorio, revisión de resultados de IA,
ejecución/comprobación de pruebas, gestión Git y preparación de demo/entrega.
Comparte APE 5, AA 5 y exposición con Martina. La estimación personal de esfuerzo
comunicada no se publica como estadística ni se reparte artificialmente el resto.

| Evidencia | Contenido observable | Límite |
|---|---|---|
| [5ff998c](https://github.com/vicfer-nando/Unishort-QR-Servicio-De-Enlaces-Academicos/commit/5ff998c) | Primer commit de UniShort QR; estructura inicial y configuración de herramientas. | El mensaje y autor no atribuyen toda la elaboración manual. |
| [53f14ac](https://github.com/vicfer-nando/Unishort-QR-Servicio-De-Enlaces-Academicos/commit/53f14ac) | Incremento funcional, código, pruebas y documentación según diff. | Explicar personalmente componentes concretos y apoyo recibido. |
| [543701c](https://github.com/vicfer-nando/Unishort-QR-Servicio-De-Enlaces-Academicos/commit/543701cb62a644f270c7d6344386f5f4a23ea6bf) | Seguridad, migraciones y pruebas; es HEAD recibido. | No contiene cambios locales posteriores del panel/cierre. |
| [PR #2](https://github.com/vicfer-nando/Unishort-QR-Servicio-De-Enlaces-Academicos/pull/2) y [105e39c](https://github.com/vicfer-nando/Unishort-QR-Servicio-De-Enlaces-Academicos/commit/105e39c) | Revisión APPROVED por vicfer-nando (5 nov., 13:59:35 UTC) y merge de la contribución de Martina. | No es un PR de autoría individual de Victor ni revisión del panel actual. |

- Contribución técnica respaldada: los commits anteriores registran incrementos
  e integración. El panel/cierre actual sigue local y no tiene aún SHA publicado.
- Integración grupal: coordinación declarada; revisión/merge de PR #2 verificables.
- Decisión o dificultad para explicar: **[PENDIENTE: elegir un caso que domine,
  por ejemplo continuidad FastAPI, persistencia o integración; explicar alternativas
  y su intervención real, sin atribuirle automáticamente cada ADR]**.
- Pruebas/documentación personales: **[PENDIENTE: vincular ejecuciones o documentos
  concretos a su validación, distinguiendo las ejecuciones asistidas por Codex]**.
- Reflexión propia (3–5 líneas, no generada como testimonio): **[PENDIENTE]**.
- Evidencia de la integración final: **[PENDIENTE: SHA/PR tras revisión y publicación]**.

## Martina Alejandra Maldonado Machuca — cuenta MartinaMaldonado

GitHub: [MartinaMaldonado](https://github.com/MartinaMaldonado).
Asignación: APE 5, AA 5 y exposición con Victor. El equipo confirma colaboración
directa en backend/integración; el PR #2 respalda una contribución incorporada.

| Evidencia | Contenido observable | Límite |
|---|---|---|
| [8df95a3](https://github.com/vicfer-nando/Unishort-QR-Servicio-De-Enlaces-Academicos/commit/8df95a3bc1f663ffc7b156527dfe4fb2596db5d0) | Actualización de configuración, logging, servicios, Alembic, dependencias, README y pruebas según historial. | Distinguir autoría registrada de escritura manual de cada cambio. |
| [PR #2](https://github.com/vicfer-nando/Unishort-QR-Servicio-De-Enlaces-Academicos/pull/2) | Autora MartinaMaldonado, rama feature/martina; fusionado el 5 nov. de 2026 a las 14:00:48 UTC, aprobado por vicfer-nando. | Evidencia auténtica de contribución integrada; no atribuye funciones añadidas después. |

La lectura del patch completo de PR #2 confirma cambios en `config.py`,
`logging_config.py`, `main.py`, `services.py`, Alembic 0001/0002, locks, README,
configuración del frontend y pruebas de logging, migraciones y flujo HTTP del
frontend. El PR también incluyó una base histórica; las bases actuales están
ignoradas y no deben volver a incorporarse. Estos son archivos de una contribución
registrada, no una certificación de escritura manual exclusiva de cada línea.

- Actividad realizada/respaldada: contribución de configuración/dependencias y
  cambios anteriores integrada mediante PR #2; participación académica inicial
  declarada por el equipo. APE 5/AA 5 requieren su material específico de respaldo.
- Integración grupal: colaboración declarada y PR fusionado; revisión del paquete
  final por Martina **pendiente de evidencia**.
- Aprendizaje para explicar: **[PENDIENTE: seleccionar un cambio de logging,
  migraciones o dependencias del PR y describir cómo lo comprobó personalmente]**.
- Pruebas/documentación personales: **[PENDIENTE: señalar casos o secciones que
  pueda explicar y su ejecución/validación propia]**.
- Reflexión propia y forma de validación: **[PENDIENTE]**.

## María del Cisne Valarezo Román — cuenta MariaCVR

GitHub: [MariaCVR](https://github.com/MariaCVR). Nombre y pertenencia confirmados
por el equipo. Responsable principal asignada de APE 2, APE 3 y APE 4; participación
inicial conjunta declarada. El número de práctica no permite deducir su contenido.

| Evidencia | Contenido observable | Límite |
|---|---|---|
| [0cb3c2d](https://github.com/vicfer-nando/Unishort-QR-Servicio-De-Enlaces-Academicos/commit/0cb3c2d507ce092788c052a64ee82113fa236e76) | Autor MariaCVR, 4 nov.; añade historias, criterios y contratos preliminares en spec 001 (113 líneas). | Está en origin/maria-del-cisne y archivo/main-reemplazado, no en main recibido. No declararlo integrado. |
| [PR #1](https://github.com/vicfer-nando/Unishort-QR-Servicio-De-Enlaces-Academicos/pull/1) | Autora MariaCVR, rama maria-del-cisne, cuatro commits; abierto, no fusionado, mergeable=false al consultar. | Su descripción menciona X-API-Key en POST /shorten y cuatro pruebas históricas. No es el contrato actual ni un resultado ejecutado en esta preparación. |

No fusionar automáticamente ese PR: sus cambios antiguos de autenticación/estructura
requieren reconciliación y podrían romper el incremento. La contribución documental
puede explicarse mostrando el diff y su evolución; integrar solo cambios pertinentes
mediante revisión real, conservando la historia, si el equipo lo decide.

- Actividad respaldada: commit documental en spec 001 y PR #1 abierto. No se atribuyen
  módulos Python actuales ni integración final a partir de un PR sin fusionar.
- Integración grupal: responsabilidad académica declarada; incorporación de los
  cambios del PR y revisión final **pendientes de evidencia**.
- Evidencia por aportar: archivos originales/entregas de APE 2–4, fecha y versión,
  parte elaborada y relación con las historias/criterios del commit cuando corresponda.
- Dificultad/aprendizaje para explicar: **[PENDIENTE: explicar un criterio de aceptación
  o cambio del diff documental y su estado actual; identificar su propia intervención]**.
- Pruebas/documentación personales: **[PENDIENTE: aportar material de prácticas y
  cualquier ejecución real; no reutilizar cuatro pruebas históricas como resultado actual]**.
- Reflexión propia, incluyendo estado de integración: **[PENDIENTE]**.

## Servio Julián Vega Jiménez — cuenta ServioVega

GitHub: [ServioVega](https://github.com/ServioVega). Responsable principal asignado
de **ACD 3, ACD 4 y ACD 5**. Participación en ACD 1/2, APE 1 y AA 1 declarada por
el equipo; no se asigna contenido técnico a esos números sin los documentos.

- Realización confirmada disponible: participación inicial según declaración del
  equipo; no se encontraron entregables específicos que permitan verificar ACD 3–5.
- Contribución técnica y Git: **sin commits/PR atribuibles identificados en el
  historial local y los PR consultados**. Esto no demuestra ausencia de aporte académico.
- Integración final: **[PENDIENTE: aportar acta, revisión concreta o material que
  respalde una intervención, si la hubo]**; no se le asignan C4/ADR por su cargo.
- Evidencia necesaria: archivos o enlaces auténticos de ACD 3–5, título real,
  fecha/versión, sección elaborada y evidencia de entrega o colaboración.
- Aprendizaje para explicar: **[PENDIENTE: escoger un concepto de sus materiales
  ACD y explicar su relación con UniShort QR, solo cuando estén disponibles]**.
- Reflexión individual: **[PENDIENTE de redacción y validación por Servio]**.

## Wilson Patricio Palma Samaniego — cuenta wilsonpalma

GitHub: [wilsonpalma](https://github.com/wilsonpalma). Responsable principal asignado
de **AA 2, AA 3 y AA 4**. Participación inicial conjunta declarada por el equipo.

- Realización confirmada disponible: etapa inicial según declaración del equipo;
  las actividades AA 2–4 necesitan sus materiales para acreditar realización/alcance.
- Contribución técnica y Git: **sin commits/PR atribuibles identificados en las
  fuentes revisadas**. No se deduce de ello que no existan aportes fuera del repositorio.
- Integración final: **[PENDIENTE: identificar colaboración concreta y respaldo,
  si la hubo]**. No se le atribuyen pruebas, módulos o revisiones no acreditados.
- Evidencia necesaria: archivos o enlaces reales de AA 2–4, títulos y fechas,
  parte realizada y comprobante de entrega/trabajo personal cuando exista.
- Dificultad/aprendizaje para explicar: **[PENDIENTE: seleccionar un resultado de
  sus actividades AA y mostrar cómo lo comprendió o aplicó; evitar testimonios genéricos]**.
- Reflexión individual: **[PENDIENTE de redacción y validación por Wilson]**.

## Cierre de las cinco fichas

La lista oficial queda confirmada con cinco integrantes. Cada persona debe revisar
su ficha, aportar materiales faltantes y explicar personalmente su aprendizaje.
Una actividad asignada no se marca realizada automáticamente. No se crean commits,
aprobaciones ni reflexiones para llenar vacíos de evidencia.

## Comandos de inspección reproducibles

```powershell
git log --all --format="%h %an %ad %s" --date=short
git show --stat 8df95a3
git show 0cb3c2d -- specs/001-create-short-link/spec.md
git branch -a --contains 0cb3c2d
git log main --oneline
git status --short --branch
```

La estrategia observada usa ramas y PR a main, sin develop permanente: equivalencia
académica simplificada, no GitFlow estricto. [CONTRIBUTING](../../CONTRIBUTING.md)
explica la justificación y sus límites. No se modifica el historial para simularla.
