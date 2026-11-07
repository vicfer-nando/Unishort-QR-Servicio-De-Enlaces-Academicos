# 003 — Panel administrativo

Fecha: 2026-11-05. Estado: implementación local solicitada por el propietario;
revisión y aprobación del equipo pendientes. No acredita aprobación institucional.

## Historias y aceptación

### US1 (P1): acceso provisional
Given una clave configurada, When el administrador la introduce, Then se valida
mediante GET /api/v1/links paginado con X-Admin-API-Key (endpoint protegido
preexistente) y se abre el panel con su resumen agregado.
Given clave ausente, incorrecta o servidor sin configurar, When se intenta entrar,
Then se informa respectivamente 401, 403 o 503 sin mostrar credenciales.
Given una sesión activa, When se cierra o abandona la página, Then se elimina la
clave de memoria y se cancelan solicitudes; respuestas tardías no reabren la sesión.

### US2 (P1): resumen y búsqueda
Given enlaces registrados, When se abre el panel, Then aparecen totales globales
de enlaces, activos, inactivos, caducados y visitas, calculados con SQL agregado.
Given una búsqueda o estado, When se consulta, Then se pagina en el servidor con
total filtrado, orden estable y coincidencia literal por código o URL.
Given cero resultados, When se consulta, Then se muestra un estado vacío.

### US3 (P1): gestión
Given un enlace, When se visualiza, Then se muestran destino, código, fechas,
estado y visitas y se permite copiar y abrir la URL corta.
Given un enlace utilizable, When se solicita su QR, Then se descarga PNG sin
incrementar visitas. QR de inactivos/caducados conserva el rechazo 410 existente.
Given confirmación explícita, When se cambia estado o caducidad, Then se usa el
PATCH protegido y se actualizan resumen y listado sin borrar registros.
Given caducidad pasada, When se intenta guardar, Then se rechaza sin mutar datos.
Reactivar el indicador no elimina caducidad: se debe ampliar o quitar la fecha
para volver a utilizar un enlace vencido. No se cambia esta regla del dominio.

### US4 (P2): experiencia
Given escritorio o móvil y navegación por teclado, When se usa el panel, Then
hay etiquetas, foco visible, mensajes anunciados, carga, confirmación y tabla
desplazable; se conserva la identidad verde y el acceso al acortador público.
El panel ofrece español e inglés con textos en catálogo externo.

## Requisitos y seguridad

- FR1: clave solamente en cierre léxico JavaScript; nunca en almacenamiento web,
  cookies, URL, HTML, mensajes o logs. Campo password vacío tras leerlo.
- FR2: ninguna petición administrativa sin clave; autorización real en servidor.
- FR3: solicitudes con cache no-store, credentials omit y cancelación al salir.
  Respuestas administrativas con Cache-Control no-store.
- FR4: mantener envelope, API pública, CORS y contratos QR existentes.
- FR5: limit 1..200, offset >= 0, q 1..2048 si se envía, estado enumerado.
  Búsqueda insensible a caja ASCII y literal (%, _ no son comodines).
- FR6: usar textContent/createElement; validar protocolos y origen antes de
  descargar QR; nunca enviar la clave a URLs devueltas por registros.
- FR7: no migraciones, eliminación física, servicios externos ni dependencias nuevas.
- FR8: autenticación compartida académica provisional; HTTPS fuera de loopback.
  No sustituye identidad institucional, roles, auditoría individual ni MFA.

## Verificación

Backend: tests/integration/test_admin_dashboard.py,
tests/contract/test_admin_dashboard_contract.py,
tests/security/test_admin_dashboard_security.py, tests/unit/test_admin_queries.py.
Frontend: node --test tests/js/admin.test.mjs; regresión pública verify_frontend.mjs.
Las pruebas usan SQLite temporal; nunca bases existentes. La inspección estática
y el DOM simulado no acreditan una prueba visual manual de WCAG ni de navegador.
