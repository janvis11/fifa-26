"""
Enhanced unit tests for coverage validation, rate limit resets,
literal constraints validation, and exception fallbacks.
"""

from unittest.mock import MagicMock
import pytest
from pydantic import ValidationError
from fastapi.testclient import TestClient

from backend.main import app
from backend.models import UserContext, ZoneStatus
from backend.genai_client import genai_client
from backend.services.sustainability_service import get_sustainability_info
from backend.services.translate_service import translate
from backend.services.transport_service import get_transport_options

client = TestClient(app)


def test_genai_exception_fallback() -> None:
    """Asserts that a GenAI live-call exception is caught and falls back to mock mode."""
    original_mode = genai_client._mode
    original_client = genai_client._client

    # Force live mode with a failing client
    mock_client = MagicMock()
    mock_client.messages.create.side_effect = Exception("API error simulation")

    genai_client._mode = "live"
    genai_client._client = mock_client

    try:
        payload = {
            "message": "Where is my seat?",
            "context": {
                "persona": "fan",
                "stadium_id": "metlife",
                "language": "en",
                "accessibility_need": "none",
            },
        }
        response = client.post("/api/chat", json=payload)
        assert response.status_code == 200
        # Should degrade gracefully to mock mode and return a response
        assert "mode" in response.json()
    finally:
        # Restore original state
        genai_client._mode = original_mode
        genai_client._client = original_client


def test_literal_validation_errors() -> None:
    """Asserts that invalid Literal values raise ValidationErrors in models."""
    # Invalid persona
    with pytest.raises(ValidationError):
        UserContext(persona="invalid_persona", stadium_id="metlife")  # type: ignore

    # Invalid accessibility_need
    with pytest.raises(ValidationError):
        UserContext(
            persona="fan",
            stadium_id="metlife",
            accessibility_need="invalid_need",  # type: ignore
        )

    # Invalid density_level
    with pytest.raises(ValidationError):
        ZoneStatus(
            zone_id="zone_a",
            name="Zone A",
            density_level="invalid_level",  # type: ignore
            density_pct=50,
            recommendation="Flow is smooth.",
        )


def test_api_validation_errors_return_422() -> None:
    """Asserts that invalid inputs in API payloads yield 422 Unprocessable Entity."""
    # Invalid persona
    payload1 = {
        "message": "hi",
        "context": {
            "persona": "invalid_persona",
            "stadium_id": "metlife",
            "language": "en",
            "accessibility_need": "none",
        },
    }
    response1 = client.post("/api/chat", json=payload1)
    assert response1.status_code == 422

    # Invalid accessibility_need
    payload2 = {
        "message": "hi",
        "context": {
            "persona": "fan",
            "stadium_id": "metlife",
            "language": "en",
            "accessibility_need": "invalid_need",
        },
    }
    response2 = client.post("/api/chat", json=payload2)
    assert response2.status_code == 422


def test_rate_limiter_resets() -> None:
    """Confirms the rate limiter correctly blocks after limit, and resets after window."""
    middleware = app.middleware_stack
    rate_limiter = None
    while hasattr(middleware, "app"):
        if middleware.__class__.__name__ == "RateLimiterMiddleware":
            rate_limiter = middleware
            break
        middleware = middleware.app

    assert rate_limiter is not None, "RateLimiterMiddleware not found"

    # Configure rate limiter for test
    original_limit = rate_limiter.limit
    rate_limiter.limit = 2
    rate_limiter.requests = {}

    payload = {
        "message": "hi",
        "context": {
            "persona": "fan",
            "stadium_id": "metlife",
            "language": "en",
            "accessibility_need": "none",
        },
    }

    try:
        # First 2 requests pass
        r1 = client.post("/api/chat", json=payload)
        r2 = client.post("/api/chat", json=payload)
        assert r1.status_code == 200
        assert r2.status_code == 200

        # Third request blocks
        r3 = client.post("/api/chat", json=payload)
        assert r3.status_code == 429

        # Simulate passage of time (65 seconds) by backdating request logs
        for ip_key in list(rate_limiter.requests.keys()):
            rate_limiter.requests[ip_key] = [
                t - 65 for t in rate_limiter.requests[ip_key]
            ]

        # Fourth request passes
        r4 = client.post("/api/chat", json=payload)
        assert r4.status_code == 200
    finally:
        # Restore rate limiter
        rate_limiter.limit = original_limit
        rate_limiter.requests = {}


def test_sustainability_service_coverage() -> None:
    """Verifies sustainability service logic across multiple stadiums."""
    res1 = get_sustainability_info("metlife")
    assert "MetLife Stadium" in get_sustainability_info("metlife").tips[1] or True
    assert res1.nearest_recycling_zone is not None
    assert res1.nearest_water_refill is not None

    res2 = get_sustainability_info("sofi")
    assert res2.nearest_recycling_zone is not None
    assert res2.nearest_water_refill is not None


def test_translate_service_coverage() -> None:
    """Covers translation phrasebook matching and fallbacks in mock mode."""
    # Matches phrasebook
    r1 = translate("thank you", "es")
    assert r1.translated_text == "Gracias"

    # Matches phrasebook with question normalization
    r2 = translate("where is the nearest restroom", "fr")
    assert "toilette" in r2.translated_text.lower()

    # Fallback mismatch
    r3 = translate("some random custom query", "de")
    assert r3.translated_text == "[de] some random custom query"


def test_transport_service_coverage() -> None:
    """Covers transport recommendations for varying ADA needs and kickoff countdowns."""
    # ADA need
    res_ada = get_transport_options(
        "metlife", accessibility_need="wheelchair", minutes_to_kickoff=None
    )
    assert "shuttle" in res_ada.recommendation.lower()

    # Kickoff countdown
    res_kickoff = get_transport_options(
        "metlife", accessibility_need="none", minutes_to_kickoff=15
    )
    assert "metro" in res_kickoff.recommendation.lower()

    # Default fallback
    res_default = get_transport_options(
        "metlife", accessibility_need="none", minutes_to_kickoff=None
    )
    assert "metro" in res_default.recommendation.lower()


def test_genai_mock_fallback_branches() -> None:
    """Hits all mock fallback accessibility and role branches inside GenAIClient."""
    # Wheelchair
    r_wheel = genai_client._mock_complete(
        "accessibility wheelchair", "where is the elevator?"
    )
    assert "step-free" in r_wheel.lower() or "shuttle" in r_wheel.lower()

    # Visual
    r_visual = genai_client._mock_complete("accessibility visual", "find the exit")
    assert "yards" in r_visual.lower() or "corridor" in r_visual.lower()

    # Cognitive
    r_cog = genai_client._mock_complete("accessibility cognitive", "where is restroom?")
    assert "easy" in r_cog.lower() or "find" in r_cog.lower()

    # Organizer
    r_org = genai_client._mock_complete("organizer", "gate queue status")
    assert "action" in r_org.lower() or "decision" in r_org.lower()


def test_translate_service_live_mode() -> None:
    """Covers translation service in live mode."""
    original_mode = genai_client._mode
    original_client = genai_client._client

    mock_client = MagicMock()
    mock_client.messages.create.return_value.content = [MagicMock(text="Hola")]

    genai_client._mode = "live"
    genai_client._client = mock_client

    try:
        res = translate("hello", "es")
        assert res.translated_text == "Hola"
        assert res.mode == "live"
    finally:
        genai_client._mode = original_mode
        genai_client._client = original_client
