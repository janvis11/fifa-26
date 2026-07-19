# PROMPT 3 — GenAI Client (Live + Offline Mock Mode)

Paste everything below this line into Antigravity.

---

Continue following `AGENTS.md`, especially §4 (security) and §5
(efficiency). Build `backend/genai_client.py`:

- A `GenAIClient` class wrapping the Anthropic Python SDK.
- Constructed once at module level as a singleton (`genai_client =
  GenAIClient()`), reused across requests — don't create a new SDK client
  per call.
- In `__init__`, only attempt to construct the real Anthropic client if
  `settings.genai_mode == "live"`. Wrap that construction in a try/except
  so any init failure degrades to mock mode rather than crashing the app
  at import time.
- Public method: `complete(system_prompt: str, user_message: str,
  max_tokens: int = 400) -> str`.
  - In live mode, call `messages.create` with the model from settings,
    the given `system` and a single `user` message. Catch all exceptions
    from the network call and fall back to the mock method rather than
    propagating — per AGENTS.md §4, a GenAI failure must never 500 the
    request.
  - In mock mode (or after a live-call failure), call a private
    `_mock_complete` method instead.
- `_mock_complete` is a deterministic, keyword-matching rule-based
  fallback (NOT a language model) that gives genuinely useful canned
  answers for the most common fan questions: restrooms, exits, food,
  finding a seat, transport, sustainability/recycling — plus a sensible
  generic fallback for anything else. Document clearly in the docstring
  that this exists purely as a reliability safety net for offline demos /
  API outages, not as the primary product experience.
- Expose a `mode` property returning `"live"` or `"mock"` so callers (and
  API responses) can be transparent about which path answered.
- Never log, print, or return the API key anywhere in this file.

Then build `backend/personas.py`:

- `BASE_RULES`: a shared system-prompt fragment enforcing conciseness,
  no invented specifics, accessibility-awareness, and responding in the
  user's requested language.
- `PERSONA_PROMPTS`: a dict keyed by persona (`fan`, `volunteer`,
  `organizer`, `venue_staff`) each combining `BASE_RULES` with
  persona-specific priorities (see `00_MASTER_PLAN.md` §3 for what each
  persona cares about).
- `build_system_prompt(context: UserContext) -> str`: picks the right
  persona prompt and appends a rendered block of the user's context
  (stadium, gate, seat, language, accessibility need, minutes to kickoff)
  so the model reasons over it. User-provided free text must never be
  interpolated into the system prompt — only structured context fields
  go here; the chat message itself stays in the `user` slot when calling
  `genai_client.complete`.

Show me both files and confirm `python -c "from backend.genai_client
import genai_client; print(genai_client.mode)"` prints `mock` when no
`.env` is present.
