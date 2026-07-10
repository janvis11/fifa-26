"""
Unit tests for application security guidelines.
"""

from fastapi.testclient import TestClient
from backend.main import app
from backend.config import settings

client = TestClient(app)

def test_api_key_not_exposed() -> None:
    """Ensures that the internal Anthropic API key is never leaked in response payloads."""
    # Health endpoint check
    resp_health = client.get("/api/health")
    assert resp_health.status_code == 200
    assert "api_key" not in resp_health.text
    assert "key" not in resp_health.text
    
    # Chat endpoint check
    payload = {
        "message": "hi",
        "context": {
            "persona": "fan",
            "stadium_id": "sofi",
            "language": "en",
            "accessibility_need": "none"
        }
    }
    resp_chat = client.post("/api/chat", json=payload)
    assert resp_chat.status_code == 200
    assert "api_key" not in resp_chat.text

def test_cors_restrictions() -> None:
    """Ensures Origin checking works against the allowed origins config."""
    # Query with disallowed Origin
    response = client.get("/api/stadiums", headers={"Origin": "http://malicious-site.com"})
    # CORS middleware omits the Access-Control-Allow-Origin header if the Origin is not allowed
    assert "access-control-allow-origin" not in response.headers
    
    # If allowed origins are configured, verify that an allowed origin returns the correct header
    if settings.allowed_origins_list:
        allowed_origin = settings.allowed_origins_list[0]
        response_allowed = client.get("/api/stadiums", headers={"Origin": allowed_origin})
        assert response_allowed.headers.get("access-control-allow-origin") == allowed_origin

def test_rate_limiting() -> None:
    """Ensures per-IP rate limiting middleware restricts high volume chat requests."""
    # Traverse the ASGI application middleware stack to find the RateLimiterMiddleware instance
    middleware = app.middleware_stack
    rate_limiter = None
    while hasattr(middleware, "app"):
        if middleware.__class__.__name__ == "RateLimiterMiddleware":
            rate_limiter = middleware
            break
        middleware = middleware.app

    # If found, temporarily patch the limit to 3 for rapid testing
    original_limit = 60
    if rate_limiter:
        original_limit = rate_limiter.limit
        rate_limiter.limit = 3
        rate_limiter.requests = {}

    payload = {
        "message": "test rate limiting",
        "context": {
            "persona": "fan",
            "stadium_id": "metlife",
            "language": "en",
            "accessibility_need": "none"
        }
    }
    
    # Hit chat endpoint 4 times in quick succession (limit is 3)
    status_codes = []
    for _ in range(4):
        resp = client.post("/api/chat", json=payload)
        status_codes.append(resp.status_code)
        
    # Revert rate limit patch
    if rate_limiter:
        rate_limiter.limit = original_limit
        rate_limiter.requests = {}
        
    assert 200 in status_codes
    assert 429 in status_codes
