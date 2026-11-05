"""Sirve el frontend local sin registrar IP ni parámetros de URL."""

import argparse
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path


class QuietHandler(SimpleHTTPRequestHandler):
    """Entrega archivos estáticos sin registros de acceso o error con PII."""

    def log_message(self, format: str, *args: object) -> None:
        """Omite el log predeterminado que incluye IP y URL de la petición."""


def main() -> None:
    """Escucha solo en loopback por defecto; Ctrl+C detiene el servidor."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=5500)
    args = parser.parse_args()
    directory = Path(__file__).resolve().parents[1] / "frontend"
    handler = partial(QuietHandler, directory=str(directory))
    with ThreadingHTTPServer((args.host, args.port), handler) as server:
        print(
            f"Frontend en http://{args.host}:{args.port}; Ctrl+C para cerrar.",
            flush=True,
        )
        try:
            server.serve_forever()
        except KeyboardInterrupt:
            pass


if __name__ == "__main__":
    main()
