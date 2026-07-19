# PROMPT 4 — Service Layer (Crowd, Translate, Transport, Sustainability)

Paste everything below this line into Antigravity.

---

Continue following `AGENTS.md`. Build four service modules under
`backend/services/`. Route handlers will call these in the next step —
services must contain all the actual logic (per AGENTS.md §3, no logic in
route handlers).

1. **`crowd_service.py`** — simulates real-time crowd density and uses
   GenAI for the operational recommendation:
   - A deterministic pseudo-random density generator (0–100%) seeded by
     stadium id + zone name + current minute-bucket (e.g. hash-based), so
     results are stable within the same minute for demo/testing
     consistency but still change over time.
   - Map density % to a level: `low` (<35), `medium` (35–64), `high`
     (65–84), `critical` (85+). This mapping is pure logic — do NOT call
     GenAI just to classify a number (see AGENTS.md §5 efficiency rule).
   - Only call `genai_client.complete` to produce the
     `overall_recommendation` narrative, and only when at least one zone
     is `high` or `critical` — otherwise return a static "all zones
     normal" string with zero GenAI calls.
   - Return a fully populated `CrowdResponse`.

2. **`translate_service.py`** — multilingual assistance:
   - In live mode, call `genai_client.complete` with a strict
     translate-only system prompt ("return ONLY the translated text, no
     explanation").
   - In mock mode, do NOT just return the generic assistant fallback
     text (that would look broken in a demo). Instead keep a small
     phrase-book dict for a handful of common stadium phrases in 3–4
     languages, and otherwise return `"[{target_lang}] {original text}"`
     as an honest, visibly-a-placeholder fallback.

3. **`transport_service.py`** — mocked transport options (shuttle, metro,
   rideshare, walking) with eta/accessibility flags, plus a GenAI call
   that picks and explains the single best recommendation given the
   user's context (accessibility need, minutes to kickoff).

4. **`sustainability_service.py`** — returns a short list of sustainability
   tips (recycling, water refill stations, public transport nudge) plus
   nearest recycling zone / water refill strings, personalized slightly by
   stadium zone data. This can be mostly static content with light
   templating — no need to call GenAI here, it doesn't need generative
   reasoning (efficiency rule again).

Every function must have a docstring and full type hints. Show me all
four files.
