# Resultados de la preparación final

Fecha: 6 de noviembre de 2026. Los resultados de esta página se actualizan solo
después de ejecutar cada comprobación. La [auditoría previa](../auditoria-final-rubrica.md)
registró 148 Python, 95,22 % de cobertura, 19 JS y recorrido HTTP real aprobados.
No se presentan esos datos como una nueva ejecución de este paquete.

## Estado inicial / comprobaciones remotas

- Rama conservada: feature/panel-administrativo, HEAD 543701c; cambios locales previos preservados.
- Snapshot de 168 fuentes y manifiesto SHA-256 antes de editar; bases originales fuera de pruebas.
- Repositorio público confirmado; Pages devolvió 404 en lectura, sin URL pública confirmada.
- PR #2 fusionado/aprobado; PR #1 abierto, no fusionado, con conflictos según metadata.
- CI histórico success para 543701c: run 42091635246. No prueba este árbol local.
- No commits, pushes, publicación, modificaciones remotas ni entrega EVA realizados.

## Ejecuciones finales

| Comprobación ejecutada | Resultado real | Alcance / límite |
|---|---|---|
| pytest completo con SQLite aislada y basetemp exclusivo | **158 aprobadas, 0 fallidas**, un aviso deprecación AnyIO/Starlette | Conserva los 148 casos previos y añade 10 de herramientas/modelos de entrega. No se modificaron pruebas del producto para aprobar. |
| Cobertura backend | **95,22 %** (896/941 sentencias), umbral **85 %** superado | No mide calidad visual ni cobertura de las herramientas Java/Node de render. |
| node --test tests/js/admin.test.mjs | **19 aprobadas**, 0 fallidas | JavaScript real con DOM/red simulados, no navegador visual. |
| node scripts/verify_frontend.mjs | Aprobada: validación, creación, QR, Blob y errores | Regresión pública JS simulada. |
| verify_runtime.py | HTTP real, SQLite, QR decodificado, administración, CORS y persistencia tras reinicio **OK** | Base temporal; p95 loopback 11,83 ms creación / 10,11 ms redirección, 100 muestras por operación, concurrencia 1, límite de tasa desactivado solo durante benchmark. No mide SC-004 visual ni carga de producción. |
| Ruff check / format --check | Aprobados, **58 archivos** formateados | backend, tests, alembic y scripts. |
| mypy backend/app | Sin errores en **20 módulos** | Configuración strict existente. |
| verify_clean_copy.py | **208 fuentes** sin BD/.env/.git/.venv; **158 Python + 19 JS + regresión pública** aprobadas | Reutiliza dependencias del entorno; no es una instalación Windows de cero ni clon remoto con cambios ya publicados. Incluye las capturas existentes al ejecutar la copia. |
| render_portal.py --prepare-only | Fuentes, páginas QMD del dossier y OpenAPI exportado | SQLite temporal, sin clave; **preparar no equivale a renderizar**. |
| verify_docs.py | Fuentes UTF-8/enlaces, YAML y referencias BPMN aprobadas | Comprobación final estricta, con los ocho SVG y manifiesto presentes. El modo fuentes se había usado antes de descargar herramientas. |
| render_portal.py (render completo) | **25 páginas HTML** construidas con Quarto portable | Sin usar bases existentes ni reenviar secretos de la aplicación; perfil/cachés aislados. |
| verify_site.py | Enlaces, archivos, recursos y anclas locales de HTML aprobados | No comprueba acceso a URLs externas ni publicación Pages. |
| check-portal.mjs | Chromium: HTML, imágenes y Mermaid sin errores; inicio escritorio/móvil; capturas reales | [Informe JSON y galería](evidencias-automaticas.md); inspección automatizada local, no prueba humana del producto. |
| pip check | Sin dependencias rotas | Entorno Python instalado. |
| node --check tools/documentation/render-bpmn.mjs | Sintaxis aprobada | No ejecuta bpmn-js/Chromium ni valida un render. |
| package-lock / npm ci documental | Lock generado e instalado: 22 paquetes, sin scripts de instalación | Versiones/hashes fijados; dependencias separadas del backend. |
| git diff --check | Sin errores de whitespace; avisos normales LF/CRLF de Git | No se modificó configuración de Git. |
| Índice Git: bases/secretos con extensiones sensibles | Ningún .db/.sqlite/.sqlite3/.env/.pem/.key registrado en el índice actual | No es una auditoría forense de todo el historial; hubo BD histórica, ya señalada. |

