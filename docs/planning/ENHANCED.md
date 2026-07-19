# ENHANCED.md — Closing the Gap from 93.99 to Full Marks

Your current AI evaluation score: **93.99/100**

| Category | Score | Gap |
|---|---|---|
| Efficiency | 100 | none |
| Security | 99 | 1 |
| Accessibility | 98 | 2 |
| Testing | 96 | 4 |
| Problem Statement Alignment | 93 | 7 |
| Code Quality | 88 | 12 |

Code Quality and Problem Statement Alignment are pulling the average down
the most — attack those first. Paste the sections below into Antigravity
**one category at a time**, in the order given, and re-run the evaluator
after each one before moving to the next. Don't paste the whole file at
once; you want to see which specific fix moved the needle.

---

## 1. Code Quality (88 → target 97+)

Paste this into Antigravity:

> Read `AGENTS.md` §3 again and audit this entire repository against it,
> file by file. Specifically:
> 1. Find and report every route handler in `backend/main.py` that
>    contains logic beyond parse-input → call-service → return-response.
>    Move any stray logic into the matching `services/` module.
> 2. Find any function longer than ~25 lines or doing more than one
>    clear thing, and split it into smaller, named functions.
> 3. Confirm every function across `backend/` has a type hint on every
>    parameter and return value, and a docstring explaining *why*, not
>    just *what* — flag and fix any that only restate the function name.
> 4. Search for repeated literals (string keys, magic numbers, repeated
>    URL paths, repeated error messages) across more than one file and
>    centralize them in `config.py` or a constants module.
> 5. Check `frontend/app.js` for inline event handlers in HTML, global
>    variables, or unnamed anonymous functions attached as callbacks —
>    replace with named functions and `addEventListener`.
> 6. Run whatever linter/formatter fits the stack (e.g. `ruff` or
>    `flake8` + `black` for Python) and fix every warning, not just
>    errors. Add the linter to `requirements.txt` (dev dependency) if
>    it isn't already there.
> 7. Give me a before/after diff summary of everything you changed.

## 2. Problem Statement Alignment (93 → target 100)

Paste this into Antigravity:

> Re-read the original challenge brief in `00_MASTER_PLAN.md` and list,
> explicitly, which of these eight capabilities the current codebase
> demonstrably implements versus merely mentions in the README: navigation,
> crowd management, accessibility, transportation, sustainability,
> multilingual assistance, operational intelligence, real-time decision
> support. For any capability that's currently thin (implemented as a
> static string rather than something GenAI or the simulated data engine
> actually reasons over), strengthen it:
> - if "operational intelligence" only appears as a single
>   `overall_recommendation` string, extend the ops dashboard to show a
>   short trend (e.g. "zone 3 has been rising for the last 10 minutes")
>   rather than a single snapshot.
> - if "real-time decision support" isn't clearly distinguishable from
>   "crowd management" in the current build, add one concrete decision
>   the organizer persona can act on directly from the assistant's
>   reply (e.g. a suggested staff reallocation), not just a status read.
> - confirm the README's "what it does" section maps each of the eight
>   capabilities to a specific file/endpoint, so a judge can verify the
>   claim in under a minute without hunting through the codebase.
> Report which capabilities you strengthened and how.

## 3. Testing (96 → target 100)

Paste this into Antigravity:

> Review `backend/tests/` for coverage gaps against `AGENTS.md` §6.
> Specifically add, if missing:
> 1. A test asserting that a GenAI live-call exception (mock the
>    Anthropic client to raise) is caught and falls back to mock mode
>    rather than propagating a 500.
> 2. A test for every `Literal` enum field (persona, accessibility_need,
>    density_level) confirming an invalid value returns 422, not just
>    testing the valid ones.
> 3. A test confirming the rate limiter resets after its time window
>    (not just that it triggers 429).
> 4. Run `pytest --cov=backend` and report the coverage percentage; if
>    any service module is under ~85% coverage, add tests to close the
>    gap. Show me the coverage report.

## 4. Accessibility (98 → target 100)

Paste this into Antigravity:

> Do a fresh keyboard-only pass over `frontend/index.html`: tab through
> every control with no mouse and confirm focus order is logical and
> every focused element has a visible focus outline (check this isn't
> suppressed by any `outline: none` in `styles.css`). Confirm the
> high-contrast toggle's state is announced to screen readers (e.g. via
> `aria-pressed`, already required by AGENTS.md §7 — verify it's actually
> present, not just planned). Confirm every `<img>` or icon-only button
> has an `alt` or `aria-label`. Fix anything missing and show me the diff.

## 5. Security (99 → target 100)

Paste this into Antigravity:

> Do a final security pass: confirm response headers don't leak server
>/framework version info (e.g. disable the default `Server` header if
> FastAPI/uvicorn exposes one), confirm all error responses go through
> the global handler in `AGENTS.md`/`main.py` with no path returning a
> raw exception message, and confirm `.env.example` truly has no real
> values in it, only placeholders. Report findings.

---

After all five sections are done and re-scored, run through
`EVAL_CHECKLIST.md` one final time before resubmitting.
