"""Genera cuatro vistas BPMN de negocio con DI; no afirma validación por XSD."""

import xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
URIS = {
    "bpmn": "http://www.omg.org/spec/BPMN/20100524/MODEL",
    "bpmndi": "http://www.omg.org/spec/BPMN/20100524/DI",
    "dc": "http://www.omg.org/spec/DD/20100524/DC",
    "di": "http://www.omg.org/spec/DD/20100524/DI",
    "xsi": "http://www.w3.org/2001/XMLSchema-instance",
}
for prefix, uri in URIS.items():
    ET.register_namespace(prefix, uri)


def element(parent, tag, **attributes):
    """Añade un elemento del estándar con atributos explícitos."""
    prefix, local = tag.split(":")
    return ET.SubElement(parent, f"{{{URIS[prefix]}}}{local}", attributes)


def model(root, key, title, nodes, flows, documentation):
    """Compone proceso, carriles, conexiones recíprocas y su vista gráfica DI."""
    process_id = f"Process_{key}"
    collaboration = element(root, "bpmn:collaboration", id=f"Collaboration_{key}")
    element(
        collaboration,
        "bpmn:participant",
        id=f"Participant_{key}",
        name=title,
        processRef=process_id,
    )
    process = element(
        root, "bpmn:process", id=process_id, name=title, isExecutable="false"
    )
    element(process, "bpmn:documentation").text = documentation
    lane_set = element(process, "bpmn:laneSet", id=f"LaneSet_{key}")
    height = 200 + max(node[4] for node in nodes) * 120
    diagram = element(root, "bpmndi:BPMNDiagram", id=f"Diagram_{key}")
    plane = element(
        diagram,
        "bpmndi:BPMNPlane",
        id=f"Plane_{key}",
        bpmnElement=f"Collaboration_{key}",
    )
    shape(plane, f"Participant_{key}", 0, 20, 1700, height)
    lane_names = {
        "user": "Persona usuaria / administrador",
        "api": "Backend FastAPI y panel web",
        "qr": "Biblioteca QR local (mismo backend)",
    }
    for lane, (x, width) in {
        "user": (40, 320),
        "api": (360, 1000),
        "qr": (1360, 340),
    }.items():
        item = element(
            lane_set, "bpmn:lane", id=f"Lane_{key}_{lane}", name=lane_names[lane]
        )
        for node in nodes:
            if node[3] == lane:
                element(item, "bpmn:flowNodeRef").text = f"{key}_{node[0]}"
        shape(plane, f"Lane_{key}_{lane}", x, 20, width, height)
    positions = {}
    defaults = {
        source: f"{key}_flow_{index}"
        for index, (source, _, label) in enumerate(flows)
        if label == "Por defecto"
    }
    for name, tag, label, lane, level, branch in nodes:
        identity = f"{key}_{name}"
        item = element(process, f"bpmn:{tag}", id=identity, name=label)
        if name in defaults:
            item.set("default", defaults[name])
        for index, (source, target, _) in enumerate(flows):
            if target == name:
                element(item, "bpmn:incoming").text = f"{key}_flow_{index}"
            if source == name:
                element(item, "bpmn:outgoing").text = f"{key}_flow_{index}"
        width, node_height = (
            (36, 36)
            if tag.endswith("Event")
            else (54, 54)
            if tag.endswith("Gateway")
            else (230, 66)
        )
        center = {"user": 200, "api": 640 if not branch else 1100, "qr": 1520}[lane]
        x, y = center - width / 2, 80 + level * 120
        positions[name] = (center, y, width, node_height)
        drawing = shape(plane, identity, x, y, width, node_height)
        if tag.endswith("Gateway"):
            diagram_label = element(drawing, "bpmndi:BPMNLabel")
            label_x = x + width + 10 if lane == "user" else x - 190
            label_y = y - 48 if lane == "user" else y + 4
            element(
                diagram_label,
                "dc:Bounds",
                x=str(label_x),
                y=str(label_y),
                width="110" if lane == "user" else "180",
                height="42",
            )
    for index, (source, target, label) in enumerate(flows):
        identity = f"{key}_flow_{index}"
        flow = element(
            process,
            "bpmn:sequenceFlow",
            id=identity,
            sourceRef=f"{key}_{source}",
            targetRef=f"{key}_{target}",
        )
        if label:
            flow.set("name", label)
        edge = element(
            plane, "bpmndi:BPMNEdge", id=f"DI_{identity}", bpmnElement=identity
        )
        sx, sy, sw, sh = positions[source]
        tx, ty, tw, th = positions[target]
        points = [(sx, sy + sh), (tx, ty)]
        if ty < sy:
            bypass = 1300
            points = [
                (sx + sw / 2, sy + sh / 2),
                (bypass, sy + sh / 2),
                (bypass, ty - 20),
                (tx, ty - 20),
                (tx, ty),
            ]
            label_x, label_y = bypass - 155, (sy + sh / 2 + ty - 20) / 2
        elif ty - sy > 180:
            # Evitar que un salto atraviese tareas intermedias de la misma columna.
            bypass = 1300 if sx == tx else 860
            target_edge = tx + tw / 2 if bypass > tx else tx - tw / 2
            points = [
                (sx + sw / 2, sy + sh / 2),
                (bypass, sy + sh / 2),
                (bypass, ty + th / 2),
                (target_edge, ty + th / 2),
            ]
            label_x, label_y = bypass - 155, (sy + ty) / 2
        elif sx != tx:
            bend = (sy + sh + ty) / 2
            points = [(sx, sy + sh), (sx, bend), (tx, bend), (tx, ty)]
            label_x, label_y = (sx + tx) / 2 - 75, bend - 38
        else:
            label_x, label_y = sx + 12, (sy + sh + ty) / 2 - 12
        for x, y in points:
            element(edge, "di:waypoint", x=str(x), y=str(y))
        if label:
            diagram_label = element(edge, "bpmndi:BPMNLabel")
            element(
                diagram_label,
                "dc:Bounds",
                x=str(label_x),
                y=str(label_y),
                width="145",
                height="32",
            )


