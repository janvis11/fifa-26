# PROMPT 2 — Data Models and Mock Venue Data

Paste everything below this line into Antigravity.

---

Continue following `AGENTS.md`. Building on the scaffold from the
previous step, add:

1. `backend/models.py` — Pydantic models for the whole app:
   - `Persona = Literal["fan", "volunteer", "organizer", "venue_staff"]`
   - `AccessibilityNeed = Literal["none", "wheelchair", "visual",
     "hearing", "cognitive", "elderly"]`
   - `UserContext`: `persona`, `stadium_id`, `gate` (optional),
     `seat_section` (optional), `language` (validated 2–8 char code),
     `accessibility_need`, `minutes_to_kickoff` (optional int, reasonable
     bounds).
   - `ChatRequest` (message, min/max length, plus a `UserContext`),
     `ChatResponse` (reply, persona, mode, suggested_actions list).
   - `TranslateRequest`/`TranslateResponse`.
   - `ZoneStatus` (zone_id, name, density_level enum
     low/medium/high/critical, density_pct 0-100, recommendation),
     `CrowdResponse` (stadium_id, generated_at, zones list,
     overall_recommendation).
   - `TransportOption` (mode, eta_minutes, accessibility_friendly bool,
     notes), `TransportResponse`.
   - `SustainabilityResponse` (tips list, nearest_recycling_zone,
     nearest_water_refill).
   All string fields the user can submit need explicit length limits.

2. `backend/data/stadium_data.py` — a small dict of at least 4 real 2026
   host stadiums (name, city, list of concourse/zone names), plus a
   `get_stadium(stadium_id)` helper that falls back to a sensible default
   if given an unknown id (never raise/crash on an unknown stadium_id from
   a request — that's user input).

Add a top-of-file docstring to each new file explaining its single
responsibility, per AGENTS.md §3. Don't build routes yet.

Confirm the files import cleanly with `python -c "import backend.models,
backend.data.stadium_data"` and show me the final contents.
