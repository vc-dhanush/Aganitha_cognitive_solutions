from fastapi.testclient import TestClient

from backend.main import app

client = TestClient(app)


def test_health():
    response = client.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert data["service"] == "microscopyai"


def test_config():
    response = client.get("/api/config")
    assert response.status_code == 200
    data = response.json()
    assert "cellpose" in data["models"]


def test_analyze_invalid_file():
    response = client.post(
        "/api/analyze",
        files={"file": ("bad.txt", b"not an image", "text/plain")},
        data={"params": "{}"},
    )
    assert response.status_code == 400
