# README Template

Give Antigravity this structure in `PROMPT_8`. Each `<...>` should be
replaced with real, specific content from the actual codebase.

```markdown
# Fan Journey Concierge — GenAI Stadium Assistant (FIFA World Cup 2026)

## Chosen Vertical

<State: Fan Experience, with a secondary Organizer/Ops dashboard view.
Explain in 2-3 sentences why the fan's match-day journey was chosen as
the persona to design around.>

## What it does

<Short paragraph + bullet list of the 6 capabilities: navigation, crowd
awareness, accessibility, transport, sustainability, multilingual help,
plus the ops dashboard.>

## Architecture

<Short description + the file tree from 00_MASTER_PLAN.md §5, updated to
match what was actually built.>

## How the GenAI integration works

<Explain: Anthropic Claude API, system-prompt-per-persona pattern in
personas.py, and — importantly — the offline mock-mode fallback and why
it exists (reliability at a live event / demo without requiring judges
to have an API key).>

## Running it locally

```bash
git clone <repo-url>
cd worldcup-genai-assistant
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env   # optional: add your ANTHROPIC_API_KEY to enable live mode
uvicorn backend.main:app --reload
```
Then open <http://localhost:8000>.

## Running tests

```bash
pytest backend/tests -v
```

## Assumptions made

<Bullet list, pulled honestly from what was actually assumed during the
build — e.g. exact challenge vertical list, mock venue/crowd data instead
of real IoT, which languages the phrase-book mock covers, etc.>

## Security notes

<Bullet list: API key handling, CORS allow-list, rate limiting, input
validation, no secrets logged.>

## Accessibility notes

<Bullet list: accessibility_need context field, high-contrast/large-text
toggle, semantic HTML/ARIA, color-plus-text signaling.>

## Known limitations / what we'd do next

<Honest, short list — e.g. in-memory rate limiter doesn't scale past one
process, mock crowd data isn't real sensor data, translation phrase-book
is small in offline mode.>
```
