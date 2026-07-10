# PROMPT 7 — Tests and CI

Paste everything below this line into Antigravity.

---

Continue following `AGENTS.md`, especially §6 (testing). Build the test
suite in `backend/tests/` using `pytest` and FastAPI's `TestClient`. Make
sure `ANTHROPIC_API_KEY` is unset in the test environment so everything
runs in mock mode — do not require network access or real credentials for
any test.

At minimum:

- `test_health.py`: `GET /api/health` returns 200 and `genai_mode ==
  "mock"` when no key is configured.
- `test_chat.py`:
  - Happy path: valid `ChatRequest` for each of the four personas returns
    200 with a non-empty `reply` and `mode == "mock"`.
  - Validation: empty `message` and a `message` over the max length both
    return 422.
  - Confirm a nonsense/unknown `stadium_id` does not crash the endpoint
    (falls back to default per AGENTS.md/PROMPT_2 requirements).
- `test_crowd.py`: `GET /api/crowd/{stadium_id}` returns 200, all zones
  have a valid `density_level`, and `overall_recommendation` is non-empty.
  Assert the endpoint is stable (calling it twice within the same test
  run doesn't wildly disagree, since it's minute-bucketed).
- `test_translate.py`: valid request returns 200 with non-empty
  `translated_text`; empty `text` or missing `target_lang` returns 422.
- `test_security.py`:
  - Confirm the API key is never present in any response body, across
    `/api/health`, `/api/chat`, and error responses.
  - Confirm CORS headers only reflect an allowed origin, not an arbitrary
    one, when `Origin` header is set to something not in the allow-list.
  - Confirm hitting `/api/chat` more than `RATE_LIMIT_PER_MINUTE` times in
    quick succession eventually returns 429 (use a small test-only limit
    via environment override if needed, so the test runs fast).

Then create `.github/workflows/ci.yml`:
- Trigger on push and pull_request to any branch.
- Set up Python, install `requirements.txt`.
- Run `pytest` with `ANTHROPIC_API_KEY` explicitly unset/empty in the CI
  environment so it always exercises mock mode.
- Fail the workflow if any test fails.

Run the full suite locally, show me the output, and confirm all tests
pass before committing.
