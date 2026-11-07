# Reproducción desde una copia del repositorio

Windows 11, PowerShell, Git, Python 3.13 y Node 22+ (pruebas JS). Quarto, Java y
herramientas de diagramas se requieren solo para construir la documentación.
Las versiones de dependencias Python están en locks. Docker es una alternativa.

## 1. Obtener las fuentes y dependencias

```powershell
git clone https://github.com/vicfer-nando/Unishort-QR-Servicio-De-Enlaces-Academicos.git
Set-Location Unishort-QR-Servicio-De-Enlaces-Academicos
git status --short --branch
py -3.13 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements-dev.lock
.\.venv\Scripts\python.exe -m pip check
```

El clon solo contiene cambios publicados. Antes de la integración final el panel
y este dossier pueden existir únicamente en la rama local. El propietario debe
comunicar al docente el SHA final/PR real; no se inventa aquí un tag de entrega.
No es necesario activar el entorno ni cambiar ExecutionPolicy.

## 2. Crear una demostración aislada y aplicar migraciones

Desde la raíz, primera terminal. No copiar claves de ejemplo ni usar bases existentes:

```powershell
$demoDirectory = Join-Path ([IO.Path]::GetTempPath()) ("unishort-entrega-" + [guid]::NewGuid().ToString("N"))
New-Item -ItemType Directory -Path $demoDirectory | Out-Null
$env:UNISHORT_DATABASE_URL = "sqlite:///$($demoDirectory.Replace('\', '/'))/entrega.db"
$env:UNISHORT_BASE_URL = "http://localhost:8000"
$env:UNISHORT_CORS_ORIGINS = "http://localhost:5500,http://127.0.0.1:5500"
$adminSecret = Read-Host "Define una clave temporal para el panel" -AsSecureString
$env:UNISHORT_ADMIN_API_KEY = [Net.NetworkCredential]::new("", $adminSecret).Password
Remove-Variable adminSecret
.\.venv\Scripts\python.exe -m alembic upgrade head
.\.venv\Scripts\python.exe -m alembic current
.\.venv\Scripts\python.exe -m uvicorn backend.app.main:app --host 127.0.0.1 --port 8000 --no-access-log
```

Mantener esta terminal abierta. La lectura oculta no imprime ni añade la clave
al historial; la variable de entorno sigue siendo un secreto del proceso, no una
bóveda. No ejecutar `Get-ChildItem Env:` ni capturar cabeceras. Sin clave configurada
el flujo público funciona y administración responde 503. `.env.example` documenta
variables sin una clave utilizable ni CORS abierto.

## 3. Frontend, Swagger y panel

Segunda terminal en la raíz:

```powershell
.\.venv\Scripts\python.exe scripts/serve_frontend.py
```

- Acortador: <http://localhost:5500/index.html>.
- Panel: <http://localhost:5500/admin.html>; introducir la misma clave temporal.
- Swagger: <http://localhost:8000/docs>; OpenAPI: <http://localhost:8000/openapi.json>.
- Salud: <http://localhost:8000/health>.

Usar HTTP local; fuera de loopback se requiere HTTPS. La clave del panel solo se
mantiene en memoria de la página, viaja en `X-Admin-API-Key` y se descarta al cerrar
sesión/recargar. No ponerla en URL, archivos, almacenamiento web ni capturas.

Crear una URL de demostración (por ejemplo `https://www.unl.edu.ec/`), descargar
QR y abrir el enlace corto. El destino es externo: necesita conectividad en el
navegador; la generación del QR no consulta ese sitio. Reiniciar Uvicorn con el
mismo entorno conserva la base temporal. Consultar visitas y estado en el panel.
Detener con Ctrl+C; al terminar en la primera terminal:

```powershell
Remove-Item Env:UNISHORT_ADMIN_API_KEY
Remove-Item Env:UNISHORT_DATABASE_URL
```

La base de demo permanece en su directorio temporal exclusivo; no se borra ninguna
base original. Para reiniciar durante la demo, no quitar DATABASE_URL hasta concluir.

## 4. Pruebas y calidad

Tercera terminal en raíz, sin variables de una base existente:

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

