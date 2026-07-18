"""
Unit tests for the translate service and endpoint.
"""

from fastapi.testclient import TestClient
from backend.main import app

client = TestClient(app)


def test_translate_happy_path() -> None:
    """Verifies translation happy path using standard phrasebook terms."""
    payload = {"text": "Where is the nearest restroom?", "target_lang": "es"}
    response = client.post("/api/translate", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "translated_text" in data
    assert len(data["translated_text"]) > 0


def test_translate_validation_errors() -> None:
    """Verifies validation on translate inputs (empty text or missing parameters)."""
    # Empty text
    payload_empty = {"text": "", "target_lang": "fr"}
    response = client.post("/api/translate", json=payload_empty)
    assert response.status_code == 422

    # Invalid target lang (too long)
    payload_long_lang = {"text": "Hello", "target_lang": "verylonglangcode"}
    response = client.post("/api/translate", json=payload_long_lang)
    assert response.status_code == 422
