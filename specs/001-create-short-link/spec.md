# Feature Specification: Generación de Enlaces Cortos y Código QR Académico (UNL)

**Feature Branch**: `001-create-short-link`  
**Created**: 2026-10-21  
**Refined**: 2026-10-22 (Refinamiento Práctica 002)  
**Status**: Approved  

---

## Contexto y Alcance del Incremento

**Descripción**: Permite a docentes y estudiantes de la Universidad Nacional de Loja (UNL) convertir URLs académicas extensas en un enlace corto único y generar automáticamente un código QR asociado descargable para su fácil difusión en entornos universitarios.

- **Funcionalidades Incluidas**: 
  - Validación de sintaxis y protocolo (HTTP/HTTPS) de la URL.
  - Generación de alias corto único (6 caracteres).
  - Almacenamiento duradero de la relación entre la URL corta y la original.
  - Generación automática de código QR codificado.
  - Definición de contratos preliminares para la API REST.
- **Funcionalidades Excluidas (Iteraciones futuras)**: 
  - Autenticación avanzada/SSO institucional de la UNL.
  - Analítica detallada de clics y geolocalización.

---

## User Scenarios & Acceptance Criteria

### User Story 1 - Crear un enlace corto y código QR a partir de una URL válida (Priority: P1)

**Como** usuario del sistema (docente/estudiante de la UNL),  
**Quiero** ingresar una URL académica válida,  
**Para** obtener una URL corta única y su código QR asociado que faciliten su difusión en medios impresos o digitales.

**Why this priority**: Es la funcionalidad principal del proyecto. Sin ella, no existe el servicio de acortamiento ni la generación de artefactos académicos (QR).

**Independent Test**: Enviar una URL válida y verificar que la respuesta HTTP 201 contenga el código corto, la URL corta, la URL original y la ubicación del código QR generado.

**Acceptance Scenarios**:

1. **Given** una URL válida con esquema `https` o `http` y host correcto (ejemplo: `https://unl.edu.ec/recurso/123`),  
   **When** el usuario solicita crear el enlace,  
   **Then** la respuesta incluye el código corto, la URL corta, la URL original y el enlace a la imagen del QR, guardando la relación en la base de datos.
2. **Given** un enlace y QR recién creados,  
   **When** el servicio se reinicia,  
   **Then** la relación entre el código corto, la URL original y el QR persiste sin perderse.
3. **Given** una URL original que ya fue acortada anteriormente,  
   **When** el usuario envía la misma URL de nuevo,  
   **Then** se genera un nuevo enlace corto único con su respectivo QR independiente.
4. **Given** la generación exitosa de la URL corta,  
   **When** se solicita la imagen del código QR asociado,  
   **Then** el QR escaneado redirige exactamente al enlace corto generado.

---

### User Story 2 - Recibir un error claro cuando la creación no puede completarse (Priority: P2)

**Como** usuario,  
**Quiero** recibir un mensaje de error claro al ingresar una entrada no válida,  
**Para** corregir la URL o entender por qué falló la solicitud.

**Acceptance Scenarios**:

1. **Given** una cadena vacía o espacios en blanco, **When** se solicita crear el enlace, **Then** responde un error HTTP 400 identificando el campo.
2. **Given** una URL con esquema no permitido (`ftp://`, `javascript:`), **When** se solicita acortar, **Then** responde error HTTP 400 sin crear registros.
3. **Given** una URL con credenciales embebidas (`https://user:pass@host`), **When** se procesa, **Then** se rechaza con error HTTP 400 por seguridad.
4. **Given** que el almacenamiento no esté disponible, **When** se intenta crear el enlace, **Then** responde error HTTP 500 sin guardar datos parciales.

---

### User Story 3 - Garantizar unicidad del código corto (Priority: P3)

**Como** usuario,  
**Quiero** que mi enlace corto sea único,  
**Para** no cruzar mi recurso académico con el de otra persona.

**Acceptance Scenarios**:

1. **Given** dos URLs distintas creadas, **When** se procesan, **Then** los códigos cortos emitidos son totalmente diferentes.
2. **Given** una colisión aleatoria de códigos, **When** el sistema la detecta, **Then** genera automáticamente un nuevo código corto único sin sobrescribir el anterior.

---

## Requirements

### Functional Requirements (FR)

- **FR-001**: El sistema DEBE validar que la URL original ingresada sea una URL absoluta con esquema `http` o `https` y longitud máxima de 2.048 caracteres.
- **FR-002**: El sistema DEBE asignar a cada URL corta un identificador único de 6 caracteres alfanuméricos.
- **FR-003**: El sistema DEBE generar automáticamente un código QR correspondiente a la URL corta generada.
- **FR-004**: El sistema DEBE conservar la relación entre el código corto, la URL original y el QR de forma persistente.
- **FR-005**: El sistema DEBE rechazar las peticiones inválidas enviando un código de estado HTTP 4xx descriptivo.
- **FR-006**: El sistema DEBE responder con HTTP 5xx ante fallos de persistencia sin confirmar la creación del enlace.

### Non-Functional Requirements (NFR)

- **RNF-001 (Rendimiento)**: El tiempo total de procesamiento (acortamiento + generación de QR) DEBE ser inferior a 500 ms en el percentil 95.
- **RNF-002 (Estándares Web)**: La API DEBE ser compatible con HTTP Semantics (RFC 9110) y responder en formato JSON.
- **RNF-003 (Privacidad)**: El sistema NO DEBE almacenar cookies, direcciones IP ni datos de sesión de los usuarios.

---

## Contratos Preliminares de la API (Preliminary Contracts)

### Operación 1: Crear Enlace Corto y Código QR

* **Recurso**: `/api/v1/shorten`
* **Método HTTP**: `POST`
* **Cabeceras**: `Content-Type: application/json`
* **Cuerpo de Entrada (JSON)**:
  ```json
  {
    "target_url": "https://unl.edu.ec/biblioteca/recursos/articulo-investigacion"
  }