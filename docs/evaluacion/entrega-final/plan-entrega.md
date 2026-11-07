# Plan de preparación de la entrega — 6 de noviembre de 2026

## Alcance autorizado

Centralizar la documentación, generar diagramas desde sus modelos, preparar un
sitio Quarto publicable y un dossier EVA. No cambiar funcionalidades del producto,
publicar, crear commits, fusionar ramas ni modificar datos existentes.

Fuentes: PDF oficial completo (11 páginas), auditoría final, constitution,
especificaciones 001–003, ADR, modelos y código/pruebas actuales. La rúbrica del
PDF prevalece; no se atribuyen aprobaciones ni pruebas humanas inexistentes.

## Preservación

Rama recibida: `feature/panel-administrativo`; HEAD `543701c`. Los cambios locales
del panel y de la auditoría se conservan. Instantánea inicial de esta preparación:
168 archivos y manifiesto SHA-256 en `.verification/entrega-baseline-3f83902c0ba54c4686bc40359de42700`.
Las bases originales no se usan para pruebas ni render.

## Incrementos verificables

1. Preparar generadores de documentación aislados y versiones explícitas.
2. Exportar BPMN con bpmn-js, C1–C3 con Structurizr y C4 con PlantUML, conservando fuentes.
3. Completar navegación Quarto y páginas del dossier desde documentos canónicos.
4. Configurar construcción CI y publicación Pages exclusivamente manual.
5. Redactar fichas individuales con commits/PR reales y campos personales pendientes.
6. Ejecutar regresiones, comprobar enlaces y render cuando las herramientas estén disponibles.
7. Registrar resultados efectivos y acciones humanas restantes.

Las herramientas de documentación se mantienen fuera de las dependencias del
backend. Su descarga/ejecución local requiere autorización; la configuración de
Actions prepara la alternativa reproducible sin publicar automáticamente.

## Criterios de cierre

Ocho documentos solicitados presentes; enlaces internos válidos; evidencia antigua
distinguida de resultados actuales; ningún secreto o base incorporado; comandos
de demostración aislados; workflow que no despliegue en push/PR; publicación y
entrega EVA explícitamente pendientes hasta confirmación real.