Las diez pruebas nuevas verifican tres rutas de traversal ZIP rechazadas antes de
extraer, detección de enlaces/anclas HTML rotos, conversión de enlaces del dossier
y obligación de despliegue manual en main con permisos mínimos, y selección de la
vista Structurizr sin confundirla con su leyenda exportada. Este último caso se
observó fallar antes de implementar la corrección; la suite final pasó completa.
Se comprobó en el código oficial del CLI el nombre real de su clase principal,
su formato de exportación y la existencia de archivos de leyenda. La continuación
añade aislamiento de perfil/secretos Quarto, etiquetas BPMN fuera de compuertas
y rechazo de acentos corruptos en SVG antes de guardar el render.
El validador HTML pasó sus pruebas y luego comprobó el sitio renderizado real.

## Continuación autorizada: render real y equipo confirmado

El usuario autorizó descargas y render local. Se descargaron **Quarto 1.11.9,
PlantUML 1.2026.9 y Structurizr CLI 2025.11.09**, con SHA-256 verificado, dentro de
`.verification/docs-tools`. npm ci instaló 22 paquetes del lock sin ejecutar scripts;
Playwright descargó Chromium 158.0.8127.18 en ese mismo espacio aislado. Java 17
existía. No hubo instalación de software del sistema.

**Render ejecutado:** Structurizr aceptó el DSL y exportó C1/C2/C3; PlantUML/Smetana
generó esas vistas y C4/UML; bpmn-js importó el XML sin advertencias y exportó sus
cuatro BPMNDiagram. Ocho SVG y manifiesto con hashes reales generados. Quarto
construyó el portal; verify_site comprobó archivos, recursos y anclas de HTML.
La inspección Chromium del portal pasó sin errores de imágenes/Mermaid, con inicio
en escritorio y móvil. Capturas e informe JSON reales en
[evidencias automáticas](evidencias-automaticas.md). No son una demostración humana.

Se corrigió el perfil/caché Quarto para escribir únicamente en `.verification`,
sin reenviar variables UNISHORT al subproceso. La primera captura directa del SVG
agotó su tiempo; se corrigió la inspección rasterizando el mismo SVG dentro de una
imagen HTML. La comprobación posterior pasó. No se ocultaron errores de los modelos.
La revisión de la captura BPMN motivó ajustar únicamente etiquetas y rutas DI;
se conserva el contenido semántico y se añadió una prueba de etiquetas de compuerta.
El cotejo automático de todos los elementos BPMN del modelo (sin DI) confirmó
igualdad con la instantánea inicial. Tras el último ajuste de límites de etiquetas
pasaron las 13 pruebas específicas de modelos/herramientas.

La revisión de C1–C3 detectó acentos mal interpretados por la codificación por defecto
de Java 17 en Windows: se fijó `-Dfile.encoding=UTF-8`, se regeneró y se comprobó el
texto real del SVG. C1/C2 incluyen explícitamente el destino externo ya existente
en el modelo para que la vista muestre la redirección seguida por el navegador.

**Equipo confirmado:** Victor, Martina, María, Servio y Wilson tienen fichas con
perfiles públicos, responsabilidades declaradas y evidencia diferenciada. El patch
completo de PR #2 se consultó para delimitar los archivos de Martina. La búsqueda
no identificó materiales por número ACD/APE/AA ni commits atribuibles a Servio/Wilson;
esos aportes requieren material externo auténtico. No se publicaron correos personales.

Docker sigue ausente y no se ejecutaron contenedores. El primer build documental
en GitHub debe comprobarse después de integrar los cambios.

No se instaló software del sistema. El workflow documentation **no se ejecutó en
GitHub** en esta preparación y no tiene aprobación remota para el árbol local.
La publicación exige configuración Pages y ejecución manual deliberada.

## Conservación de datos

SHA-256 de ambas bases coincide con el observado antes de trabajar:

```text
unishort.db       5DF7AD7C0231CD8F042FE0843132BA9FA6C084B1EF7B38E5925CCACF36768585
demo-unishort.db  1DA10E7949B1F5794E9FEB9699AD36D2FE6545A24ABC90CE444C9078F92B64E3
```

No se cambió de rama ni se alteró el historial. Las fuentes originales de modelos
se conservan. Se simplificó README trasladando instrucciones/evidencias a documentos
enlazados, sin eliminar el generador público o avances del panel. `.env.example`
dejó de sugerir una clave predeterminada y CORS abierto; no cambia datos del usuario.

El cotejo de los **168 archivos iniciales** contra su manifiesto no detectó
archivos desaparecidos. Los hashes de **backend/ y frontend/** permanecen iguales
a los recibidos al comenzar esta fase: no se alteró código funcional del producto.

## Pendientes de intervención humana

Integración revisada/CI del SHA final, configuración y publicación Pages, revisión
visual del portal/aplicación, fichas y reflexiones individuales, confirmación de uso
OpenCode/modelo, capturas/demostración, Docker si se exige evidencia ejecutada y
envío real en EVA. Ninguna plantilla equivale a esas actividades.