`--basetemp` debe ser nuevo y exclusivo: pytest limpia su contenido. Runtime necesita
8000/5500 libres (detener demo primero), usa SQLite temporal y termina sus propios
subprocesos. Copia limpia incluye fuentes locales no ignoradas y reutiliza las
dependencias instaladas: no equivale a probar una instalación Windows desde cero.
Los [resultados](resultados-verificacion.md) distinguen ejecuciones de instrucciones.

## 5. Quarto y los ocho diagramas

La alternativa sin instalar herramientas en Windows es el workflow documentation:
ver [guía de publicación](publicacion-quarto.md). Para render local, instalar
Node 22+ y Java 17+ desde sus proveedores si no existen; requieren decisión humana.
El siguiente procedimiento descarga paquetes portátiles y dependencias únicamente
del proyecto, sin modificar PATH ni instalar Quarto en el sistema:

```powershell
.\.venv\Scripts\python.exe scripts/setup_docs_tools.py --quarto
npm.cmd --prefix tools/documentation ci --ignore-scripts --no-audit --no-fund
$env:PLAYWRIGHT_BROWSERS_PATH = Join-Path (Get-Location) ".verification/docs-tools/browsers"
Push-Location tools/documentation
npx.cmd playwright install chromium
Pop-Location
.\.venv\Scripts\python.exe scripts/render_diagrams.py
.\.venv\Scripts\python.exe scripts/render_portal.py --prepare-only
.\.venv\Scripts\python.exe scripts/verify_docs.py
.\.venv\Scripts\python.exe scripts/render_portal.py
.\.venv\Scripts\python.exe scripts/verify_site.py
node tools/documentation/check-portal.mjs
.\.venv\Scripts\python.exe -m http.server 5600 --bind 127.0.0.1 --directory quarto/_site
```

Abrir <http://localhost:5600/>. Los artefactos quedan en `quarto/diagrams` y
`quarto/_site`; el manifiesto registra hashes de las tres fuentes formales. El
render debe fallar si un modelo no se puede exportar; no se reemplaza por imágenes
decorativas. Quarto instalado en PATH también es válido; `QUARTO_BIN` permite indicar
su ejecutable. El instalador portable Windows fija Quarto 1.11.9, PlantUML 1.2026.9 y
Structurizr CLI 2025.11.09 con SHA-256. Este CLI archivado se usa solo como exportador
local; una futura actualización debe validar nuevamente su salida. bpmn-js 18.31.1
exporta las cuatro vistas del XML; Playwright 1.65.0 ejecuta el render de documentación.
El render Quarto aísla sus cachés/perfil en `.verification/quarto-profile` y no
reenvía variables UNISHORT al proceso documental. No modifica APPDATA/LOCALAPPDATA
del usuario: los valores se sustituyen únicamente para ese subproceso. La inspección
Chromium genera capturas y un informe JSON identificados como automáticos, sin
equivaler a demostración humana o aceptación visual del producto.

## 6. Docker (alternativa pendiente si no está disponible)

Instalar/iniciar [Docker Desktop para Windows](https://docs.docker.com/desktop/setup/install/windows-install/)
con WSL 2/virtualización según su guía. No se requiere para la demo local anterior.
Con puertos 8000/5500 libres y un nombre de proyecto nuevo:

```powershell
docker version
docker compose -p unishort-entrega-20261106 config --quiet
$dockerSecret = Read-Host "Clave temporal de esta demo Docker" -AsSecureString
$env:UNISHORT_ADMIN_API_KEY = [Net.NetworkCredential]::new("", $dockerSecret).Password
Remove-Variable dockerSecret
docker compose -p unishort-entrega-20261106 up --build -d
docker compose -p unishort-entrega-20261106 ps
Invoke-RestMethod http://localhost:8000/health
docker compose -p unishort-entrega-20261106 stop
Remove-Item Env:UNISHORT_ADMIN_API_KEY
```

`config --quiet` evita imprimir secretos. La imagen aplica Alembic al arrancar y
usa un volumen de ese proyecto; no monta las bases de la raíz. No usar `down -v`
ni borrar volúmenes. Las URLs son las mismas de la demo. Docker configurado no
equivale a Docker ejecutado; consultar el estado real en resultados.
