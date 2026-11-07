"""Integridad del modelo BPMN utilizado como evidencia técnica editable."""

import re
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
NS = {
    "b": "http://www.omg.org/spec/BPMN/20100524/MODEL",
    "di": "http://www.omg.org/spec/BPMN/20100524/DI",
}


def test_bpmn_models_four_real_flows_and_uses_infinitive_tasks():
    root = ET.parse(ROOT / "docs/procesos/creacion-enlace.bpmn").getroot()
    processes = root.findall("b:process", NS)
    assert len(processes) == 4
    for process in processes:
        assert process.get("isExecutable") == "false"
    tasks = [
        element
        for element in root.iter()
        if element.tag.split("}")[-1].endswith("Task")
    ]
    assert tasks
    assert all(
        re.match(r"\w+(?:ar|er|ir)\s+\S", task.get("name", "")) for task in tasks
    )


def test_bpmn_references_flows_reciprocally_and_has_complete_di():
    root = ET.parse(ROOT / "docs/procesos/creacion-enlace.bpmn").getroot()
    by_id = {element.get("id"): element for element in root.iter() if element.get("id")}
    shapes = {
        element.get("bpmnElement") for element in root.findall(".//di:BPMNShape", NS)
    }
    edges = {
        element.get("bpmnElement") for element in root.findall(".//di:BPMNEdge", NS)
    }
    for flow in root.findall(".//b:sequenceFlow", NS):
        assert flow.get("id") in edges
        source, target = by_id[flow.get("sourceRef")], by_id[flow.get("targetRef")]
        assert flow.get("id") in [
            item.text for item in source.findall("b:outgoing", NS)
        ]
        assert flow.get("id") in [
            item.text for item in target.findall("b:incoming", NS)
        ]
    for process in root.findall("b:process", NS):
        for element in process:
            tag = element.tag.split("}")[-1]
            if tag.endswith(("Task", "Event", "Gateway")):
                assert element.get("id") in shapes
            if element.get("default"):
                assert element.get("default") in [
                    item.text for item in element.findall("b:outgoing", NS)
                ]


def test_bpmn_root_order_and_process_scoped_references():
    root = ET.parse(ROOT / "docs/procesos/creacion-enlace.bpmn").getroot()
    diagrams_started = False
    for element in root:
        if element.tag == f"{{{NS['di']}}}BPMNDiagram":
            diagrams_started = True
        else:
            assert not diagrams_started, "Los elementos raíz BPMN deben preceder al DI"
    for process in root.findall("b:process", NS):
        local_ids = {element.get("id") for element in process.iter()}
        for flow in process.findall("b:sequenceFlow", NS):
            assert flow.get("sourceRef") in local_ids
            assert flow.get("targetRef") in local_ids
        for lane_ref in process.findall(".//b:flowNodeRef", NS):
            assert lane_ref.text in local_ids


def test_gateway_labels_are_explicit_and_outside_the_diamond():
    root = ET.parse(ROOT / "docs/procesos/creacion-enlace.bpmn").getroot()
    bounds_tag = "{http://www.omg.org/spec/DD/20100524/DC}Bounds"
    shapes = {
        shape.get("bpmnElement"): shape for shape in root.findall(".//di:BPMNShape", NS)
    }
    for gateway in root.findall(".//b:exclusiveGateway", NS):
        shape = shapes[gateway.get("id")]
        label = shape.find("di:BPMNLabel", NS)
        assert (
            label is not None
        ), "La etiqueta de compuerta debe evitar el flujo inferior"
        box, text = shape.find(bounds_tag), label.find(bounds_tag)
        assert float(text.get("x")) >= 0
        assert float(text.get("x")) + float(text.get("width")) <= float(
            box.get("x")
        ) or float(text.get("x")) >= float(box.get("x")) + float(box.get("width"))
