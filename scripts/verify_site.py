"""Comprueba archivos y anclas de enlaces HTML del sitio generado, sin red."""

from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlsplit

ROOT = Path(__file__).resolve().parents[1]


class Page(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.links: list[str] = []
        self.anchors: set[str] = set()

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        values = dict(attrs)
        identifier = values.get("id")
        if identifier:
            self.anchors.add(identifier)
        if tag == "a" and values.get("name"):
            self.anchors.add(str(values["name"]))
        for attribute in ("href", "src"):
            if values.get(attribute):
                self.links.append(str(values[attribute]))


def verify_site(site: Path) -> list[str]:
    site = site.resolve()
    pages: dict[Path, Page] = {}
    failures = []
    for path in site.rglob("*.html"):
        page = Page()
        page.feed(path.read_text("utf-8"))
        pages[path.resolve()] = page
    if not pages or not (site / "index.html").exists():
        return ["No existe un portal HTML construido con index.html"]
    for path, page in pages.items():
        for link in page.links:
            parsed = urlsplit(link)
            if parsed.scheme or parsed.netloc or not link or link == "#":
                continue
            target = (
                (path.parent / unquote(parsed.path)).resolve() if parsed.path else path
            )
            if not target.is_relative_to(site):
                failures.append(
                    f"{path.relative_to(site)}: enlace fuera del sitio: {link}"
                )
                continue
            if target.is_dir():
                target /= "index.html"
            if not target.exists():
                failures.append(
                    f"{path.relative_to(site)}: archivo inexistente: {link}"
                )
            elif (
                parsed.fragment
                and target in pages
                and unquote(parsed.fragment) not in pages[target].anchors
            ):
                failures.append(f"{path.relative_to(site)}: ancla inexistente: {link}")
    return sorted(set(failures))


def main() -> None:
    site = ROOT / "quarto/_site"
    failures = verify_site(site)
    if failures:
        raise SystemExit("Enlaces HTML inválidos:\n" + "\n".join(failures))
    print(
        f"HTML: {len(list(site.rglob('*.html')))} páginas, enlaces/recursos/anclas locales OK."
    )
    print(
        "No equivale a verificar destinos externos ni accesibilidad o revisión visual humana."
    )


if __name__ == "__main__":
    main()
