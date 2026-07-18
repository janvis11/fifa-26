"""
Main FastAPI application entry point.

Sets up middleware (CORS, Rate Limiting), API routes, and mounts static files
to serve the frontend. Implements global error handling to secure internal state.
"""

import logging
import os
import time
from typing import List, Dict
from fastapi import FastAPI, Request, Response, status, Query
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from starlette.middleware.base import BaseHTTPMiddleware

from backend.config import settings
from backend.models import (
    ChatRequest,
    ChatResponse,
    TranslateRequest,
    TranslateResponse,
    CrowdResponse,
    TransportResponse,
    SustainabilityResponse,
    AccessibilityNeed,
)
from backend.data.stadium_data import get_all_stadiums
from backend.genai_client import genai_client
from backend.services.chat_service import get_chat_response
from backend.services.crowd_service import get_crowd_status
from backend.services.translate_service import translate
from backend.services.transport_service import get_transport_options
from backend.services.sustainability_service import get_sustainability_info

# Initialize logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# FastAPI app definition
app = FastAPI(
    title="FIFA World Cup 2026 Stadium Concierge",
    description=(
        "GenAI-powered Fan Journey Concierge assisting stadium attendees with "
        "crowd levels, navigation, transport, sustainability tips, and multilingual assistance."
    ),
    version="1.0.0",
)

# CORS middleware setup (Restricted allow-list, never wildcard)
if settings.allowed_origins_list:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.allowed_origins_list,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    logger.info(f"CORS allowed origins configured: {settings.allowed_origins_list}")
else:
    logger.info("No CORS origins configured. Running on same-origin only.")


# In-memory Rate Limiting Middleware for single-process demo runs
class RateLimiterMiddleware(BaseHTTPMiddleware):
    """
    Fixed-window rate limiting middleware.
    Monitors /api/chat and /api/translate requests by client IP.
    Note: For production multi-process clusters, this must be refactored to use Redis.
    """

    def __init__(self, app: FastAPI, limit_per_minute: int):
        super().__init__(app)
        self.limit = limit_per_minute
        # Maps IP -> list of timestamps
        self.requests: Dict[str, List[float]] = {}

    async def dispatch(self, request: Request, call_next) -> Response:
        path = request.url.path
        if path in ("/api/chat", "/api/translate"):
            client_ip = request.client.host if request.client else "unknown"
            now = time.time()

            # Keep timestamps within the last 60 seconds
            if client_ip in self.requests:
                self.requests[client_ip] = [
                    t for t in self.requests[client_ip] if now - t < 60
                ]
            else:
                self.requests[client_ip] = []

            if len(self.requests[client_ip]) >= self.limit:
                logger.warning(
                    f"Rate limit exceeded for IP: {client_ip} on path: {path}"
                )
                return JSONResponse(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    content={
                        "detail": "Too many requests. Please wait a minute before trying again."
                    },
                )

            self.requests[client_ip].append(now)

        return await call_next(request)


app.add_middleware(
    RateLimiterMiddleware, limit_per_minute=settings.rate_limit_per_minute
)


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """
    Middleware to strip sensitive response headers and enforce security parameters.
    Why: Prevents fingerprinting by removing framework/server signatures (e.g., Server header).
    """

    async def dispatch(self, request: Request, call_next) -> Response:
        response = await call_next(request)
        if "server" in response.headers:
            del response.headers["server"]
        if "x-powered-by" in response.headers:
            del response.headers["x-powered-by"]
        return response


app.add_middleware(SecurityHeadersMiddleware)


# Global Exception Handler (prevents leaking stack traces or credentials in response payloads)
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    logger.exception(f"Unhandled error during request to {request.url.path}: {exc}")
    return JSONResponse(
        status_code=500,
        content={
            "detail": "An internal server error occurred. Please try again later."
        },
    )


# --- API ROUTES ---


@app.get("/api/health")
async def get_health() -> dict:
    """Returns application status and the active GenAI mode (live or mock)."""
    return {"status": "ok", "genai_mode": genai_client.mode}


@app.get("/api/stadiums")
async def get_stadiums() -> List[dict]:
    """Retrieves list of active World Cup stadiums for UI selector."""
    return get_all_stadiums()


@app.get("/api/crowd/{stadium_id}")
async def get_crowd(stadium_id: str) -> CrowdResponse:
    """Gets simulated real-time crowd densities for all concourses/zones."""
    return get_crowd_status(stadium_id)


@app.post("/api/chat")
async def post_chat(request: ChatRequest) -> ChatResponse:
    """
    Processes chat requests using the built persona prompts and context attributes.
    Delegates processing and suggested action generation to the chat service.
    """
    return get_chat_response(request)


@app.post("/api/translate")
async def post_translate(request: TranslateRequest) -> TranslateResponse:
    """Translates message text into the target language code."""
    return translate(request.text, request.target_lang)


@app.get("/api/transport/{stadium_id}")
async def get_transport(
    stadium_id: str,
    accessibility_need: AccessibilityNeed = "none",
    minutes_to_kickoff: int | None = Query(None),
) -> TransportResponse:
    """Returns local transport schedules with a personalized transit recommendation."""
    return get_transport_options(stadium_id, accessibility_need, minutes_to_kickoff)


@app.get("/api/sustainability/{stadium_id}")
async def get_sustainability(stadium_id: str) -> SustainabilityResponse:
    """Returns recycling spots and carbon reduction hints."""
    return get_sustainability_info(stadium_id)


# --- STATIC FILES MOUNT ---
# Static assets are mounted last so that custom API routes take precedence
frontend_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "frontend")
if os.path.exists(frontend_dir):
    app.mount("/", StaticFiles(directory=frontend_dir, html=True), name="static")
else:
    logger.warning(
        f"Frontend directory '{frontend_dir}' was not found. "
        "Static file serving will be unavailable."
    )
