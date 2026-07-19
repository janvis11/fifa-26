# PROMPT 1 — Project Scaffold

Paste everything below this line into Antigravity.

---

Read `AGENTS.md` in this repo root and follow it for everything below and
for every future task in this workspace.

Set up the initial project scaffold for "Fan Journey Concierge", a GenAI
stadium assistant for FIFA World Cup 2026, backend in Python/FastAPI,
frontend in plain HTML/CSS/JS. Do not implement any business logic yet —
this step is scaffolding only.

Create:

1. `requirements.txt` with: `fastapi`, `uvicorn[standard]`, `pydantic`,
   `pydantic-settings`, `python-dotenv`, `httpx`, `anthropic`, `pytest`.
   Pin reasonable current stable versions.
2. `.env.example` documenting: `ANTHROPIC_API_KEY` (optional — explain
   that leaving it blank runs the app in offline mock mode),
   `ANTHROPIC_MODEL` (default `claude-sonnet-4-6`), `ALLOWED_ORIGINS`
   (comma-separated CORS allow-list), `RATE_LIMIT_PER_MINUTE` (default 60).
3. `.gitignore` covering Python, `.env`, editor cruft, and `node_modules/`.
4. `LICENSE` — MIT.
5. Empty directory structure:
   ```
   backend/
     __init__.py
     data/__init__.py
     services/__init__.py
     tests/__init__.py
   frontend/
   .github/workflows/
   ```
6. `backend/config.py`: a `Settings` object that loads all of the above
   env vars (via `python-dotenv` + `os.getenv`), with a `genai_mode`
   property returning `"live"` if `ANTHROPIC_API_KEY` is set else
   `"mock"`. No defaults that silently enable anything unsafe.

Do not write `main.py` or any service/model files yet — that's the next
prompt. When done, show me the full file tree and confirm
`pip install -r requirements.txt` succeeds in a clean virtualenv.
