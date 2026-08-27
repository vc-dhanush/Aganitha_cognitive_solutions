from fastapi.testclient import TestClient

from aganitha_cognitive_solutions import greet
from aganitha_cognitive_solutions.app import app


def test_greet() -> None:
    assert greet("Aganitha") == "Hello, Aganitha!"


def test_health_endpoint() -> None:
    client = TestClient(app)
    response = client.get("/health")
    assert response.status_code == 200
    payload = response.json()
    assert payload["status"] == "ok"
    assert payload["version"] == "0.1.0"
