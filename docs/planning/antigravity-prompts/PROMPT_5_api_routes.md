# PROMPT 5 — FastAPI App, Routes, and Security Middleware

Paste everything below this line into Antigravity.

---

Continue following `AGENTS.md`, especially §4 (security). Build
`backend/main.py`:

1. Create the FastAPI app with a descriptive title/description (this
   powers the auto-generated `/docs` page).
2. Configure CORS using `settings.allowed_origins` from `config.py` —
   never a wildcard.
3. Add a simple in-memory per-IP rate limiter as middleware (token bucket
   or fixed-window counter keyed by client IP, limit from
   `settings.rate_limit_per_minute`), applied at least to the chat and
   translate endpoints since those are the costly ones. Return HTTP 429
   with a clear message when exceeded. Document in a comment that this is
   an in-memory limiter suitable for a single-process demo, and that a
   production deployment behind multiple workers would need a shared
   store (e.g. Redis) instead — be upfront about this limitation rather
   than pretending it scales.
4. Routes:
   - `GET /api/health` → `{"status": "ok", "genai_mode": ...}`.
   - `GET /api/stadiums` → list of available stadium ids/names for the
     frontend's dropdown.
   - `GET /api/crowd/{stadium_id}` → calls `crowd_service`.
   - `POST /api/chat` → validates `ChatRequest`, builds the system prompt
     via `personas.build_system_prompt`, calls `genai_client.complete`
     with the user's raw message as the `user` slot, returns
     `ChatResponse` including a couple of `suggested_actions` (simple
     logic-derived quick replies like "Show me transport options" based
     on keywords in the reply — no extra GenAI call needed for this).
   - `POST /api/translate` → calls `translate_service`.
   - `GET /api/transport/{stadium_id}` → calls `transport_service`,
     accepting `accessibility_need` and `minutes_to_kickoff` as optional
     query params to personalize.
   - `GET /api/sustainability/{stadium_id}` → calls
     `sustainability_service`.
5. Mount `frontend/` as static files at `/` so the whole app is servable
   from a single `uvicorn backend.main:app` process (this matters for
   judges running it quickly — one command, not two servers).
6. Add a global exception handler that returns a generic safe error
   message and logs the real exception server-side — never leak stack
   traces or internal details to the client.

Show me the full file. Then run the app locally and confirm `GET
/api/health` and `GET /docs` both work, and that `POST /api/chat` with a
trivial message returns a sensible mock-mode reply.
