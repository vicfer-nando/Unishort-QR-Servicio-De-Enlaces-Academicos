# Preparación reproducible en Windows 11 y entrega

## Preparación desde fuentes recibidas

Los cambios del panel y esta auditoría siguen locales: un clon de main no los
incluye hasta que el propietario autorice revisión, commit y push. No se presenta
la copia temporal comprobada como prueba de publicación en GitHub.

Requisitos: Python 3.13 para reproducir el entorno observado, Git y Node 22+ para
las pruebas JavaScript. Quarto y Docker Desktop son herramientas separadas.
Desde una terminal PowerShell en la raíz de la copia:

```powershell
py -3.13 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements-dev.lock
.\.venv\Scripts\python.exe -m pip check
```

No hace falta cambiar ExecutionPolicy ni activar el entorno: los comandos usan
su ejecutable directamente. Las versiones están fijadas en los locks. La
instalación desde red no se repitió aquí: se comprobó pip check y una copia de
fuentes sin BD/.env/.git/.venv con las dependencias ya instaladas.

Para iniciar con una base nueva y clave oculta, usar el
[guion completo del panel](../../specs/003-admin-dashboard/quickstart.md).
Inicia Alembic antes de Uvicorn, frontend en otra terminal y abre index.html o
admin.html en 5500. Swagger: http://localhost:8000/docs; health: /health.
Una copia limpia sin clave mantiene el flujo público y devuelve 503 en administración.

## Verificaciones

```powershell
$testTemp = Join-Path ([IO.Path]::GetTempPath()) ("unishort-tests-" + [guid]::NewGuid().ToString("N"))
.\.venv\Scripts\python.exe -m pytest tests --cov=backend/app --cov-report=term-missing -p no:cacheprovider --basetemp=$testTemp
.\.venv\Scripts\python.exe -m ruff check backend tests alembic scripts
.\.venv\Scripts\python.exe -m ruff format --check backend tests alembic scripts
.\.venv\Scripts\python.exe -m mypy backend/app
node scripts/verify_frontend.mjs
node --test tests/js/admin.test.mjs
.\.venv\Scripts\python.exe scripts/verify_clean_copy.py
.\.venv\Scripts\python.exe scripts/verify_runtime.py
```

Usar siempre un basetemp nuevo y exclusivo: pytest limpia su contenido al empezar.
verify_runtime necesita 8000/5500 libres, usa SQLite temporal y termina solo sus
subprocesos. verify_clean_copy incluye cambios locales sin commit y elimina solo
su temporal propio. Ninguno necesita una base existente para probar.

## Quarto — instalación y render pendientes

No se encontró quarto en PATH ni en las ubicaciones habituales de instalación.
No se instaló software del sistema sin autorización. En una terminal propia,
instalar Quarto desde su [sitio oficial](https://quarto.org/docs/get-started/) o,
si Windows Package Manager está disponible:

```powershell
winget install --id Posit.Quarto --exact
```

Reabrir la terminal para actualizar PATH; después, desde raíz:

```powershell
quarto --version
.\.venv\Scripts\python.exe scripts/render_portal.py --prepare-only
.\.venv\Scripts\python.exe scripts/verify_docs.py
.\.venv\Scripts\python.exe scripts/render_portal.py
quarto preview quarto --no-browser
```

El script prepara fuentes, PDF oficial y openapi.json generado del backend actual
en un subproceso con SQLite temporal. El HTML final queda en quarto/_site.
--prepare-only comprueba preparación, no render. Revisar visualmente los enlaces,
diagramas, tablas y navegación antes de entregar el portal o autorizar publicación.
Los comandos de instalación se documentan para ejecución humana; no se ejecutaron.

## Docker — instalación y ejecución pendientes

No se encontró Docker en PATH ni en su ubicación habitual. Instalar Docker Desktop
desde [Docker para Windows](https://docs.docker.com/desktop/setup/install/windows-install/)
o, si corresponde al entorno de Windows Package Manager:

```powershell
winget install --id Docker.DockerDesktop --exact
```

La instalación puede requerir permisos, WSL 2/virtualización y reinicio. Seguir el
instalador oficial y las condiciones de licencia aplicables; no se ejecutó aquí.
Después de iniciar Docker Desktop, usar un proyecto/volumen de demostración separado:

```powershell
docker version
docker compose -p unishort-evaluacion config --quiet
$adminSecret = Read-Host "Clave temporal de esta demostración" -AsSecureString
$env:UNISHORT_ADMIN_API_KEY = [Net.NetworkCredential]::new("", $adminSecret).Password
Remove-Variable adminSecret
docker compose -p unishort-evaluacion up --build -d
docker compose -p unishort-evaluacion ps
Invoke-RestMethod http://localhost:8000/health
```

--quiet evita volcar la configuración con la clave al comprobar Compose. La imagen
ejecuta Alembic y usa un usuario sin privilegios; el volumen queda asociado al
proyecto unishort-evaluacion, separado de las bases de la raíz. No repetir esto
contra un despliegue existente sin verificar puertos y nombre de proyecto.
Para detener esa demostración: docker compose -p unishort-evaluacion stop.
No usar down -v ni eliminar volúmenes para la entrega. HTTPS/producción no se afirman.

## Demostración breve sobre el producto (PDF pp. 7–8)

1. Explicar problema, actores y alcance; mostrar especificación y una historia.
2. Mostrar BPMN y C4/UML, explicar capas y ADR de FastAPI/SQLite.
3. Crear enlace público en la base temporal, ver/descargar PNG y abrir URL corta.
4. Mostrar Swagger: 201, envelope y errores; explicar PNG/307 y contrato legacy.
5. Entrar al panel con clave oculta; mostrar resumen, búsqueda/filtros y gestión
   confirmada. Desactivar/reactivar y cambiar/quitar fecha, sin borrar registros.
6. Mostrar pruebas/cobertura, migración aislada y health/logs sin secretos.
7. Mostrar portal Quarto generado e instrucciones de despliegue cuando se hayan
   ejecutado. No presentar capturas o CI históricos como evidencia del SHA final.
8. Cada integrante explicar su contribución y declarar el apoyo de IA.

## Entrega en EVA y acciones humanas

- Enlace al repositorio que contenga realmente los cambios revisados y publicados.
- Enlace a documentación generada desde el mismo contenido, con acceso del docente.
- Demostración funcional en el producto, no solo diapositivas.
- Evidencia/reflexión individual según el PDF p. 8.
- Revisión del equipo y autorización del propietario antes de commit/push/PR.
- Verificar Actions sobre el SHA final; no hay un check aprobado del árbol local.

No se publicaron sitios ni se crearon PR en esta auditoría. La calificación y la
aceptación de decisiones corresponden al docente, no a la herramienta.
