# Construcción y publicación de Quarto

## Estado y límites

Repositorio: [UniShort QR](https://github.com/vicfer-nando/Unishort-QR-Servicio-De-Enlaces-Academicos).
**URL pública de documentación: [PENDIENTE: publicación y comprobación real].**
La consulta de solo lectura al recurso Pages devolvió 404; no demuestra una URL
publicada. No se ha modificado configuración remota ni desplegado desde esta sesión.

El workflow [documentation.yml](../../../.github/workflows/documentation.yml) genera
el sitio en Ubuntu, con versiones fijadas, render de modelos, OpenAPI aislado y
verificación de enlaces HTML e inspección Chromium. También genera el artefacto
`unishort-documentation-qa` con capturas y manifiesto. No necesita mantener encendida la PC. En push a main
y PR solo construye un artefacto; el despliegue exige ejecución manual con la
opción `publicar=true`, rama `main` y entorno `github-pages`.

## Configurar GitHub una vez (propietario)

1. Revisar e integrar los cambios del panel, auditoría y entrega mediante un PR real.
   No fusionar PR #1 por cumplir un casillero: contiene cambios antiguos de seguridad
   incompatibles con el diseño actual y figura con conflictos.
2. En el repositorio: **Settings → Pages → Build and deployment → Source → GitHub Actions**.
   Requiere permisos de administración; no cambiar visibilidad ni crear secretos.
3. En **Settings → Actions → General**, permitir las acciones usadas por el workflow
   si una política las restringe. No conceder permisos de escritura globales: el
   trabajo de despliegue declara `pages: write` e `id-token: write` de forma explícita.
4. Opcional: en **Settings → Environments → github-pages**, configurar revisión
   humana y limitar ramas de despliegue a main. Una aprobación configurada debe
   completarla una persona; este documento no la concede.

## Construir y revisar antes de publicar

1. **Actions → Documentación Quarto → Run workflow**, seleccionar main y dejar
   `publicar` desmarcado. Esperar trabajo build correcto.
2. Descargar el artefacto `unishort-quarto-site` desde la ejecución. Extraerlo en
   una carpeta de revisión y servirla con Python en 5600; abrir el índice.
3. Revisar navegación, ocho SVG legibles, enlaces, páginas del dossier, PDF y
   OpenAPI. Registrar el enlace de esta ejecución y su SHA; una ejecución antigua
   del workflow quality no verifica este portal ni los cambios nuevos.
4. Si falla, leer el paso exacto y corregir mediante un nuevo cambio revisado.
   No desactivar validadores ni sustituir diagramas por imágenes inventadas.

## Publicar y obtener la URL real

1. Con aprobación del propietario, ejecutar de nuevo **Run workflow** en main,
   ahora con `publicar` marcado. El trabajo deploy requiere build aprobado.
2. Cumplir cualquier revisión de entorno; abrir el enlace mostrado por el trabajo
   deploy/entorno `github-pages` o por Settings → Pages.
3. Abrir esa URL real en una ventana sin sesión de GitHub y comprobar índice,
   diagramas, dossier y fuentes. No deducir que está publicada por el nombre del repo.
4. Copiar exactamente esa URL a `texto-entrega-eva.md`, este índice y el README.
   Registrar ejecución, SHA y fecha de verificación en resultados. Publicar esa
   actualización requiere revisión/commit/push humanos como cualquier otro cambio.

Si Pages está bloqueado por política o permisos, entregar temporalmente el
artefacto HTML generado con instrucciones de apertura y comunicar el bloqueo al
docente. El enlace a un artefacto de Actions puede requerir sesión y expira según
retención; no es equivalente a un portal público permanente.

## Reproducción de modelos y versiones

- [DSL C1–C3](../../arquitectura/unishort-c4.dsl) → Structurizr CLI → PlantUML → SVG.
- [UML C4](../../arquitectura/c4-codigo.puml) → PlantUML/Smetana → SVG, sin Graphviz.
- [BPMN 2.0.2](../../procesos/creacion-enlace.bpmn) → bpmn-js → cuatro SVG desde BPMNDI.
- `tools/documentation/versions.json` fija descargas y hashes; package-lock fija JS.
- `scripts/render_diagrams.py` falla si no exporta los modelos esperados.
- `scripts/render_portal.py` copia fuentes públicas, genera páginas HTML del dossier
  y exporta el OpenAPI en SQLite temporal, sin clave ni conexión a bases existentes.

No hay servicio remoto de render que reciba los modelos. Los SVG son derivados:
las fuentes editables se conservan y se enlazan junto con cada vista.

Referencias de procedimiento: [Quarto y GitHub Pages](https://quarto.org/docs/publishing/github-pages.html),
[workflows personalizados de Pages](https://docs.github.com/en/pages/getting-started-with-github-pages/using-custom-workflows-with-github-pages).
