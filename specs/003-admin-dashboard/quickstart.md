# Demostración aislada del panel

Desde la raíz en PowerShell, con las dependencias instaladas:

```powershell
$demoDirectory = Join-Path ([IO.Path]::GetTempPath()) ("unishort-admin-" + [guid]::NewGuid().ToString("N"))
New-Item -ItemType Directory -Path $demoDirectory | Out-Null
$env:UNISHORT_DATABASE_URL = "sqlite:///$($demoDirectory.Replace('\', '/'))/admin.db"
$env:UNISHORT_BASE_URL = "http://localhost:8000"
$env:UNISHORT_CORS_ORIGINS = "http://localhost:5500,http://127.0.0.1:5500"
$adminSecret = Read-Host "Define una clave temporal que volverás a introducir en el panel" -AsSecureString
$env:UNISHORT_ADMIN_API_KEY = [Net.NetworkCredential]::new("", $adminSecret).Password
Remove-Variable adminSecret
.\.venv\Scripts\python.exe -m alembic upgrade head
.\.venv\Scripts\python.exe -m uvicorn backend.app.main:app --host 127.0.0.1 --port 8000 --no-access-log
```

No escribir el secreto como literal en un comando: quedaría en el historial.
La lectura oculta evita imprimirlo. La variable de entorno es provisional,
no una bóveda de secretos. El subproceso debe heredarla para autorizar peticiones.
No guardar la clave en el navegador ni compartir capturas de cabeceras.

En otra terminal desde la raíz:

```powershell
.\.venv\Scripts\python.exe scripts/serve_frontend.py
```

1. Abrir <http://localhost:5500/index.html> y crear varios enlaces de prueba.
2. Abrir <http://localhost:5500/admin.html> o pulsar Administración.
3. Introducir la misma clave temporal. La primera petición protegida es
   GET /api/v1/links con limit=20 y offset=0 (listado protegido preexistente); la clave
   nunca se transmite por URL. A continuación se obtiene el resumen agregado.
4. Ver resumen, buscar parte de una URL/código y filtrar estado. Probar paginación
   con más de 20 enlaces. Los totales globales no cambian con la búsqueda.
5. Copiar, abrir y descargar QR. Abrir registra visita; descargar no la incrementa.
6. Pulsar Gestionar; desmarcar Enlace habilitado y confirmar. Reactivar de igual
   forma. El QR solo se habilita cuando el enlace es utilizable.
7. Gestionar permite fecha futura en hora local o vacío para quitar caducidad.
   Un enlace vencido requiere ampliar/quitar fecha además de estar habilitado.
8. Cerrar sesión y recargar: no debe conservarse acceso. Probar clave incorrecta.
9. Detener ambos procesos con Ctrl+C. En la primera terminal:

```powershell
Remove-Item Env:UNISHORT_ADMIN_API_KEY
Remove-Item Env:UNISHORT_DATABASE_URL
```

La base de demostración queda en el directorio temporal creado, separado de
unishort.db y demo-unishort.db. No hay borrado automático de esas bases.
Para usar la base habitual, iniciar normalmente sin redefinir DATABASE_URL;
las acciones confirmadas del panel sí actualizarán los enlaces de esa base.

## Errores y despliegue

401 solicita volver a entrar; 403 indica clave incorrecta/sin acceso; 503 indica
administración sin configurar o servicio no disponible. En los tres casos el
cliente cierra la sesión local. Si se modifica la variable del servidor, reiniciar
Uvicorn para que la configuración cacheada tome el nuevo valor.

El navegador solo mantiene la clave en memoria de esa página. Recargar/abandonar
obliga a iniciar otra vez; no hay identidad individual, roles ni sesión en servidor.
Cerrar sesión no revoca la clave compartida en otros clientes: requiere rotación.
Usar HTTPS fuera de loopback y servir únicamente frontend y scripts de confianza.
La política CSP de admin.html permite la API local en 8000 y el mismo origen;
otros despliegues deben configurar el origen de API con un script propio permitido
y ajustar connect-src de forma explícita, sin comodines ni scripts inline.

Pruebas: pytest completo con SQLite temporal, node --test tests/js/admin.test.mjs,
node scripts/verify_frontend.mjs. La prueba visual/manual y revisión del equipo
siguen pendientes; este guion no constituye evidencia de haberlas realizado.
