# Guion de demostración funcional

Duración orientativa: 8–12 minutos; practicar y ajustar con el tiempo concedido.
No se afirma que esta presentación ya se haya realizado. Preparar antes las dos
terminales y la base temporal siguiendo [reproducción](instrucciones-reproduccion.md).
Mantener la clave fuera de proyección, capturas, historial y cabeceras visibles.

## Preparación previa

- Terminal A: Alembic + Uvicorn sobre una base nueva; terminal B: serve_frontend.py.
- Abrir acortador, panel, Swagger, portal generado/publicado y repositorio.
- Tener a mano un destino de prueba público, sin datos personales.
- Guardar el enlace creado para comprobar persistencia; no usar bases habituales.
- Tener resultados reales disponibles; una salida guardada se identifica como tal.

Comprobación rápida, tercera terminal:

```powershell
Invoke-RestMethod http://localhost:8000/health
git status --short --branch
```

## Recorrido completo

| Paso | Explicación natural y acción concreta | Qué debe poder verificarse |
|---|---|---|
| 1. Problema y objetivo | «Compartir direcciones académicas extensas dificulta su transcripción; ofrecemos enlaces cortos y QR». Abrir inicio Quarto. | Problema, contexto académico y alcance sin integración institucional ficticia. |
| 2. Requisitos seleccionados | Abrir Requisitos: creación, QR, redirección, estado/caducidad y administración. Elegir una historia y su aceptación. | Enlace de la especificación a implementación y prueba. |
| 3. Arquitectura | Abrir Arquitectura y mostrar C1–C4. Explicar navegador → API → servicio/dominio → repositorio → SQLite. | FastAPI justificado por ADR; QR local bajo demanda, sin servicio externo. |
| 4. Crear enlace corto | En <http://localhost:5500/index.html>, introducir `https://www.unl.edu.ec/` y crear. | URL corta única y resultado comprensible. No prometer que el destino externo siempre esté disponible. |
| 5. Generar QR | Visualizar y descargar PNG desde el resultado. | QR codifica la URL corta. Si se escanea con teléfono, usar una dirección alcanzable y configuración segura previa: localhost del teléfono no es la PC. |
| 6. Redirigir | Abrir el enlace corto en el mismo equipo. | Backend responde 307 y navegador sigue Location; no descarga el destino en el servidor. |
| 7. Persistencia | Detener solo Uvicorn con Ctrl+C y repetir el comando de inicio abajo, en la misma terminal con DATABASE_URL intacta. | El código creado sigue resolviendo; no se ha borrado ni recreado la base. |
| 8. Panel administrativo | Abrir <http://localhost:5500/admin.html>. Introducir clave sin proyectarla. | Login comprobado con petición protegida; resumen, lista y navegación coherentes. |
| 9. Autenticación/autorización | Cerrar sesión; introducir una clave incorrecta para mostrar mensaje, después volver a entrar correctamente. Mostrar el test de petición sin clave. | 401 sin clave, 403 incorrecta, 503 si servidor no configurado. No cambiar la clave del servidor en mitad de la demo principal. |
| 10. Estadísticas/gestión | Buscar el código, filtrar, ver visitas; Gestionar → desactivar → confirmar. Abrir URL: 410. Reactivar; editar fecha futura o quitarla y confirmar. | Reglas backend; un vencido requiere ampliar/quitar fecha y estar habilitado. QR no cuenta visita; abrir URL sí. No hay borrado físico. |
| 11. Swagger/OpenAPI | Abrir <http://localhost:8000/docs>. Ejecutar POST /api/v1/links con cuerpo válido y luego inválido, sin autorizar Swagger con la clave durante proyección. | 201/422, cinco claves envelope; PNG/307 son representaciones HTTP distintas; explicar legacy. |
| 12. Pruebas | Ejecutar comandos abajo o mostrar salida real fechada identificándola como previa. | Python/cobertura, JS, Ruff, mypy; relacionar un test con el requisito elegido. |
| 13. Seguridad | Explicar clave solo en memoria, autorización por petición, validación, DOM seguro y logs sin destinos/secretos. | Limitaciones explícitas: clave compartida, sin roles, HTTPS requerido fuera de local. |
| 14. Quarto | Abrir URL pública verificada si existe; de lo contrario portal local en 5600, indicando ese límite. Mostrar diagramas y dossier navegables. | Fuentes formales descargables, OpenAPI generado y procedimiento reproducible. |
| 15. GitHub y colaboración | Abrir PR #2, CI del SHA final si existe y fichas individuales; cada persona explica su parte y apoyo IA. | Commits/PR auténticos; PR #1 abierto se identifica como tal; reflexiones personales. |

Reiniciar backend sin perder la base de esta sesión:

```powershell
.\.venv\Scripts\python.exe -m uvicorn backend.app.main:app --host 127.0.0.1 --port 8000 --no-access-log
```

Pruebas breves en terminal propia (no la que sirve Uvicorn):

```powershell
$testTemp = Join-Path ([IO.Path]::GetTempPath()) ("unishort-demo-tests-" + [guid]::NewGuid().ToString("N"))
.\.venv\Scripts\python.exe -m pytest tests --cov=backend/app --cov-report=term-missing -p no:cacheprovider --basetemp=$testTemp
node --test tests/js/admin.test.mjs
node scripts/verify_frontend.mjs
.\.venv\Scripts\python.exe -m ruff check backend tests alembic scripts
.\.venv\Scripts\python.exe -m mypy backend/app
```

Para abrir portal local ya construido, terminal adicional:

```powershell
.\.venv\Scripts\python.exe -m http.server 5600 --bind 127.0.0.1 --directory quarto/_site
```

## Recorrido corto de emergencia (3–4 minutos)

1. Enunciar problema y mostrar una historia trazable y la vista C2 (30 s).
2. Crear enlace → ver/descargar QR → abrir URL corta (60 s).
3. Entrar al panel → buscar código → visitas → desactivar/confirmar → comprobar
   410 → reactivar (60 s). No exponer clave; explicar la validación backend.
4. Mostrar Swagger, resultado real de pruebas y Quarto (30–45 s).
5. Abrir repositorio/PR #2 y fichas; cada integrante explicar brevemente su aporte
   si el docente lo solicita. Declarar cualquier pendiente, incluida publicación.

Si falla internet, demostrar generación/redirección hacia un recurso local conocido
configurado previamente, o mostrar el 307 sin afirmar llegada al destino externo.
No presentar una grabación antigua como ejecución actual. Si falla el portal
público, usar el HTML generado e indicar que es local.
