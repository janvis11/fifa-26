# PROMPT 8 — README and Final Polish

Paste everything below this line into Antigravity.

---

Continue following `AGENTS.md`, especially §8 (honesty about
assumptions). Write `README.md` at the repo root using the structure in
`README_TEMPLATE.md` (paste that file's contents in below this prompt
when you send it). Fill in every section with specifics from the actual
code you've written — do not leave template placeholders in the final
README.

Also do a final polish pass:

1. Re-read every file against `AGENTS.md` sections 3–7 and fix any
   drift you find (logic that crept into a route handler, a missing
   docstring, a missing input validation bound, a hard-coded value that
   should be config, a color-only UI signal, etc.). List what you fixed.
2. Confirm `.env` is not tracked by git (`git status` should not show it
   even if you created a local one for testing) and that `.env.example`
   has no real secrets in it.
3. Confirm the whole app runs end-to-end with a single command from a
   clean clone (document the exact command in the README) and with zero
   API keys configured (mock mode) — this must work, since judges won't
   have your Anthropic key.
4. Run the full pytest suite one final time and paste the output.
5. Double check the repo has no work split across branches — everything
   on `main`.

When done, give me a final summary of: the file tree, test results, and
any assumptions you made along the way that I should double check.
