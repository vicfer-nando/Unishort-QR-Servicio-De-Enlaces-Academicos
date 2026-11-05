# Quickstart: UniShort QR (implementación actual)

**Fecha**: 2026-10-26 | **Estado**: acortador de URLs operativo

Esta guía describe la implementación que existe hoy en el repositorio: un backend
FastAPI en `backend/app` y un frontend estático en `frontend/index.html`. Está
escrita para Windows 10/11 con PowerShell.

> **Alcance actual**: creación de enlaces cortos y redirección. La generación de
> códigos QR, la autenticación, los roles, el panel administrativo, las
> estadísticas y el rate limiting **no** están implementados todavía. UniShort QR
> es un proyecto académico y no representa una aprobación oficial de la
> Universidad Nacional de Loja.

## Requisitos

- Python 3.11 o superior. En el entorno de desarrollo actual se usa Python 3.13.
- PowerShell.
- Un navegador moderno.

## 1. Backend: dependencias

Desde la raíz del repositorio:

```powershell
cd backend
```

El entorno virtual `backend/.venv` ya existe en este repositorio. Si falta, se
puede crear una sola vez:

```powershell
py -m venv .venv
```

Actívalo e instala las dependencias:

```powershell
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

Si PowerShell bloquea la activación:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
```

Para ejecutar las pruebas, instala también las dependencias de desarrollo:

```powershell
python -m pip install -r requirements-dev.txt
```

`requirements-dev.txt` incluye `requirements.txt`, `pytest` y `httpx`. Sin
`httpx` no funciona `fastapi.testclient.TestClient`.

## 2. Backend: base de datos y arranque

No hay migraciones ni Alembic. Al importar `app.main`, SQLAlchemy crea
automáticamente la tabla `short_urls` en el archivo SQLite `unishort.db` de la
raíz del repositorio (`backend/app/database.py`).

Arranca la API desde la carpeta `backend`:

```powershell
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

- API: <http://127.0.0.1:8000/>
- Documentación interactiva: <http://127.0.0.1:8000/docs>
- OpenAPI: <http://127.0.0.1:8000/openapi.json>

## 3. Frontend: arranque

En otra terminal, desde la raíz del repositorio:

```powershell
cd frontend
py -m http.server 5500
```

Abre <http://localhost:5500>. El frontend llama a la API en
`http://localhost:8000`, valor definido en `frontend/index.html` mediante
`API_BASE_URL`. Si cambias el host o el puerto del backend, actualiza esa
constante. El backend permite CORS desde el origen del frontend.

También se puede abrir `frontend/index.html` directamente, pero servir la página
por HTTP evita restricciones del navegador relacionadas con el portapapeles.

## 4. Contrato real de la API

### Crear un enlace

```http
POST /shorten
Content-Type: application/json

{"url": "https://www.example.com/articulo?lang=es"}
```

Respuesta **200**:

```json
{
  "short_code": "dfgBoG",
  "short_url": "http://localhost:8000/s/dfgBoG",
  "original_url": "https://www.example.com/articulo?lang=es"
}
```

Comportamiento observado:

- `short_code` tiene 6 caracteres alfanuméricos.
- `short_url` usa el host de la petición y la ruta `/s/{short_code}`.
- Si se envía la misma URL otra vez, se devuelve el mismo `short_code`
  (deduplicación).
- No se devuelve 201; la implementación responde 200.

### Resolver un enlace

```http
GET /s/dfgBoG
```

Responde **307** con la URL original en la cabecera `Location`. Un código
inexistente responde **404** con:

```json
{"detail": "Enlace corto no encontrado"}
```

### Entradas inválidas

FastAPI/Pydantic responde **422** con un arreglo `detail`, por ejemplo para
esquemas distintos de `http`/`https`, URLs malformadas, campos ausentes o URLs
de más de 2083 caracteres. El frontend traduce ese arreglo a un mensaje legible.

## 5. Pruebas

Desde la raíz del repositorio, sin necesidad de arrancar el servidor:

```powershell
backend\.venv\Scripts\python.exe -m pytest tests -q
```

O con el entorno activado:

```powershell
pytest tests -q
```

Las pruebas usan `TestClient` y una base SQLite en memoria con la dependencia
`get_db` sobrescrita, por lo que no escriben en `unishort.db` ni requieren un
servidor levantado manualmente. Cubren:

- raíz de la API y disponibilidad de OpenAPI;
- creación de enlaces, forma de la respuesta y código de 6 caracteres;
- deduplicación de URLs repetidas;
- códigos distintos para URLs distintas;
- redirección 307 y 404 para códigos inexistentes;
- entradas inválidas (esquema, URL malformada, campo ausente y URL demasiado
  larga);
- preflight CORS desde el origen del frontend.

## 6. Verificación manual en el navegador

1. Arranca el backend en el puerto 8000.
2. Arranca el frontend en el puerto 5500.
3. Abre <http://localhost:5500>.
4. Introduce `https://www.example.com/articulo?lang=es` y pulsa **Acortar URL**.
5. Comprueba que aparece la URL corta con la ruta `/s/{short_code}`.
6. Pulsa **Copiar** y verifica el mensaje de confirmación. Si el navegador
   bloquea el portapapeles, la interfaz muestra un aviso para copiar el enlace
   manualmente.
7. Pulsa **Abrir** y comprueba que se abre la URL original.
8. Repite la misma URL: debe mostrarse el mismo código.
9. Prueba `javascript:alert(1)` y una dirección malformada: no se debe crear
   ningún enlace y debe aparecer un mensaje de error.

## 7. Criterios de aceptación verificables

| Criterio | Comprobación |
|----------|--------------|
| Crear enlace | `POST /shorten` con URL válida responde 200 y devuelve los tres campos. |
| Deduplicar | Enviar dos veces la misma URL devuelve el mismo `short_code`. |
| Redirigir | `GET /s/{short_code}` responde 307 hacia la URL original. |
| Rechazar entradas inválidas | Esquemas no http/https y URLs malformadas responden 422 sin crear enlaces. |
| Interfaz | El formulario, copiar y abrir funcionan en el navegador. |
| Pruebas | `pytest tests -q` pasa sin un servidor levantado manualmente. |
| Persistencia | Los enlaces se guardan en `unishort.db` y sobreviven a un reinicio del backend. |

## 8. Fuera de alcance en esta versión

- Generación de códigos QR (el nombre y el subtítulo del proyecto la mencionan,
  pero aún no está implementada).
- Autenticación, roles y panel administrativo.
- Estadísticas avanzadas.
- Rate limiting.
- Migraciones de base de datos o PostgreSQL.
