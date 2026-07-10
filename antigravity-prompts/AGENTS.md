# AGENTS.md — Persistent Rules for This Project

Antigravity: treat this file as standing instructions for every task in
this repository, not just the current prompt. Re-read it before each
`PROMPT_*.md` step. If a specific prompt ever conflicts with this file,
stop and ask rather than silently choosing one.

## 1. What we're building

"Fan Journey Concierge" — a GenAI-powered assistant for fans at a FIFA
World Cup 2026 host stadium, with a secondary operations-dashboard view.
Full context lives in `00_MASTER_PLAN.md`. Do not change the chosen
persona or tech stack without being explicitly asked.

## 2. Persona and scope boundaries

- Primary user: **the fan**. Every feature must trace back to something a
  fan on match day would actually need: navigation, crowd awareness,
  accessibility, transport, sustainability, multilingual help.
- Secondary user: **the organizer** (ops dashboard), fed by the same
  simulated crowd data. Keep this view small — it exists to show breadth,
  not to become a second product.
- Do not add unrelated features (no ticketing, no payments, no user
  accounts/login system) — they add surface area and risk without scoring
  points against the brief.

## 3. Code quality rules

- Python: type hints on every function signature, Pydantic models for all
  request/response shapes, docstrings that explain *why* a non-obvious
  decision was made (e.g. why mock mode exists), not just what the code
  does.
- No business logic inside route handlers — routes call into `services/`,
  handlers stay thin (parse input → call service → return response).
- No magic numbers/strings duplicated across files — centralize in
  `config.py` or the relevant data/service module.
- Frontend JS: no inline `onclick=` handlers, no global variable soup —
  use small named functions and `addEventListener`.
- Keep functions short. If a function is doing three distinct things,
  split it.
- Every module needs a top-of-file docstring stating its single
  responsibility.

## 4. Security rules (non-negotiable)

- The Anthropic API key is read from an environment variable
  (`ANTHROPIC_API_KEY`) via `.env` locally. It must **never**:
  - be hard-coded anywhere in source,
  - be sent to the frontend in any response payload,
  - be logged, printed, or included in error messages,
  - be committed — confirm `.env` is in `.gitignore` before every commit.
- Validate all incoming request fields (length limits, enum constraints)
  with Pydantic — reject bad input with a 422, don't let it reach a
  service function unchecked.
- CORS must be restricted to an explicit allow-list from config, never
  `allow_origins=["*"]` in anything resembling a "production" code path.
- Add a simple in-memory per-IP rate limiter on the chat/translate
  endpoints so a single client can't hammer the (costly) GenAI calls.
- Never build prompts by directly concatenating raw user input into a
  system prompt in a way that lets the user override assistant
  instructions — user text goes in the `user` message slot only, system
  instructions stay in the `system` slot.
- If the live GenAI call fails or times out for any reason (bad key, rate
  limit, network error), catch the exception and fall back to mock mode.
  Never let a GenAI failure 500 the whole request.

## 5. Efficiency rules

- Don't call the GenAI API when a deterministic answer is possible (e.g.
  crowd-level classification from a number is pure logic, not a model
  call — only the *narrative recommendation* should hit the model, and
  only when there's something non-trivial to say).
- Keep the frontend dependency-free (no npm build step) unless explicitly
  asked to add one.
- Cache/reuse the GenAI client instance — don't construct a new SDK client
  per request.

## 6. Testing rules

- Every new endpoint needs a pytest test in `backend/tests/` before the
  task is considered done.
- Tests must cover: the happy path, at least one validation-error path
  (bad input → 422), and the offline-mock-mode path (since CI will not
  have a real API key).
- Do not write tests that require a live network call or a real API key —
  CI has neither. Mock-mode must be the default test environment.
- Run the full test suite after every prompt and report the result before
  moving to the next prompt.

## 7. Accessibility rules

- `accessibility_need` is a first-class field on the user context, not a
  cosmetic afterthought. When it's set to `wheelchair`, assistant answers
  about routing must prefer step-free language. When set to `visual`,
  keep language extra literal/explicit (avoid "over there", use concrete
  directions). When set to `cognitive`, keep sentences short and avoid
  jargon.
- Frontend HTML must use semantic elements (`<button>`, `<label>`,
  `<nav>`, proper heading order) and ARIA attributes where semantics
  alone aren't enough. Every interactive control needs a visible label or
  `aria-label`.
- Provide a high-contrast/large-text toggle in the UI that persists for
  the session.
- Color must never be the only signal for crowd-density levels — pair
  color with a text label and/or icon.

## 8. Honesty about assumptions

- All venue/crowd/transport data is simulated. Say so plainly in the
  README under "Assumptions" — do not imply a real IoT/turnstile
  integration exists.
- If you (Antigravity) have to guess at something not specified in a
  prompt, make the smallest reasonable assumption, write it down in the
  README's Assumptions section, and keep moving — don't block on asking
  the human unless it's a genuine fork in direction (e.g. "should mock
  mode exist at all" would be worth asking; "what should the mock
  restroom message say" is not).

## 9. Commit discipline

- Commit after each `PROMPT_*.md` step completes and tests pass, with a
  clear, conventional commit message (e.g. `feat: add crowd density
  service with GenAI narrative recommendations`).
- Keep everything on a single branch, per the challenge submission rules.
- Never commit a `.env` file, `__pycache__/`, or `node_modules/`.
