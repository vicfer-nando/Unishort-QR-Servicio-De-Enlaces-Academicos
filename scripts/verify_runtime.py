"""Verifica UniShort por TCP con SQLite temporal; nunca usa unishort.db.

Ejecutar desde la raíz: python scripts/verify_runtime.py
Con --serve conserva el entorno temporal hasta Ctrl+C para probar el navegador.
"""

import argparse
import hashlib
import json
import os
import secrets
import sqlite3
import subprocess
import sys
import tempfile
import time
from contextlib import closing
from pathlib import Path

import cv2
import httpx
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
BASE_URL = "http://localhost:8000"


def wait_ready(client, url):
    """Espera disponibilidad local con un plazo acotado."""
    for _ in range(100):
        try:
            response = client.get(url)
            if response.status_code == 200:
                return
        except httpx.TransportError:
            pass
        time.sleep(0.1)
    raise RuntimeError(f"El servicio no arrancó: {url}")


def stop(process):
    """Detiene solo el proceso creado por esta comprobación."""
    process.terminate()
    process.wait(timeout=10)


def verify(client, key, database):
    """Recorre el flujo real sin seguir destinos de Internet."""
    admin = {"X-Admin-API-Key": key}
    origin = {"Origin": "http://localhost:5500"}
    assert client.get("http://localhost:5500").status_code == 200
    assert client.get("http://localhost:5500/admin.html").status_code == 200
    module = client.get("http://localhost:5500/admin.mjs")
    assert module.status_code == 200
    assert "javascript" in module.headers["content-type"]
    assert client.get("/docs").status_code == 200
    assert "/api/v1/links" in client.get("/openapi.json").json()["paths"]
    created = client.post(
        "/api/v1/links",
        json={"url": "http://localhost:5500/?demo=runtime"},
        headers=origin,
    )
    assert created.status_code == 201
    assert created.headers["access-control-allow-origin"] == origin["Origin"]
    data = created.json()["data"]
    code = data["short_code"]
    qr = client.get(data["qr_url"])
    image = cv2.imdecode(
        np.frombuffer(qr.content, dtype=np.uint8), cv2.IMREAD_GRAYSCALE
    )
    decoded, _, _ = cv2.QRCodeDetector().detectAndDecode(image)
    assert decoded == data["short_url"]
    stats = f"/api/v1/links/{code}/stats"
    assert client.get(stats, headers=admin).json()["data"]["click_count"] == 0
    redirect = client.get(data["short_url"])
    assert redirect.status_code == 307
    assert redirect.headers["location"] == "http://localhost:5500/?demo=runtime"
    assert client.get(stats, headers=admin).json()["data"]["click_count"] == 1
    assert client.get(stats).status_code == 401
    assert (
        client.get(stats, headers={"X-Admin-API-Key": "incorrecta"}).status_code == 403
    )
    assert client.get("/api/v1/links", headers=admin).status_code == 200
    summary = client.get("/api/v1/admin/stats", headers=admin)
    assert summary.status_code == 200
    assert summary.headers["cache-control"] == "no-store"
    assert summary.json()["data"]["total_links"] == 1
    assert summary.json()["data"]["total_visits"] == 1
    assert client.get("/api/v1/admin/stats").status_code == 401
    filtered = client.get(
        "/api/v1/links",
        params={"q": code, "status": "active", "limit": 1},
        headers=admin,
    )
    assert filtered.json()["data"]["total"] == 1
    assert filtered.json()["data"]["items"][0]["short_code"] == code
    assert client.get("/s/nonexistent").status_code == 404
    for url in (
        "not-a-url",
        "ftp://example.edu",
        "https://[bad",
        "https://user:pass@example.edu",
    ):
        assert client.post("/api/v1/links", json={"url": url}).status_code in (400, 422)
    assert client.delete(f"/api/v1/links/{code}", headers=admin).status_code == 200
    assert client.get(data["short_url"]).status_code == 410
    assert client.get(data["qr_url"]).status_code == 410
    assert (
        client.patch(
            f"/api/v1/links/{code}", json={"is_active": True}, headers=admin
        ).status_code
        == 200
    )
    # Solo esta base temporal: simula el paso del reloj sin esperas frágiles.
    with closing(sqlite3.connect(database)) as connection:
        with connection:
            connection.execute(
                "UPDATE short_urls SET expires_at = '2020-01-01 00:00:00' WHERE short_code = ?",
                (code,),
            )
    assert client.get(data["short_url"]).status_code == 410
    assert client.get(data["qr_url"]).status_code == 410
    assert (
        client.patch(
            f"/api/v1/links/{code}", json={"expires_at": None}, headers=admin
        ).status_code
        == 200
    )
    samples = {"create": [], "redirect": []}
    for _ in range(100):
        start = time.perf_counter()
        response = client.post(
            "/api/v1/links", json={"url": "https://example.edu/benchmark"}
        )
        samples["create"].append((time.perf_counter() - start) * 1000)
        assert response.status_code == 201
        start = time.perf_counter()
        assert client.get(response.json()["data"]["short_url"]).status_code == 307
        samples["redirect"].append((time.perf_counter() - start) * 1000)
    return code, {
        operation: round(sorted(values)[94], 2) for operation, values in samples.items()
    }


