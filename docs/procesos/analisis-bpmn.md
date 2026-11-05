# Análisis BPMN 2.0.2: creación y uso de un enlace corto

**Proceso:** crear un enlace corto, generar su QR y redirigir al destino.
**Versión del estándar:** BPMN 2.0.2.
**Artefacto:** [`creacion-enlace.bpmn`](creacion-enlace.bpmn).

## 1. Objetivo del proceso

Permitir que una persona usuaria transforme una URL académica extensa en una
URL corta única, obtenga un código QR que representa esa URL corta y pueda
acceder al destino original mediante el enlace o el QR, respetando reglas de
validación, caducidad, desactivación y privacidad.

## 2. Participantes y carriles

| Participante / carril | Responsabilidad |
|-----------------------|-----------------|
| Usuario académico | Introduce la URL, recibe el enlace y accede a él. |
| API UniShort QR | Valida, aplica reglas, genera el código, persiste y redirige. |
| Servicio QR | Genera y entrega el PNG que contiene la URL corta. |
| Administrador DTI | Desactiva enlaces y consulta métricas (proceso administrativo relacionado). |

## 3. Eventos

- **Evento de inicio:** necesidad de compartir un recurso académico.
- **Eventos de fin exitoso:** enlace entregado; redirección completada.
- **Eventos de fin con error:** URL inválida; fallo de persistencia; enlace
  desactivado o caducado.
- **Eventos intermedios implícitos:** colisión de código detectada; enlace no
  utilizable.

## 4. Actividades (verbos en infinitivo)

1. Introducir la URL de destino.
2. Validar la solicitud (esquema, host, longitud, credenciales, expiración).
3. Aplicar reglas de negocio (normalizar, comprobar estado).
4. Generar un código corto único.
5. Persistir el enlace y su estado.
6. Generar el código QR con la URL corta.
7. Entregar el enlace corto y el QR.
8. Acceder mediante el enlace o el QR.
9. Resolver el código corto.
10. Comprobar la usabilidad del enlace.
11. Registrar el clic agregado.
12. Redirigir al destino original.
13. Devolver un error de validación.
14. Devolver un error de persistencia.
15. Devolver un error por enlace no disponible.

## 5. Decisiones (compuertas exclusivas)

| Decisión | Condición | Camino |
|----------|-----------|--------|
| ¿URL válida? | Esquema http/https, host, longitud, sin credenciales | Sí: aplicar reglas. No: error 4xx. |
| ¿Código libre? | El código no existe en la base | Sí: persistir. No: regenerar (máximo 10). |
| ¿Persistencia correcta? | Commit confirmado | Sí: generar QR. No: revertir y 5xx. |
| ¿Enlace activo y vigente? | `is_active` y `expires_at` | Sí: redirigir. No: 410. |

## 6. Flujos y datos

- **Flujo principal:** inicio → introducir URL → validar → reglas → generar
  código → persistir → generar QR → entregar → acceder → resolver → comprobar →
  registrar clic → redirigir → fin.
- **Datos de entrada:** URL, fecha de expiración opcional, clave administrativa
  si la operación es administrativa.
- **Datos persistidos:** `short_code`, `original_url`, `created_at`,
  `is_active`, `expires_at`, `click_count`.
- **Datos de salida:** `short_code`, `short_url`, `original_url`, `qr_url`,
  estado y contador agregado.
- **Datos NO persistidos:** IP del visitante, User-Agent, cookies, correo,
  nombre o identificadores de sesión.

## 7. Excepciones

| Excepción | Tratamiento |
|-----------|-------------|
| URL vacía, malformada, esquema no permitido, credenciales o longitud excesiva | 422/400 con envelope y sin crear enlace. |
| Colisión repetida tras 10 intentos | 409 `collision_unresolved`. |
| Fallo de base de datos al guardar | Rollback y 500 `persistence_failure`. |
| Código inexistente al redirigir | 404 `link_not_found`. |
| Enlace desactivado | 410 `link_inactive`, sin redirección. |
| Enlace caducado | 410 `link_expired`, sin redirección. |
| Límite de creación superado | 429 `rate_limit_exceeded` con `Retry-After`. |
| Operación administrativa sin credencial | 401/403/503 según configuración. |

## 8. Reglas de negocio asociadas

- Cada envío genera un enlace nuevo; no se deduplica la URL.
- El código corto es único por restricción de base de datos.
- El QR codifica la URL corta, nunca la URL de destino.
- La redirección solo ocurre para enlaces activos y no caducados.
- El contador de clics es agregado; no se guardan eventos individuales.

## 9. Correspondencia con la implementación

| Elemento BPMN | Implementación |
|---------------|----------------|
| Validar solicitud | `backend/app/domain.py`, `api/schemas.py` |
| Aplicar reglas / generar código | `backend/app/domain.py`, `services.py` |
| Persistir | `backend/app/repository.py` |
| Generar QR | `backend/app/qr.py`, `api/v1.py` |
| Resolver y redirigir | `backend/app/main.py`, `services.py` |
| Errores y envelope | `backend/app/main.py`, `api/envelope.py` |
| Métricas | `backend/app/repository.py` (`increment_click_count`) |
