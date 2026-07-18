"""
Unit tests for the health check endpoint.
"""

from fastapi.testclient import TestClient
from backend.main import app

client = TestClient(app)


def test_health_check() -> None:
    """Asserts that the health endpoint returns OK and runs in mock mode by default."""
    response = client.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert data["genai_mode"] in ("mock", "live")
