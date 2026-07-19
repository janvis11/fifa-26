# Evaluation Checklist — Run This Before Submitting

Go through every line. If something is unchecked, send a targeted
follow-up prompt to Antigravity (quote the exact line) rather than
submitting with a gap.

## Problem Statement Alignment
- [ ] README explicitly names the chosen vertical/persona and explains why.
- [ ] The app demonstrably touches: navigation, crowd management,
      accessibility, transportation, sustainability, multilingual
      assistance, operational intelligence, real-time decision support.
- [ ] Every feature traces back to a real fan/organizer need — nothing
      feels bolted on just to tick a keyword.

## Code Quality
- [ ] No business logic inside FastAPI route handlers.
- [ ] Every function has type hints and a docstring.
- [ ] No duplicated magic numbers/strings — centralized in config/data.
- [ ] Frontend JS has no inline `onclick=` handlers or global soup.
- [ ] Consistent naming and file organization matches `00_MASTER_PLAN.md` §5.

## Security
- [ ] `ANTHROPIC_API_KEY` only ever read from env, never hard-coded.
- [ ] `.env` is gitignored and NOT present in `git log` history.
- [ ] API key never appears in any response body or log line — verified
      by `test_security.py`.
- [ ] CORS allow-list is explicit, not `"*"`.
- [ ] All request models have length/enum/range validation.
- [ ] Rate limiting is present on the chat/translate endpoints.
- [ ] A failed/misbehaving GenAI call cannot crash a request (falls back
      to mock, never a raw 500 with a stack trace).

## Efficiency
- [ ] GenAI is only called when generative reasoning is actually needed
      (crowd level classification, sustainability tips, etc. are pure
      logic/static content, not model calls).
- [ ] GenAI client is a singleton, not re-instantiated per request.
- [ ] Frontend has no build step / unnecessary dependencies.

## Testing
- [ ] Full pytest suite passes locally with no `ANTHROPIC_API_KEY` set.
- [ ] Tests cover happy path, validation errors, and mock-mode behavior
      for every endpoint.
- [ ] CI workflow runs on push and is green.

## Accessibility
- [ ] `accessibility_need` visibly changes assistant behavior (try asking
      the same question with different values and compare replies).
- [ ] High-contrast/large-text toggle works and is keyboard-operable.
- [ ] All interactive elements are reachable and usable via keyboard only
      (tab through the whole page without a mouse).
- [ ] Crowd density is never color-only — text/icon is always present.
- [ ] Chat log uses `aria-live` so replies are announced by screen readers.

## Submission logistics
- [ ] Repo is public.
- [ ] Everything is on a single branch (`main`).
- [ ] README has all required sections filled in with real specifics, no
      leftover template placeholders.
- [ ] A fresh clone + the documented single command actually runs the
      app with zero configuration (mock mode) — test this literally, in
      a clean directory, right before submitting.
