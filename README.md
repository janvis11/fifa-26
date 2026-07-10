# Fan Journey Concierge- GenAI Stadium Assistant (FIFA World Cup 2026)

## Chosen Vertical

**Primary Vertical: Fan Experience** (with a secondary Organizer/Ops dashboard view). 
The fan's match-day journey was chosen because it represents the highest-value touchpoint for stadium satisfaction, safety, and inclusion at a massive international tournament. Helping a fan navigate transit, restrooms, crowd density, and languages directly addresses match-day friction points, while the ops dashboard consumes the same crowd simulation engine to help coordinators optimize crowd flow.

## What it does

The Fan Journey Concierge is a GenAI-powered web application assisting World Cup attendees and organizers. Key capabilities include:
- **Navigation & Chat:** Interactive assistant answering questions on seating, restrooms, exits, and concessions.
- **Crowd Awareness:** Simulates real-time concourse densities and alerts fans of bottleneck advisories.
- **Accessibility:** First-class routing considerations for wheelchair, visual, cognitive, hearing, and elderly needs.
- **Transport:** Simulates transit options (Metro, Shuttles, Walking, Rideshare) and gives Claude-driven travel recommendations.
- **Sustainability:** Provides waste sorting instructions and free water refill locations.
- **Multilingual:** Translates queries and replies into the user's preferred language.
- **Ops Dashboard:** Secondary view giving stadium coordinators operational support and safety recommendations.

## Architecture

This project is built using **Python + FastAPI** for the backend, and **Vanilla HTML, CSS, and Javascript** (no heavy framework build step) for the frontend.

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

## How the GenAI integration works

The GenAI core resides in `backend/genai_client.py`:
1. **Client Wrapper:** Uses a singleton `GenAIClient` wrapping the Anthropic Python SDK, constructed once at startup.
2. **System-Prompt-Per-Persona Pattern:** Prompts in `backend/personas.py` combine `BASE_RULES` with specific constraints for each persona (Fan, Volunteer, Ops, Venue Staff), appending structured user context parameters.
3. **Offline Mock Fallback:** If `ANTHROPIC_API_KEY` is not present, or if a network/rate limit error occurs during a live call, the system degrades gracefully to `_mock_complete`. This rule-based fallback utilizes keyword-matching and accessibility contexts to provide realistic, helpful answers without throwing 500 errors.

## Running it locally

```bash
# Clone the repository
git clone <repo-url>
cd worldcup-genai-assistant

# Create a virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows, use: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Copy environment variables (optional: add ANTHROPIC_API_KEY to run in live mode)
cp .env.example .env

# Run the FastAPI server
uvicorn backend.main:app --reload
```
Then open <http://localhost:8000> in your browser. Access the interactive API docs at <http://localhost:8000/docs>.

## Running tests

```bash
pytest backend/tests/ -v
```

## Assumptions made

- Stadium layouts, gates, restrooms, and concession zones are simulated mocks for demo consistency.
- Real-time IoT sensor and turnstile counts are simulated deterministically based on stadium ID and minute buckets (guaranteeing consistency across page refreshes within the same minute).
- The offline phrasebook covers English, Spanish, French, German, and Portuguese for standard stadium queries in mock mode.

## Security notes

- **API Keys:** API keys are read from environment variables and kept server-side; they are never logged or sent to the client.
- **CORS Restricted:** Restricted allow-list configuration loaded via configuration, prohibiting wildcards.
- **Rate Limiting:** IP-based token-rate limiter onexpensive chat and translate endpoints to mitigate denial-of-service abuse.
- **Input Validation:** Strict Pydantic models validate constraints (e.g., maximum string lengths, value bounds) on all inputs, rejecting malicious data with a 422.

## Accessibility notes

- **Accessibility Need Context:** The `accessibility_need` field modifies prompt reasoning (e.g., step-free paths for wheelchairs, precise instructions without visual cues for visual, and short jargon-free sentences for cognitive).
- **High Contrast Toggle:** High Contrast stylesheet selector is available in the header, persisting user settings via `localStorage`.
- **Semantic Structure:** Follows clean HTML5 guidelines, including landmarks (`<header>`, `<nav>`, `<main>`), proper label structures, and `aria-live="polite"` regions for screen-reader chat updates.
- **Color-Plus-Text Signalling:** Crowd levels use color combined with text labels and status emojis (🟢, 🟡, 🟠, 🔴) so color is never the single signal.

## Known limitations / what we'd do next

- **In-memory Rate Limiting:** The IP rate limiter is in-memory and will reset on process restarts; for production, this should be backed by a shared Redis store.
- **Mock Phrasebook size:** The offline translation phrasebook handles common inquiries. For rare phrases in mock mode, it uses an honest `[lang] text` fallback format.