def shape(plane, identity, x, y, width, height):
    """Añade límites DI para poder abrir la fuente en un modelador BPMN."""
    result = element(
        plane, "bpmndi:BPMNShape", id=f"DI_{identity}", bpmnElement=identity
    )
    element(
        result, "dc:Bounds", x=str(x), y=str(y), width=str(width), height=str(height)
    )
    return result


def main():
    """Reconcilia las vistas públicas y administrativas con el código implementado."""
    root = ET.Element(
        f"{{{URIS['bpmn']}}}definitions",
        {
            "id": "Definitions_UniShort",
            "targetNamespace": "https://unishort.example/bpmn",
            "exporter": "UniShort QR",
            "exporterVersion": "2026-11-06",
        },
    )
    model(
        root,
        "Create",
        "Crear enlace corto (POST /api/v1/links)",
        [
            (
                "Start",
                "startEvent",
                "Necesidad de compartir un recurso",
                "user",
                0,
                False,
            ),
            (
                "Input",
                "userTask",
                "Introducir URL y caducidad opcional",
                "user",
                1,
                False,
            ),
            (
                "Validate",
                "serviceTask",
                "Validar solicitud y aplicar límite",
                "api",
                2,
                False,
            ),
            ("Valid", "exclusiveGateway", "¿Solicitud aceptada?", "api", 3, False),
            ("Generate", "serviceTask", "Generar código aleatorio", "api", 4, False),
            (
                "Persist",
                "serviceTask",
                "Intentar insertar y confirmar enlace",
                "api",
                5,
                False,
            ),
            (
                "Result",
                "exclusiveGateway",
                "¿Resultado de persistencia?",
                "api",
                6,
                False,
            ),
            (
                "Retry",
                "exclusiveGateway",
                "¿Quedan intentos de los diez?",
                "api",
                7,
                True,
            ),
            (
                "Return",
                "serviceTask",
                "Devolver 201 con URL corta y qr_url",
                "api",
                7,
                False,
            ),
            ("Display", "userTask", "Consultar enlace creado", "user", 8, False),
            ("End", "endEvent", "Enlace creado sin generar PNG", "user", 9, False),
            (
                "Invalid",
                "serviceTask",
                "Devolver 400, 422 o 429 sin insertar",
                "api",
                4,
                True,
            ),
            ("InvalidEnd", "endEvent", "Solicitud rechazada", "api", 5, True),
            (
                "Conflict",
                "serviceTask",
                "Devolver 409 tras agotar colisiones",
                "api",
                8,
                True,
            ),
            (
                "Failure",
                "serviceTask",
                "Revertir y devolver error 500",
                "api",
                10,
                True,
            ),
            ("FailureEnd", "endEvent", "Creación no confirmada", "api", 11, True),
        ],
        [
            ("Start", "Input", ""),
            ("Input", "Validate", ""),
            ("Validate", "Valid", ""),
            ("Valid", "Generate", "Aceptada"),
            ("Valid", "Invalid", "Por defecto"),
            ("Invalid", "InvalidEnd", ""),
            ("Generate", "Persist", ""),
            ("Persist", "Result", ""),
            ("Result", "Return", "Commit confirmado"),
            ("Result", "Retry", "IntegrityError y rollback"),
            ("Result", "Failure", "Por defecto"),
            ("Retry", "Generate", "Intentos < 10"),
            ("Retry", "Conflict", "Por defecto"),
            ("Conflict", "FailureEnd", ""),
            ("Failure", "FailureEnd", ""),
            ("Return", "Display", ""),
            ("Display", "End", ""),
        ],
        "Flujo público sin autenticación. Unicidad en SQL; hasta diez intentos. Devuelve qr_url, no PNG. No se consulta el destino.",
    )
    model(
        root,
        "QR",
        "Obtener PNG bajo demanda (GET /api/v1/links/{code}/qr)",
        [
            (
                "Start",
                "startEvent",
                "Necesidad de ver o descargar QR",
                "user",
                0,
                False,
            ),
            ("Request", "userTask", "Solicitar código QR", "user", 1, False),
            (
                "Resolve",
                "serviceTask",
                "Resolver código y comprobar estado",
                "api",
                2,
                False,
            ),
            (
                "Usable",
                "exclusiveGateway",
                "¿Enlace existente, activo y vigente?",
                "api",
                3,
                False,
            ),
            ("Generate", "serviceTask", "Generar PNG con la URL corta", "qr", 4, False),
            (
                "Deliver",
                "serviceTask",
                "Entregar PNG sin incrementar visitas",
                "api",
                5,
                False,
            ),
            ("End", "endEvent", "PNG disponible", "user", 6, False),
            ("Error", "serviceTask", "Devolver 404 o 410 con envelope", "api", 4, True),
            ("ErrorEnd", "endEvent", "QR rechazado", "api", 5, True),
        ],
        [
            ("Start", "Request", ""),
            ("Request", "Resolve", ""),
            ("Resolve", "Usable", ""),
            ("Usable", "Generate", "Sí"),
            ("Usable", "Error", "Por defecto"),
            ("Generate", "Deliver", ""),
            ("Deliver", "End", ""),
            ("Error", "ErrorEnd", ""),
        ],
        "Solicitud independiente de la creación. Biblioteca QR en el mismo backend; contenido igual a short_url. Fallo de generación: 500 controlado.",
    )
    model(
        root,
        "Redirect",
        "Redirigir enlace corto (GET /s/{code})",
        [
            (
                "Start",
                "startEvent",
                "Acceso al enlace corto o QR escaneado",
                "user",
                0,
                False,
            ),
            ("Resolve", "serviceTask", "Resolver código corto", "api", 1, False),
            ("Found", "exclusiveGateway", "¿Código existente?", "api", 2, False),
            ("Usable", "exclusiveGateway", "¿Activo y no caducado?", "api", 3, False),
            (
                "Count",
                "serviceTask",
                "Intentar incrementar contador agregado",
                "api",
                4,
                False,
            ),
            (
                "Redirect",
                "serviceTask",
                "Redirigir con 307 y Location",
                "api",
                5,
                False,
            ),
            ("End", "endEvent", "Destino comunicado al navegador", "user", 6, False),
            ("Missing", "serviceTask", "Devolver 404 heredado", "api", 3, True),
            ("Gone", "serviceTask", "Devolver 410 con envelope", "api", 4, True),
            ("ErrorEnd", "endEvent", "Redirección rechazada", "api", 6, True),
        ],
        [
            ("Start", "Resolve", ""),
            ("Resolve", "Found", ""),
            ("Found", "Usable", "Sí"),
            ("Found", "Missing", "Por defecto"),
            ("Missing", "ErrorEnd", ""),
            ("Usable", "Count", "Sí"),
            ("Usable", "Gone", "Por defecto"),
            ("Gone", "ErrorEnd", ""),
            ("Count", "Redirect", "Contador de mejor esfuerzo"),
            ("Redirect", "End", ""),
        ],
        "No se obtiene contenido del destino. Un error del contador se registra sin PII y no impide redirigir. Nunca se persisten eventos individuales.",
    )
    model(
        root,
        "Admin",
        "Consultar y gestionar desde el panel administrativo",
        [
            (
                "Start",
                "startEvent",
                "Necesidad de administrar enlaces",
                "user",
                0,
                False,
            ),
            (
                "Key",
                "userTask",
                "Introducir clave provisional en memoria",
                "user",
                1,
                False,
            ),
            (
                "Authenticate",
                "serviceTask",
                "Validar clave en GET protegido del listado",
                "api",
                2,
                False,
            ),
            (
                "Authorized",
                "exclusiveGateway",
                "¿Clave autorizada por el backend?",
                "api",
                3,
                False,
            ),
            (
                "Query",
                "serviceTask",
                "Consultar resumen SQL y lista paginada",
                "api",
                4,
                False,
            ),
            (
                "View",
                "userTask",
                "Consultar enlaces con búsqueda y filtros",
                "user",
                5,
                False,
            ),
            (
                "Action",
                "exclusiveGateway",
                "¿Gestionar o cerrar sesión?",
                "user",
                6,
                False,
            ),
            ("Edit", "userTask", "Editar estado o caducidad", "user", 7, False),
            ("Confirm", "exclusiveGateway", "¿Confirmar cambios?", "user", 8, False),
            (
                "Patch",
                "serviceTask",
                "Revalidar clave y aplicar PATCH validado",
                "api",
                9,
                False,
            ),
            ("Saved", "exclusiveGateway", "¿Cambio confirmado?", "api", 10, False),
            (
                "Error",
                "serviceTask",
                "Mostrar error sin revelar credenciales",
                "api",
                11,
                True,
            ),
            (
                "ErrorKind",
                "exclusiveGateway",
                "¿Error de autenticación?",
                "api",
                12,
                True,
            ),
            (
                "Logout",
                "userTask",
                "Cerrar sesión y descartar clave local",
                "user",
                12,
                False,
            ),
            ("End", "endEvent", "Sesión local terminada", "user", 13, False),
            (
                "Denied",
                "serviceTask",
                "Mostrar 401, 403 o 503 y borrar clave",
                "api",
                4,
                True,
            ),
            ("DeniedEnd", "endEvent", "Acceso rechazado", "api", 5, True),
        ],
        [
            ("Start", "Key", ""),
            ("Key", "Authenticate", ""),
            ("Authenticate", "Authorized", ""),
            ("Authorized", "Query", "Sí"),
            ("Authorized", "Denied", "Por defecto"),
            ("Denied", "DeniedEnd", ""),
            ("Query", "View", ""),
            ("View", "Action", ""),
            ("Action", "Edit", "Gestionar"),
            ("Action", "Logout", "Por defecto"),
            ("Edit", "Confirm", ""),
            ("Confirm", "Patch", "Confirmar"),
            ("Confirm", "View", "Por defecto"),
            ("Patch", "Saved", ""),
            ("Saved", "Query", "Sí: refrescar"),
            ("Saved", "Error", "Por defecto"),
            ("Error", "ErrorKind", ""),
            ("ErrorKind", "View", "Por defecto"),
            ("ErrorKind", "Logout", "401 / 403 / 503"),
            ("Logout", "End", ""),
        ],
        "X-Admin-API-Key solo en cabecera. Estado/fecha no cambian el destino. Sin eliminación física. Logout cancela peticiones; cada operación exige autorización en servidor. Copiar/abrir/QR son acciones auxiliares descritas en el análisis.",
    )
    # BPMN exige elementos raíz antes de la secuencia de diagramas DI.
    for diagram in list(root.findall(f"{{{URIS['bpmndi']}}}BPMNDiagram")):
        root.remove(diagram)
        root.append(diagram)
    ET.indent(root, space="  ")
    target = ROOT / "docs/procesos/creacion-enlace.bpmn"
    ET.ElementTree(root).write(target, encoding="utf-8", xml_declaration=True)
    print(
        "BPMN generado: creación, QR diferido, redirección y administración; DI incluido."
    )


if __name__ == "__main__":
    main()
