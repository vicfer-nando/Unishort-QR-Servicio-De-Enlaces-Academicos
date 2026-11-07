# Capturas: inventario y lista de obtención humana

Al iniciar esta preparación no se encontraron capturas PNG/JPG/SVG de la aplicación
en docs/, quarto/ o specs/ (excluidos derivados). Los SVG generados de modelos son
artefactos técnicos, **no** capturas de una demostración humana. Los enlaces GitHub
son evidencia consultable, no imágenes de ejecución local.

En la continuación autorizada se generaron [diez capturas automáticas del portal
y modelos](evidencias-automaticas.md), con resultado JSON y versión del navegador.
Esas imágenes ya existen; las capturas de uso de la aplicación de la tabla siguiente
siguen pendientes de una persona. El portal local no equivale a Pages publicado.

Guardar nuevas capturas auténticas en `docs/evaluacion/entrega-final/capturas/`,
solo después de realizarlas. No mostrar claves, cabeceras Authorization/API-Key,
variables de entorno completas, datos personales o URLs sensibles. No editar una
imagen para simular éxito. La tabla siguiente es una lista pendiente, no evidencia
de que se ejecutaron las acciones.

| Archivo recomendado | Pantalla / acción | Qué debe verse | Criterio | Estado inicial |
|---|---|---|---|---|
| 01-requisito-trazabilidad.png | Portal: abrir historia y matriz de capas | RF/aceptación y relación con código/prueba | 1 | Pendiente de captura humana |
| 02-bpmn.png | Portal: abrir proceso formal de creación | Diagrama legible y enlace XML | 1 | Pendiente; requiere render correcto |
| 03-arquitectura.png | Portal: abrir C2 y C4/UML | Contenedores y módulos reales, no solo tablas | 1 | Pendiente; requiere render correcto |
| 04-creacion-enlace.png | Acortador: crear URL de demostración | Resultado con URL corta y acceso a QR | 2 | Pendiente |
| 05-qr-descargado.png | Abrir PNG descargado | QR legible y nombre de archivo, sin secreto | 2 | Pendiente |
| 06-redireccion.png | Abrir URL corta; red de navegador solo para esta petición pública | 307/Location o destino con explicación de origen | 2 | Pendiente |
| 07-persistencia.png | Reiniciar backend con misma base temporal y consultar código | Registro/código conservado y health correcto | 2, 4 | Pendiente |
| 08-admin-login.png | Abrir acceso y probar clave incorrecta | Mensaje claro; campo vacío o enmascarado, sin cabeceras | 3 | Pendiente |
| 09-dashboard.png | Entrar y mostrar resumen/lista | Totales, estados, visitas y navegación | 2 | Pendiente |
| 10-gestion-estado.png | Confirmar desactivación y abrir URL corta | Confirmación/estado inactivo y respuesta 410 | 2, 3 | Pendiente |
| 11-swagger-envelope.png | POST v1 desde Swagger sin autorizar panel | 201 y cinco claves; caso inválido separado | 2 | Pendiente |
| 12-pruebas-python.png | Ejecutar pytest/cobertura | Comando, resultado completo, porcentaje y fecha contextual | 4 | Pendiente; no copiar cifras antiguas como actuales |
| 13-pruebas-js-calidad.png | Ejecutar JS, Ruff y mypy | Resultados reales y comandos | 3, 4 | Pendiente |
| 14-portal-publico.png | Abrir Pages sin sesión de GitHub | URL real, índice, navegación y diagramas | 5 | Pendiente de publicación y captura |
| 15-actions-final.png | Abrir ejecución del SHA final | SHA/rama, trabajos y conclusión aprobada | 4, 5 | Pendiente de integración y CI final |
| 16-pr-contribucion.png | Abrir PR #2 y revisión; cada integrante su evidencia | Autor, commits, estado y revisión reales | 5 / individual | Pendiente de captura; PR #2 sí fue consultado |
| 17-docker.png | Solo si se ejecuta Docker | compose ps healthy y /health, sin config con clave | 5 | Pendiente; Docker no disponible en auditoría |

Para una grabación breve, seguir el guion; registrar fecha, SHA, base de demo y
persona que demuestra. Completar un inventario tras obtener imágenes:

| Archivo real | Persona / fecha | SHA o versión mostrada | Observación |
|---|---|---|---|
| [PENDIENTE] | [PENDIENTE] | [PENDIENTE] | No añadir enlaces a archivos inexistentes. |

Los logs automatizados de esta preparación se describen en
[resultados](resultados-verificacion.md); no se convierten en capturas inventadas.