def main():
    """Arranca dos procesos propios, verifica y los cierra al terminar."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--serve", action="store_true")
    args = parser.parse_args()
    original = ROOT / "unishort.db"
    original_hash = (
        hashlib.sha256(original.read_bytes()).hexdigest() if original.exists() else None
    )
    processes = []
    with tempfile.TemporaryDirectory(prefix="unishort-runtime-") as temp:
        directory = Path(temp)
        database = directory / "demo.db"
        key = secrets.token_urlsafe(32)
        env = dict(
            os.environ,
            UNISHORT_DATABASE_URL=f"sqlite:///{database.as_posix()}",
            UNISHORT_BASE_URL=BASE_URL,
            UNISHORT_ADMIN_API_KEY=key,
            UNISHORT_RATE_LIMIT_ENABLED="false",
            UNISHORT_LOG_LEVEL="WARNING",
        )
        flags = subprocess.CREATE_NO_WINDOW if sys.platform == "win32" else 0

        def start_backend():
            process = subprocess.Popen(
                [
                    sys.executable,
                    "-m",
                    "uvicorn",
                    "backend.app.main:app",
                    "--host",
                    "127.0.0.1",
                    "--port",
                    "8000",
                    "--no-access-log",
                ],
                cwd=ROOT,
                env=env,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                creationflags=flags,
            )
            processes.append(process)
            return process

        try:
            # No adoptar un servicio ajeno que ya ocupe los puertos de demostración.
            import socket

            for port in (8000, 5500):
                with socket.socket() as probe:
                    probe.bind(("127.0.0.1", port))
            subprocess.run(
                [sys.executable, "-m", "alembic", "upgrade", "head"],
                cwd=ROOT,
                env=env,
                check=True,
                capture_output=True,
                creationflags=flags,
            )
            backend = start_backend()
            frontend = subprocess.Popen(
                [
                    sys.executable,
                    "scripts/serve_frontend.py",
                ],
                cwd=ROOT,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                creationflags=flags,
            )
            processes.append(frontend)
            with httpx.Client(
                base_url=BASE_URL, trust_env=False, follow_redirects=False, timeout=10
            ) as client:
                wait_ready(client, "/health")
                wait_ready(client, "http://localhost:5500")
                code, latency = verify(client, key, database)
                stop(backend)
                start_backend()
                wait_ready(client, "/health")
                assert client.get(f"/s/{code}").status_code == 307
                report = {
                    "checks": "HTTP + SQLite + QR decodificado + admin + CORS + reinicio OK",
                    "requests_per_operation": 100,
                    "concurrency": 1,
                    "p95_ms_loopback": latency,
                    "rate_limit_during_benchmark": False,
                    "real_database_sha256": original_hash,
                }
                print(json.dumps(report, ensure_ascii=False, indent=2), flush=True)
                if args.serve:
                    print(
                        "Frontend temporal en http://localhost:5500; Ctrl+C para cerrar.",
                        flush=True,
                    )
                    while True:
                        time.sleep(1)
        except KeyboardInterrupt:
            pass
        finally:
            for process in reversed(processes):
                if process.poll() is None:
                    stop(process)
            if original_hash:
                assert (
                    hashlib.sha256(original.read_bytes()).hexdigest() == original_hash
                )


if __name__ == "__main__":
    main()
