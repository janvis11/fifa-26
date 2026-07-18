"""
Unit tests for the chat assistant endpoint.
"""

from fastapi.testclient import TestClient
from backend.main import app

client = TestClient(app)


def test_chat_personas_happy_path() -> None:
    """Verifies that all four personas can successfully query the chat assistant."""
    personas = ["fan", "volunteer", "organizer", "venue_staff"]
    for persona in personas:
        payload = {
            "message": "Where is the nearest exit?",
            "context": {
                "persona": persona,
                "stadium_id": "sofi",
                "gate": "Gate B",
                "seat_section": "100",
                "language": "en",
                "accessibility_need": "none",
                "minutes_to_kickoff": 45,
            },
        }
        response = client.post("/api/chat", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert "reply" in data
        assert len(data["reply"]) > 0
        assert data["persona"] == persona
        assert "mode" in data
        assert len(data["suggested_actions"]) > 0


def test_chat_validation_errors() -> None:
    """Verifies that empty messages or messages exceeding length bounds trigger 422 errors."""
    # Empty message validation
    payload_empty = {
        "message": "",
        "context": {
            "persona": "fan",
            "stadium_id": "metlife",
            "language": "en",
            "accessibility_need": "none",
        },
    }
    response = client.post("/api/chat", json=payload_empty)
    assert response.status_code == 422

    # Message too long validation (limit is 1000)
    payload_long = {
        "message": "x" * 1001,
        "context": {
            "persona": "fan",
            "stadium_id": "metlife",
            "language": "en",
            "accessibility_need": "none",
        },
    }
    response = client.post("/api/chat", json=payload_long)
    assert response.status_code == 422


def test_chat_invalid_stadium_fallback() -> None:
    """Asserts that passing an unknown stadium_id falls back to default and does not crash."""
    payload = {
        "message": "Where is the food section?",
        "context": {
            "persona": "fan",
            "stadium_id": "invalid-stadium-id-123",
            "language": "en",
            "accessibility_need": "none",
        },
    }
    response = client.post("/api/chat", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "reply" in data
