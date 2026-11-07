# Plan — panel administrativo

## Contexto técnico y contratos

Conservar FastAPI, SQLAlchemy, SQLite y frontend estático sin dependencias nuevas.
Orden: especificación → plan → tareas → pruebas rojas → implementación → regresión.
Agregar GET /api/v1/admin/stats protegido; ampliar GET /api/v1/links con q y status.
Reutilizar PATCH y QR. No cambiar esquema, permisos, rutas públicas ni envelope.
API → servicios → repositorio; dominio sigue independiente del framework.

## Constitution Check

Privacidad: consultas agregadas, sin eventos individuales ni logs de búsquedas.
Compatibilidad: parámetros aditivos y estados mutuamente excluyentes con prioridad
inactive > expired > active, igual que link_to_data.
Calidad: pytest/cobertura >=85%, Ruff, mypy estricto, JavaScript real con Node.
Accesibilidad: etiquetas, foco, confirmación nativa dialog, estado vivo y catálogo es/en.
La revisión humana de contraste, teclado y disposición es una puerta pendiente.

## Complexity Tracking

La solicitud explícita autoriza implementar localmente sin esperar votación del
equipo ni ejecutar comandos /speckit no disponibles en esta sesión. Se escriben
los artefactos equivalentes antes del código y no se inventa aprobación alguna.
La fusión/publicación quedan sujetas a revisión del equipo; no se hará commit/push.
HTML/CSS/JS son necesarios para ampliar el frontend existente aunque el principio
II formule producción en Python. No se añade framework ni segunda arquitectura.

## Implementación y validación

Resumen en una consulta SQL con COUNT/SUM/CASE y COALESCE. Listado acotado y
conteo con idénticos filtros y reloj, orden created_at DESC, id DESC.
Panel independiente admin.html enlazado al acortador; clave en cierre léxico,
AbortController y generación de sesión evitan resultados tras cerrar sesión.
Confirmación previa a PATCH; fechas locales convertidas a ISO UTC.
Pruebas de autorización, búsqueda literal, paginación, agregación, errores,
reactivación/caducidad, ausencia de secretos y regresión pública.
