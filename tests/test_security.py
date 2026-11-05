from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_shorten_without_api_key_returns_401():
    response = client.post("/shorten", json={"url": "https://unl.edu.ec"})
    assert response.status_code == 401

def test_shorten_with_invalid_api_key_returns_403():
    response = client.post(
        "/shorten", 
        json={"url": "https://unl.edu.ec"},
        headers={"X-API-Key": "clave-incorrecta"}
    )
    assert response.status_code == 403

def test_shorten_with_invalid_url_syntax_returns_422():
    response = client.post(
        "/shorten", 
        json={"url": "no-es-una-url-valida"},
        headers={"X-API-Key": "unishort-secret-key-2026"}
    )
    assert response.status_code == 422

def test_shorten_authorized_success():
    response = client.post(
        "/shorten", 
        json={"url": "https://unl.edu.ec"},
        headers={"X-API-Key": "unishort-secret-key-2026"}
    )
    assert response.status_code == 201
    assert "short_code" in response.json()