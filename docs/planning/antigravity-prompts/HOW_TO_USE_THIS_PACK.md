# How to Use This Pack With Antigravity

## What's in this pack

| File | Purpose |
|---|---|
| `00_MASTER_PLAN.md` | Read yourself, first. The strategy and architecture. |
| `AGENTS.md` | Copy into the **root of your repo**. Antigravity reads this automatically as standing rules for every task in the workspace. |
| `PROMPT_1` … `PROMPT_8` | Paste into Antigravity's chat **one at a time, in order**. |
| `README_TEMPLATE.md` | Give this to Antigravity in `PROMPT_7` as the required README structure. |
| `EVAL_CHECKLIST.md` | Run through this yourself before submitting. |

## Step-by-step

1. Create a new **public** GitHub repo, e.g. `worldcup-genai-assistant`, with
   no template files (empty repo).
2. Clone it into Antigravity's workspace.
3. Copy `AGENTS.md` into the repo root immediately, before your first
   prompt. Commit it by itself: `docs: add agent rules`.
4. Open `PROMPT_1_scaffold.md`, copy its entire contents, paste into
   Antigravity chat, let it run and finish, review the diff, commit.
5. Repeat for `PROMPT_2` through `PROMPT_8`, in order. Don't skip ahead —
   later prompts assume earlier files exist.
6. After each prompt, actually run the app locally (or have Antigravity
   run it) and glance at the result before moving on. Catching a problem
   at step 3 is cheap; catching it at step 8 means re-doing work.
7. After `PROMPT_8`, go through `EVAL_CHECKLIST.md` top to bottom.
8. Push to the single branch (`main`), confirm the repo is public, and
   submit the link.

## Tips for prompting Antigravity well

- If Antigravity's output drifts from `AGENTS.md` (e.g. it hard-codes a
  key, or puts logic in a route handler), just reply: *"This violates
  AGENTS.md section X — please fix."* Pointing at the specific section
  number gets a much more precise correction than a vague "clean this up."
- If a step fails or produces something you don't like, don't pile a new
  prompt on top — ask Antigravity to fix the specific issue first, then
  re-run the tests, then proceed.
- Keep your own commit hygiene even if Antigravity forgets: after each
  accepted step, confirm `git status` is clean and `git log` shows a
  sensible message.
- If you swap the Anthropic API for a different provider, only
  `genai_client.py` should need to change — if Antigravity wants to touch
  other files for a provider swap, that's a sign the abstraction leaked
  and worth flagging.
