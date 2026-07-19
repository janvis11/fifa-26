# CODE_QUALITY_ONLY.md — Raise Code Quality Without Touching Anything Else

Current scores: Code Quality 88, Security 99, Testing 99, Accessibility
98, Efficiency 100, Problem Statement Alignment 100. This pass targets
Code Quality only. Every rule below exists to keep the other five exactly
where they are.

Paste the sections in order. Do not paste more than one section at a
time. Run the verification gate after each one before moving to the next.

## Standing rules for this entire pass (paste this first, once)

> for the rest of this session, follow these constraints on every change
> you make:
> 1. only touch files related to code structure, formatting, type hints,
>    docstrings, naming, and file organization. do not modify anything
>    inside `backend/tests/`, `.github/workflows/ci.yml`, or any
>    accessibility-related markup/aria attributes in `frontend/`.
> 2. after every single change, run `pytest backend/tests -v` and paste
>    the output. if any test fails, revert that specific change
>    immediately and tell me, rather than trying to fix it forward.
> 3. if a change would alter any runtime behavior — a return value, a
>    condition, a default, an api response shape, cors config, or rate
>    limit config — stop and show me that specific diff before applying
>    it. formatting and structure changes should never alter behavior;
>    if one seems to require it, flag it instead of proceeding.
> 4. work on one file or one issue at a time, not sweeping multi-file
>    rewrites in a single step. small, verifiable diffs only.
> 5. never remove or weaken input validation, error handling, or the
>    security/rate-limiting logic while "cleaning up" a file — if a
>    validation check looks redundant, leave it and ask me rather than
>    deleting it.

## Step 1 — clean up the repo root (near-zero risk)

> the repo root currently mixes planning artifacts (`00_MASTER_PLAN.md`,
> `AGENTS.md`, `EVAL_CHECKLIST.md`, `HOW_TO_USE_THIS_PACK.md`, and the
> `antigravity-prompts/` folder) in with the actual application folders
> (`api/`, `backend/`, `frontend/`). move all of those planning files
> into a new folder `docs/planning/`, unchanged in content, fixing any
> relative links between them if needed. leave `README.md` and `LICENSE`
> at the root. do not touch `api/`, `backend/`, or `frontend/` in this
> step. show me the new root file listing.

**Gate:** run `pytest backend/tests -v` — should be unaffected. Confirm
`uvicorn backend.main:app --reload` still starts cleanly.

## Step 2 — read-only audit (zero risk)

> list every source file under `api/`, `backend/`, and `frontend/`. for
> each, report: missing type hints, weak/one-line docstrings that just
> restate the function name, functions over 25 lines or doing more than
> one job, magic numbers/strings duplicated in more than one file, dead
> code (commented-out blocks, unused imports/variables), inconsistent
> naming or formatting between files, and whether `api/` reimplements
> logic that already exists in `backend/main.py` instead of importing it.
> output as a table: file | issue | line numbers. do not change anything
> yet — this is the map for the next steps.

**Gate:** none needed, nothing was changed. Read the table before continuing.

## Step 3 — formatting only, auto-fixable (very low risk)

> add `ruff` and `black` as dev dependencies. run `black .` and
> `ruff check --fix .` across the whole repo including `api/`. these
> tools only change formatting (whitespace, quote style, import
> ordering) — do not manually change any logic. show me the full diff.

**Gate:** run `pytest backend/tests -v`. Personally skim the diff — every
line should be purely cosmetic. If any line changes an actual value,
condition, or return statement, ask why before accepting it.

## Step 4 — docstrings and type hints, additive only (low risk)

> using the table from step 2, add missing type hints and replace weak
> docstrings with ones that explain a non-obvious *why*, across every
> file including `api/`. this must be purely additive — no function's
> logic, return value, or behavior should change, only its hints and
> documentation.

**Gate:** run `pytest backend/tests -v`.

## Step 5 — centralize duplicated constants (low-medium risk)

> using the table from step 2, move magic numbers/strings duplicated
> across more than one file into `backend/config.py`, updating call sites
> to reference the centralized value. one duplicated value at a time.

**Gate:** run `pytest backend/tests -v` after every single value you
centralize, not after the whole batch. Also manually confirm
`/api/health`, `/api/chat`, and `/api/crowd/<valid-stadium-id>` still
return the same response shape as before this step.

## Step 6 — split long/multi-responsibility functions (medium risk)

> using the table from step 2, split any function over 25 lines or doing
> more than one job into smaller named functions, preserving exact
> existing behavior. one function at a time.

**Gate:** run `pytest backend/tests -v` after every single split.

## Step 7 — resolve `api/` duplication, only if step 2 flagged it (highest risk, do last)

> show me, with actual file contents, whether `api/` imports and mounts
> the fastapi app from `backend/main.py`, or reimplements request
> handling independently.

Read the answer yourself.

- If `api/` already just imports/mounts `backend/main.py`: stop here,
  nothing to fix, do not touch it further.
- If it reimplements logic independently, only then paste:

> refactor `api/` into a thin adapter that imports and mounts the
> existing fastapi app from `backend/main.py`, removing the duplicated
> implementation, without changing any behavior — cors, rate limiting,
> and the global exception handler must apply identically after the
> change. show me the before/after.

**Gate:** run `pytest backend/tests -v` in full. Then manually hit
`/api/health`, `/api/chat`, and `/api/crowd/<valid-stadium-id>` against
the live vercel deployment after pushing, and confirm identical response
shapes to local testing. If anything differs, `git revert` immediately —
do not attempt to debug forward this close to your evaluation run.

## Before you run the evaluation

- [ ] `pytest backend/tests -v` passes fully, right now, on the current
      `main` branch state.
- [ ] you personally reviewed `git diff` (or the commit history) and
      confirm nothing under `backend/tests/`, `.github/workflows/`, or
      accessibility markup in `frontend/` changed.
- [ ] the live vercel deployment still loads and responds correctly.
- [ ] everything is committed and pushed to `main`.
- [ ] if you stopped before step 7, that's fine — a smaller, verified
      set of wins that didn't risk the 98-100 categories is better than
      a bigger change you're not fully sure about.