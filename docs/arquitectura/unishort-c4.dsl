// UniShort QR - Modelo C4 en Structurizr DSL (C1, C2 y C3)
// Renderizar con Structurizr Lite/CLI o pegando el contenido en structurizr.com/dsl.

workspace "UniShort QR" "Servicio institucional de acortamiento de enlaces y QR para la Universidad Nacional de Loja" {

    model {

        usuario = person "Usuario académico" "Crea enlaces cortos, comparte la URL y usa el QR."
        administrador = person "Administrador DTI" "Desactiva enlaces y consulta métricas agregadas."
        evaluador = person "Docente evaluador" "Verifica el incremento desde Swagger o el frontend."

        identidad = softwareSystem "Identidad institucional (futuro)" "Proveedor OIDC de la UNL. No implementado en este incremento." {
            tags "External"
        }

        unishort = softwareSystem "UniShort QR" "Acorta URL, redirige, genera QR y conserva métricas agregadas sin datos personales." {

            frontend = container "Frontend web" "HTML, CSS y JavaScript estático. Consume /api/v1 y muestra el QR." "Navegador / http.server"

            api = container "Backend API" "API REST FastAPI con validación Pydantic y SQLAlchemy. Conserva endpoints heredados." "Python 3.11+, FastAPI, Uvicorn" {

                v1 = component "API v1" "Rutas /api/v1/links: crear, consultar, listar, actualizar, desactivar, métricas y QR." "FastAPI Router"
                legacy = component "Compatibilidad heredada" "Rutas /shorten y /s/{short_code} con contrato anterior." "FastAPI Router"
                esquemas = component "Esquemas Pydantic" "Validación de entrada, envelope y modelos de respuesta." "Pydantic v2"
                servicios = component "Casos de uso" "Orquesta validación, creación, resolución, métricas y actualización." "Python"
                dominio = component "Dominio" "Reglas puras de URL, código corto, expiración y fechas UTC." "Python"
                repositorio = component "Repositorio" "Transacciones, unicidad, reintento por colisión y contador atómico." "SQLAlchemy 2.x"
                seguridad = component "Control de acceso" "Clave administrativa provisional y comparación segura." "FastAPI Dependency"
                limite = component "Limitador de tasa" "Ventana fija efímera en memoria; la IP no se persiste." "Python"
                qr = component "Generador QR" "PNG cuyo contenido es la URL corta." "qrcode + Pillow"
            }

            db = container "Base de datos" "Tabla short_urls con estado, expiración y contador agregado." "SQLite (desarrollo) / PostgreSQL (futuro)" {
                tags "Database"
            }

            proxy = container "Proxy HTTPS (futuro)" "Terminación TLS y límite de tasa perimetral." "Nginx / reverse proxy" {
                tags "External"
            }
        }

        usuario -> frontend "Usa"
        administrador -> api "Administra con X-Admin-API-Key"
        evaluador -> frontend "Verifica el flujo"
        evaluador -> api "Inspecciona OpenAPI"

        frontend -> api "Envía JSON y solicita QR" "HTTPS /api/v1"
        proxy -> api "Enruta el tráfico" "HTTPS"
        api -> db "Lee y escribe enlaces" "SQLAlchemy"
        api -> identidad "Autenticación institucional futura" "OIDC (futuro)"

        v1 -> esquemas "Valida entrada y compone salida"
        legacy -> esquemas "Reutiliza modelos heredados"
        v1 -> servicios "Invoca casos de uso"
        legacy -> servicios "Invoca resolución y creación heredada"
        servicios -> dominio "Aplica reglas puras"
        servicios -> repositorio "Persiste y consulta"
        v1 -> seguridad "Protege operaciones administrativas"
        v1 -> limite "Limita la creación de enlaces"
        v1 -> qr "Genera PNG de la URL corta"
        repositorio -> db "Usa la sesión de datos"
    }

    views {

        systemContext unishort "C1-Contexto" {
            include *
            autoLayout lr
        }

        container unishort "C2-Contenedores" {
            include *
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
