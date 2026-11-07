// UniShort QR - Modelo C4 en Structurizr DSL (C1, C2 y C3)
// Render reproducible local/CI: python scripts/render_diagrams.py; conservar esta fuente.

workspace "UniShort QR" "Proyecto académico de acortamiento de enlaces y QR en el contexto de la Universidad Nacional de Loja; sin integración institucional" {

    model {

        usuario = person "Usuario académico" "Crea enlaces cortos, comparte la URL y usa el QR."
        administrador = person "Administrador técnico" "Usa el panel con clave provisional para consultar, buscar y modificar enlaces. Rol académico; no hay integración institucional."
        evaluador = person "Docente evaluador" "Verifica el incremento desde Swagger o el frontend."
        visitante = person "Visitante" "Abre una URL corta o escanea el QR; su navegador sigue Location."
        destino = softwareSystem "Recurso académico de destino" "Sitio externo abierto por el navegador. El backend no lo consulta." {
            tags "External"
        }

        unishort = softwareSystem "UniShort QR" "Acorta URL, redirige, genera QR y conserva contadores sin recopilar metadatos de visitantes." {

            frontend = container "Frontend web" "Acortador público index.html y panel admin.html. Clave solo en memoria; búsqueda, paginación, métricas y edición confirmada." "HTML/CSS/JavaScript; servidor estático Python o Nginx"

            api = container "Backend API" "API REST FastAPI con validación Pydantic y SQLAlchemy. Conserva endpoints heredados." "Python 3.11+, FastAPI, Uvicorn" {

                v1 = component "API v1" "Rutas /api/v1/links y /api/v1/admin/stats. Listado filtrado/paginado, resumen agregado, gestión protegida y QR público bajo demanda." "FastAPI Router"
                legacy = component "Compatibilidad heredada" "Rutas /shorten y /s/{short_code} con contrato anterior." "FastAPI Router"
                esquemas = component "Esquemas Pydantic" "Validación de entrada, envelope y modelos de respuesta." "Pydantic v2"
                servicios = component "Casos de uso" "Orquesta validación, creación, resolución, métricas y actualización." "Python"
                dominio = component "Dominio" "Reglas puras de URL, código corto, expiración y fechas UTC." "Python"
                repositorio = component "Repositorio" "Transacciones, unicidad, reintentos, contador atómico, búsqueda parametrizada y COUNT/SUM/CASE." "SQLAlchemy 2.x"
                seguridad = component "Control de acceso" "Clave administrativa provisional y comparación segura." "FastAPI Dependency"
                limite = component "Limitador de tasa" "Ventana fija efímera en memoria; la IP no se persiste." "Python"
                qr = component "Generador QR" "PNG cuyo contenido es la URL corta." "qrcode + Pillow"
            }

            db = container "Base de datos" "Tabla short_urls con estado, expiración y contador agregado. Alembic 0001-0003; PostgreSQL no implementado." "SQLite / SQLAlchemy 2.x" {
                tags "Database"
            }

        }

        usuario -> frontend "Usa"
        administrador -> frontend "Accede al panel, confirma cambios y cierra sesión"
        administrador -> api "Alternativa: administra desde Swagger con X-Admin-API-Key"
        evaluador -> frontend "Verifica el flujo"
        evaluador -> api "Inspecciona OpenAPI"
        visitante -> api "Solicita URL corta; recibe 307, 404 o 410" "HTTP/HTTPS; /s/{code}"
        visitante -> destino "El navegador sigue Location tras 307; no es una petición del backend" "HTTP/HTTPS"

        frontend -> api "Crea enlaces, solicita PNG, consulta resumen/lista y envía PATCH. Clave en cabecera solo para operaciones admin" "HTTP loopback / HTTPS remoto; /api/v1"
        api -> db "Lee y escribe enlaces" "SQLAlchemy"

        v1 -> esquemas "Valida entrada y compone salida"
        legacy -> esquemas "Reutiliza modelos heredados"
        v1 -> servicios "Invoca casos de uso"
        legacy -> servicios "Invoca resolución y creación heredada"
        servicios -> dominio "Aplica reglas puras"
        servicios -> repositorio "Persiste y consulta"
        repositorio -> dominio "Genera códigos y toma la referencia UTC"
        v1 -> seguridad "Protege operaciones administrativas"
        v1 -> limite "Limita la creación de enlaces"
        legacy -> limite "Comparte límite de creación con v1"
        v1 -> qr "Genera PNG de la URL corta"
        repositorio -> db "Usa la sesión de datos"
    }

    views {

        systemContext unishort "C1-Contexto" {
            include *
            include destino
            autoLayout lr
        }

        container unishort "C2-Contenedores" {
            include *
            include destino
            autoLayout lr
        }

        component api "C3-Componentes-backend" {
            include *
            autoLayout tb
        }

        styles {
            element "Person" {
                shape Person
                background "#08427b"
                color "#ffffff"
            }
            element "Software System" {
                background "#1168bd"
                color "#ffffff"
            }
            element "Container" {
                background "#438dd5"
                color "#ffffff"
            }
            element "Component" {
                background "#85bbf0"
                color "#000000"
            }
            element "Database" {
                shape Cylinder
                background "#438dd5"
                color "#ffffff"
            }
            element "External" {
                background "#999999"
                color "#ffffff"
            }
        }
    }
}
