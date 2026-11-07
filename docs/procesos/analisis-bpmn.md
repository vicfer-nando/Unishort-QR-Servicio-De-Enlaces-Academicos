# Análisis BPMN 2.0.2: creación y uso de un enlace corto

**Procesos:** crear enlace, obtener QR bajo demanda, redirigir y administrar.
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
| Biblioteca QR local | Se ejecuta dentro del backend, sin servicio remoto ni persistencia de imágenes. |
| Administrador técnico | Usa el panel con clave compartida provisional; no acredita un rol institucional DTI. |

## 3. Eventos

- **Evento de inicio:** necesidad de compartir un recurso académico.
- **Eventos de inicio independientes:** enviar URL, pedir PNG, abrir URL corta,
  necesitar administrar. Cada uno corresponde a una petición o sesión distinta.
- **Eventos de fin exitoso:** enlace entregado, PNG entregado, redirección
  comunicada al navegador o sesión administrativa cerrada.
- **Eventos de fin con error:** URL inválida; fallo de persistencia; enlace
  desactivado o caducado.
- Colisión y usabilidad se representan mediante decisiones, no se presentan como
  eventos BPMN intermedios que el XML no contiene. Modelo descriptivo no ejecutable.

## 4. Actividades (verbos en infinitivo)

1. Introducir la URL de destino.
2. Validar la solicitud (esquema, host, longitud, credenciales, expiración).
3. Aplicar reglas de negocio (normalizar, comprobar estado).
4. Generar un código corto único.
5. Persistir el enlace y su estado.
6. Devolver 201 con URL corta y qr_url, sin generar imagen.
7. Solicitar QR en una petición GET posterior y generar PNG con la URL corta.
8. Acceder mediante el enlace o el QR.
9. Resolver el código corto.
10. Comprobar la usabilidad del enlace.
11. Registrar el clic agregado.
12. Redirigir al destino original.
13. Devolver un error de validación.
14. Devolver un error de persistencia.
15. Devolver un error por enlace no disponible.
16. Introducir clave provisional y validar acceso mediante el listado protegido.
17. Consultar resumen SQL y lista con búsqueda, filtros y paginación.
18. Editar estado o caducidad y confirmar cambios.
19. Revalidar clave y aplicar PATCH; refrescar o mostrar error sin secretos.
20. Cerrar sesión y descartar la clave local, cancelando solicitudes pendientes.

## 5. Decisiones (compuertas exclusivas)

| Decisión | Condición | Camino |
|----------|-----------|--------|
| ¿URL válida? | Esquema http/https, host, longitud, sin credenciales | Sí: aplicar reglas. No: error 4xx. |
| ¿Código libre? | El código no existe en la base | Sí: persistir. No: regenerar (máximo 10). |
| ¿Resultado de persistencia? | Commit, colisión o fallo distinto | Commit: 201 JSON; colisión: rollback y reintento acotado; otro fallo: rollback/500. |
| ¿Enlace activo y vigente? | `is_active` y `expires_at` | Sí: redirigir. No: 410. |
| ¿Código existente? | Consulta por código | Sí: comprobar estado; no: 404 (formato heredado en redirección). |
| ¿Clave autorizada? | Comparación en servidor | Sí: consultar; no: 401/403/503, sin datos administrativos. |
| ¿Confirmar cambios? | Confirmación del diálogo | Sí: PATCH protegido; no: volver a la lista sin escritura. |
| ¿Error de autenticación? | 401/403/503 en gestión | Cerrar sesión local; otros errores: informar y permitir corregir/reintentar. |

## 6. Flujos y datos

- **Crear:** introducir URL → validar/límite → generar código → intentar insertar →
  resolver colisiones hasta diez intentos → commit → devolver 201 con qr_url → fin.
- **QR:** solicitar PNG → buscar y comprobar estado → generar en memoria → entregar
  image/png → fin. No aumenta visitas ni forma parte de la transacción de creación.
- **Redirigir:** recibir código → buscar → comprobar estado → intentar incrementar
  contador → devolver 307/Location → fin. El navegador sigue el destino; API no lo descarga.
- **Administrar:** introducir clave → GET listado protegido → resumen/lista → buscar
  o gestionar → confirmar → PATCH autorizado → refrescar. Cancelar no escribe;
  logout/pagehide borran clave de memoria. No hay eliminación física.
- **Datos de entrada:** URL, fecha de expiración opcional, clave administrativa
  si la operación es administrativa.
- **Datos persistidos:** `short_code`, `original_url`, `created_at`,
  `is_active`, `expires_at`, `click_count`.
- **Datos de salida:** `short_code`, `short_url`, `original_url`, `qr_url`,
  estado y contador agregado.
- **Datos NO persistidos:** IP del visitante, User-Agent, cookies, correo,
  nombre o identificadores de sesión.
- No se solicitan esos metadatos; una URL original arbitraria podría contener datos
  sensibles. No se promete que el contenido ingresado esté libre de información personal.

## 7. Excepciones

| Excepción | Tratamiento |
|-----------|-------------|
| URL vacía, malformada, esquema no permitido, credenciales o longitud excesiva | 422/400 con envelope y sin crear enlace. |
| Colisión repetida tras 10 intentos | 409 `collision_unresolved`. |
| Fallo de base de datos al guardar | Rollback y 500 `persistence_failure`. |
| Código inexistente al redirigir | 404 detail heredado; en GET de metadatos/QR v1 usa envelope link_not_found. |
| Enlace desactivado | 410 `link_inactive`, sin redirección. |
| Enlace caducado | 410 `link_expired`, sin redirección. |
| Límite de creación superado | 429 `rate_limit_exceeded` con `Retry-After`. |
| Operación administrativa sin credencial | 401/403/503 según configuración. |
| Error al generar PNG | 500 controlado; el enlace previamente creado se conserva. |
| Error al incrementar visitas | Se registra sin datos sensibles y se mantiene la redirección: contador de mejor esfuerzo. |
| Fecha pasada al editar | 422 sin aplicar cambios; habilitar no borra una caducidad vencida. |

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
| Panel y confirmación | `frontend/admin.mjs`, `api/deps.py`, `api/v1.py` |
| Búsqueda, paginación y resumen | `services.py`, `repository.py`, `get_admin_stats` |

## 10. Fuentes y verificación

El XML contiene cuatro procesos y cuatro diagramas DI, generados de forma local
por scripts/build_process_models.py. Las pruebas test_documentation_models.py
comprueban infinitivos, referencias recíprocas, límites de proceso, DI y orden
de elementos raíz. No equivalen a validación XSD completa ni inspección visual
en un modelador BPMN. La evidencia actual y sus pendientes están en la auditoría final.
