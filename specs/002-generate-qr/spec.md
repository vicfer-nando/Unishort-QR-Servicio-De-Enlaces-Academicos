# Feature Specification: Generar y consultar códigos QR

**Feature Branch**: `002-generate-qr`

**Created**: 2026-11-05

**Status**: Implemented

**Input**: Incremento de la Evaluación Sumativa 1. La generación de QR quedó
explícitamente fuera del alcance de `001-create-short-link`; esta especificación
la incorpora como evolución del servicio existente.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Obtener un QR que represente el enlace corto (Priority: P1)

Como usuario, quiero obtener un código QR de mi enlace corto para imprimirlo o
colocarlo en material académico sin transcribir la URL.

**Why this priority**: El QR es el valor diferencial del producto frente a un
acortador tradicional. Sin él, el incremento no cumple su nombre ni el flujo de
uso previsto.

**Independent Test**: Crear un enlace, solicitar `GET
/api/v1/links/{short_code}/qr`, decodificar el PNG y comprobar que el contenido
es exactamente la URL corta.

**Acceptance Scenarios**:

1. **Given** un enlace activo, **When** se solicita su QR, **Then** la respuesta
   es `200` con `Content-Type: image/png` y un PNG válido.
2. **Given** el PNG obtenido, **When** se decodifica, **Then** el texto leído es
   la URL corta construida con `UNISHORT_BASE_URL`, no la URL de destino.
3. **Given** un enlace creado con expiración futura, **When** se solicita su QR,
   **Then** el QR se genera y sigue apuntando a la URL corta.
4. **Given** un enlace desactivado o caducado, **When** se solicita su QR,
   **Then** la respuesta es `410` con envelope y no se entrega una imagen.
5. **Given** un código inexistente, **When** se solicita su QR, **Then** la
   respuesta es `404` con envelope y no se entrega una imagen.

---

### User Story 2 - Usar el QR desde el frontend (Priority: P2)

Como persona evaluadora, quiero ver y descargar el QR desde la interfaz web para
verificar el flujo completo sin herramientas externas.

**Why this priority**: Facilita la demostración y reduce pasos manuales, pero
depende de que el endpoint de QR ya exista.

**Independent Test**: Abrir el frontend, crear un enlace y comprobar que la
imagen del QR se muestra y que el botón de descarga guarda un PNG.

**Acceptance Scenarios**:

1. **Given** una creación exitosa, **When** el frontend recibe la respuesta,
   **Then** muestra la imagen del QR y permite descargarla.
2. **Given** un error de creación, **When** el frontend recibe el envelope de
   error, **Then** muestra el mensaje sin intentar renderizar un QR.

---

### Edge Cases

- Código con caracteres no permitidos o longitud anormal: se trata como
  inexistente (`404`) sin consultar destinos externos.
- Enlace caducado por fecha pasada: `410 link_expired`.
- Enlace desactivado: `410 link_inactive`.
- Falla la generación de la imagen: `500` controlado, sin exponer trazas.
- Base URL mal configurada: el QR contiene la URL corta resultante; la
  configuración es responsabilidad del despliegue.

## Requirements *(mandatory)*

- **FR-001**: El sistema DEBE exponer `GET /api/v1/links/{short_code}/qr`.
- **FR-002**: La respuesta exitosa DEBE ser un PNG válido con
  `Content-Type: image/png`.
- **FR-003**: El contenido codificado DEBE ser exactamente la URL corta
  (`{UNISHORT_BASE_URL}/s/{short_code}`), nunca la URL original.
- **FR-004**: El QR DEBE ser decodificable por un lector estándar; las pruebas
  automatizadas DEBEN verificarlo.
- **FR-005**: Un código inexistente DEBE responder `404` y uno desactivado o
  caducado `410`, ambos con el envelope común, sin generar imagen.
- **FR-006**: La consulta del QR NO DEBE incrementar `click_count`; solo el
  acceso efectivo al enlace cuenta como clic.
- **FR-007**: La generación NO DEBE consultar la URL de destino ni almacenar
  datos personales de quien solicita el QR.
- **FR-008**: El tamaño del módulo y el borde DEBEN ser configurables por
  entorno (`UNISHORT_QR_BOX_SIZE`, `UNISHORT_QR_BORDER`).
- **FR-009**: El frontend DEBE mostrar y permitir descargar el QR usando la
  `qr_url` devuelta por la API.

### Key Entities

- **Enlace corto**: código, URL original, URL corta, estado y expiración. El QR
  se deriva de la URL corta y no se almacena como archivo.
- **Imagen QR**: artefacto efímero generado en memoria; no se persiste.

## Success Criteria *(mandatory)*

- **SC-001**: El 100 % de los enlaces activos probados genera un PNG que un
  decodificador estándar puede leer como su URL corta.
- **SC-002**: El 100 % de los códigos inexistentes, inactivos o caducados
  probados no recibe una imagen y obtiene el estado HTTP esperado.
- **SC-003**: Ninguna prueba automatizada de QR depende de la red pública.
- **SC-004**: La descarga y visualización del QR funciona en el frontend sin
  pasos manuales adicionales.

## Assumptions

- El QR se genera bajo demanda; no se almacena en la base de datos.
- El contenido del QR usa la URL corta porque es estable y no expone la URL
  original en el material impreso.
- La configuración de tamaño y borde tiene valores por defecto razonables y no
  requiere intervención para la demostración.
- El endpoint de QR no es administrativo: cualquier persona con el código puede
  obtener la imagen de un enlace activo.
