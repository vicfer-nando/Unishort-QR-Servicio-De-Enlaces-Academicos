"""Valida UTF-8, enlaces locales, YAML y referencias BPMN sin afirmar render."""

import re
import xml.etree.ElementTree as ET
from pathlib import Path
from urllib.parse import unquote

import yaml

ROOT = Path(__file__).resolve().parents[1]


def main():
    """Revisa fuentes públicas; exige preparar recursos Quarto previamente."""
    files = [ROOT / "README.md", ROOT / ".specify/memory/constitution.md"]
    for directory in ("docs", "specs", "quarto"):
        files.extend(
            path
            for path in (ROOT / directory).rglob("*")
            if path.is_file()
            and path.suffix in {".md", ".qmd", ".yml", ".bpmn", ".dsl", ".puml"}
            and not any(part in {"sources", "_site", ".quarto"} for part in path.parts)
        )
    broken = []
    for path in files:
        text = path.read_text(encoding="utf-8", errors="strict")
        assert "\ufffd" not in text, path
        for line in text.splitlines():
            if "http" not in line:
                assert not re.search(r"[A-Za-z]\?[A-Za-z]", line), (path, line)
        if path.suffix in {".md", ".qmd"}:
            for link in re.findall(r"\]\(([^)]+)\)", text):
                if link.startswith(("http:", "https:", "#", "mailto:")):
                    continue
                target = unquote(link.split("#")[0])
                if target and not (path.parent / target).exists():
                    broken.append(f"{path.relative_to(ROOT)} -> {link}")
    if broken:
        raise SystemExit("Enlaces locales inexistentes:\n" + "\n".join(broken))
    xml = ET.parse(ROOT / "docs/procesos/creacion-enlace.bpmn")
    elements = list(xml.iter())
    identifiers = [
        element.attrib["id"] for element in elements if "id" in element.attrib
    ]
    assert len(identifiers) == len(set(identifiers))
    ids = set(identifiers)
    for element in elements:
        for attribute in ("sourceRef", "targetRef", "processRef", "bpmnElement"):
            if attribute in element.attrib:
                assert element.attrib[attribute] in ids
        if element.tag.rsplit("}", 1)[-1] in {"flowNodeRef", "incoming", "outgoing"}:
            assert element.text.strip() in ids
    for path in (
        ROOT / "quarto/_quarto.yml",
        ROOT / "docker-compose.yml",
        ROOT / ".github/workflows/quality.yml",
    ):
        assert isinstance(yaml.safe_load(path.read_text(encoding="utf-8")), dict)
    print(
        f"UTF-8 y enlaces: {len(files)} fuentes OK; YAML OK; BPMN XML y referencias OK."
    )
    print(
        "No equivale a render Quarto/PlantUML/Structurizr ni validación BPMN por XSD."
    )


if __name__ == "__main__":
    main()
