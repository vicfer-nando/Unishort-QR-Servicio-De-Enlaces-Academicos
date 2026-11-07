# Plan de cierre técnico — 2026-11-06

## Fuente y alcance

La revisión anterior se inició sin el PDF y quedó provisional. En esta continuación
el archivo Asignación_Y_Rubrica_Evaluación_Sumativa_1.pdf sí está en la raíz:
se extrajo y leyó íntegramente el texto de sus 11 páginas con pypdf, corrigiendo
la codificación de salida de Windows. No hubo páginas sin texto verificable.
Poppler no está disponible: no se afirma inspección visual del render del PDF.
La fuente oficial prevalece; enumera cinco criterios de 2 puntos, pide justificar
tecnologías adicionales y declarar uso de IA y contribución individual (pp. 8–11).

No se ejecutan comandos Spec Kit ni se atribuyen aprobaciones. Este documento
registra el plan de mantenimiento autorizado por la solicitud, sin cambiar alcance
funcional ni constitución. Se mantienen FastAPI y las interfaces públicas existentes.

## Preservación

Rama recibida: feature/panel-administrativo, HEAD 543701c. Se conserva la rama y los
32 registros iniciales de estado Git, incluido el panel sin commit. Instantánea
local previa de 153 archivos en .verification/audit-baseline-d801cfd3ab3b414fa6489971a9f61d57.
Bases originales solo leídas para hash/copia; toda escritura de pruebas usa SQLite
temporal. No commits, pushes, borrados, instalaciones ni cambios del historial.

La continuación recibió 161 archivos de código/documentación más el PDF y los
preservó en .verification/rubrica-baseline-582b9471dbd54604bda13f74e19c19d5,
con manifiesto SHA-256, antes de editar. La rama y HEAD siguen sin cambiar.

## Hallazgos independientes del PDF y tareas

- [x] Reproducir línea base: 143 Python, 95,22 %; 19 JavaScript.
- [x] Revisar inventario vigente recibido y corregir afirmaciones no verificadas del ADR.
- [x] Incorporar panel/resumen, visitante/destino y dependencias reales a C4 C1–C4.
- [x] Reconciliar análisis/Quarto con BPMN recibido: PNG bajo demanda, colisiones y administración.
- [x] Probar integridad semántica básica/DI con XML y conservar fuentes editables.
- [x] Consolidar clarificaciones sin simular una sesión Spec Kit.
- [x] Documentar contratos JSON y excepciones heredadas sin romper clientes.
- [x] Verificar regresiones, migraciones de copia y arranque real con datos temporales.
- [x] Preparar matriz de cumplimiento y evidencias de colaboración observables.
- [x] Comprobar disponibilidad Docker/Quarto y verificar PR/Actions publicados en lectura autorizada.
- [x] Cotejar íntegramente las 11 páginas del PDF oficial incorporado.
- [x] Excluir admin_api_key de repr/str de Settings; rojo/verde observado.
- [x] Verificar suite desde copia de fuentes sin BD/.env/.venv, y arranque HTTP temporal.
- [x] Añadir declaración de IA y guion de entrega individual sin atribuciones ficticias.
- [x] Exportar OpenAPI real al preparar Quarto con subproceso/SQLite temporal, rojo/verde observado.
- [ ] Ejecutar Docker, render Quarto y validación visual/modeladores cuando estén disponibles.
- [ ] Completar revisión/reflexiones humanas y CI del SHA final tras publicación autorizada.

## Aceptación del mantenimiento

Given el software implementado, When se consultan inventario y diagramas, Then
describen API v1, panel y QR diferido, sin representar OIDC como implementado.
Given el XML BPMN, When se valida, Then sus actividades usan infinitivo, todas las
referencias y conexiones recíprocas son válidas y los nodos tienen DI.
Given las rutas públicas/heredadas, When se ejecuta la suite, Then conservan
contratos; errores vacíos siguen siendo [] en v1 y PNG/307 no se fuerzan a JSON.
Given una evidencia no ejecutada o una aprobación no observada, When se documenta,
Then figura pendiente, nunca cumplida por inferencia.
Given Settings con clave configurada, When se convierte a repr/str, Then el secreto
no aparece; su valor interno y la validación de cabecera siguen funcionando.
Given preparación del portal, When se exporta OpenAPI, Then se genera desde FastAPI
en un proceso aislado sin crear/modificar la base recibida por entorno ni incluir claves.
