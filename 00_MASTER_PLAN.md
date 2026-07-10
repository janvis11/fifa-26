# Master Plan — FIFA World Cup 2026 GenAI Stadium Assistant

This is the strategy document. Read this first, yourself, before feeding
anything to Antigravity. Everything else in this pack (`AGENTS.md`, the
`PROMPT_*.md` files) implements this plan.

## 1. Chosen Vertical

**Primary persona: Fan Experience** — a GenAI concierge that helps a fan
navigate the stadium, understand crowd conditions, get accessible routing,
find transport, get sustainability nudges, and get help in their own
language.

**Secondary persona (bonus, not the core focus): Organizer / Ops Control
Room** — a lightweight dashboard view fed by the same crowd-simulation
engine, showing operational intelligence and real-time decision support.
This lets one codebase visibly touch almost every bullet in the challenge
brief (navigation, crowd management, accessibility, transportation,
sustainability, multilingual assistance, operational intelligence,
real-time decision support) without diluting the "choose one vertical and
design around that persona" requirement — the fan is the one persona the
whole product is designed around; the ops view is presented explicitly as
a secondary lens onto the same data.

> **Assumption:** the original challenge document listed specific named
> verticals (e.g. "Fan Experience", "Volunteer Coordination", "Stadium
> Operations", "Accessibility & Inclusion") that weren't included in what
> you pasted to me. I'm assuming "Fan Experience" is one of them, since
> it's the most common framing for this kind of hackathon. If your actual
> vertical list is different, tell Antigravity to swap the persona in
> `AGENTS.md` §2 — everything else in this plan still applies unchanged.

## 2. Why this wins on the AI evaluation criteria

| Criterion | How this plan scores well |
|---|---|
| **Problem Statement Alignment** | One assistant, one clear persona, but touches navigation, crowd mgmt, accessibility, transport, sustainability, multilingual, ops intelligence, and real-time decision support — the full bullet list from the brief, all justified by the fan's actual journey through a match day. |
| **Code Quality** | Strict module boundaries (config / models / genai client / services / routes), typed Pydantic schemas everywhere, no logic in route handlers, docstrings explaining *why* not just *what*. |
| **Security** | API keys server-side only via env vars, `.env` never committed, input validation on every endpoint, CORS allow-list, basic rate limiting, no secrets ever logged or returned to the client. |
| **Efficiency** | Lightweight stack (FastAPI + vanilla JS, no heavy frontend build), deterministic mock mode avoids unnecessary API calls during dev/testing, caching-friendly crowd simulation. |
| **Testing** | pytest suite covering every endpoint, both live-mode-mocked and offline-mock-mode paths, input validation edge cases, CI workflow running tests on every push. |
| **Accessibility** | Accessibility isn't a checkbox feature — it's a first-class field in the user context object that changes what the assistant says (step-free routing, larger text, screen-reader-friendly markup, high-contrast toggle, plain-language mode). |

## 3. Core product idea

A single web app, **"Fan Journey Concierge"**, with:

1. A chat assistant (GenAI-powered) that answers contextual questions —
   "where's the nearest accessible restroom", "how do I get to Gate C
   without stairs", "what's the fastest way home after the match".
2. A **live crowd/zone status panel** (simulated real-time data) that
   feeds both the fan's chat context and a separate **Ops view**.
3. A **transport widget** with GenAI-personalized recommendations.
4. A **sustainability tip panel** (nearest recycling/water refill + tips).
5. A **language switcher** — the assistant replies in the fan's language.
6. An **accessibility mode** — toggling it changes both the UI (larger
   text, higher contrast) and the assistant's reasoning (step-free routes,
   plainer language, more explicit instructions).

Everything runs on mock/simulated venue data (turnstile counts, zone
sensors) — the brief is about demonstrating the GenAI decision-making
pattern, not about having a real IoT integration, so mock data generation
must be clearly labeled as such in the README (see `AGENTS.md` §7 on
honesty about assumptions).

## 4. Recommended tech stack

- **Backend:** Python + FastAPI (async, typed, auto-generates OpenAPI docs
  at `/docs` — free "look how professional this is" points for judges).
- **GenAI provider:** Anthropic Claude API (`anthropic` Python SDK), model
  `claude-sonnet-4-6`, called server-side only.
- **Critical resilience feature:** if no API key is configured, the app
  falls back to a deterministic, rule-based **mock mode** so it *always*
  demos successfully — even with no internet, no key, or a live-demo API
  outage. This is a deliberate reliability decision, call it out in the
  README and the demo pitch.
- **Frontend:** plain HTML/CSS/JS (no framework build step) so a judge can
  clone the repo and open `index.html` / run one `uvicorn` command with
  zero friction. Do not over-engineer this with React/Next.js — simplicity
  here is a feature, not a limitation.
- **Tests:** pytest + FastAPI `TestClient`.
- **CI:** one GitHub Actions workflow running lint + tests on push.

## 5. Repo layout Antigravity should produce

```
worldcup-genai-assistant/
├── README.md
├── LICENSE
├── .gitignore
├── .env.example
├── requirements.txt
├── AGENTS.md                  <- persistent rules, keep in repo root
├── backend/
│   ├── main.py
│   ├── config.py
│   ├── models.py
│   ├── genai_client.py
│   ├── personas.py
│   ├── data/stadium_data.py
│   ├── services/
│   │   ├── crowd_service.py
│   │   ├── translate_service.py
│   │   ├── transport_service.py
│   │   └── sustainability_service.py
│   └── tests/
│       ├── test_chat.py
│       ├── test_crowd.py
│       ├── test_translate.py
│       └── test_security.py
├── frontend/
│   ├── index.html
│   ├── styles.css
│   └── app.js
└── .github/workflows/ci.yml
```

## 6. Order of operations

Feed the `PROMPT_*.md` files to Antigravity **in numeric order**, one at a
time, letting it finish and commit before starting the next. Don't paste
them all at once — small, reviewable steps produce better code and are
easier for you to sanity-check between stages. See `HOW_TO_USE_THIS_PACK.md`.

## 7. Definition of done

Before submitting, walk through `EVAL_CHECKLIST.md` line by line. If
anything is unchecked, send the matching item back to Antigravity as a
follow-up prompt rather than submitting with gaps.
