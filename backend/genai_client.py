"""
GenAI Client wrapper for the Anthropic Claude API.

Manages live calls to Anthropic's SDK and implements a robust, deterministic
mock fallback mode for offline testing, local runs, or in case of API errors.
"""

import logging
from anthropic import Anthropic
from backend.config import settings

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Module-level keyword and phrasing constants for the mock response engine.
# Separating data from logic keeps _select_response purely algorithmic.
# ---------------------------------------------------------------------------

# Maps each topic to the keywords that trigger it.
_TOPIC_KEYWORDS: list[tuple[str, list[str]]] = [
    ("restroom", ["restroom", "toilet", "bathroom", "wc"]),
    ("exit", ["exit", "gate", "leave", "out"]),
    ("food", ["food", "eat", "drink", "beer", "hungry", "thirsty", "concession"]),
    ("seat", ["seat", "section", "find", "where is my", "where's my"]),
    (
        "transport",
        ["transport", "metro", "bus", "shuttle", "uber", "rideshare", "park", "car"],
    ),
    (
        "sustain",
        ["sustainability", "recycle", "water", "green", "trash", "environment"],
    ),
]

# Keywords that trigger the accessibility catch-all handler.
_ACCESSIBILITY_KEYWORDS: list[str] = [
    "accessibility",
    "wheelchair",
    "step-free",
    "elevator",
    "ramp",
]

# Organizer-facing topic labels (prepended to each response).
_ORGANIZER_PREFIX: dict[str, str] = {
    "restroom": "Operations Alert: ",
    "exit": "Logistics Alert: ",
    "food": "Concessions Advisory: ",
    "seat": "Seating Advisory: ",
    "transport": "Transit Command: ",
    "sustain": "Sustainability Status: ",
}

# Standard-fan prefix for topic responses (empty means no label needed).
_FAN_PREFIX: dict[str, str] = {
    "restroom": "",
    "exit": "",
    "food": "Hungry? ",
    "seat": "",
    "transport": "Here is the transport info: ",
    "sustain": "Eco Nudge: ",
}

# Friendly closing phrases appended for fan responses.
_FAN_SUFFIX: dict[str, str] = {
    "restroom": " Please let me know if you need help finding anything else.",
    "exit": " Thank you for visiting the stadium today!",
    "food": " Soft drinks and water are also sold there.",
    "seat": " Volunteers in yellow vests are standing by to guide you.",
    "transport": " Expect moderate post-match delays.",
    "sustain": " Help us keep the FIFA World Cup 2026 green!",
}


# Specialized responses keyed by role/persona for offline/mock mode.
_ROLE_RESPONSES: dict[str, dict[str, str]] = {
    "organizer": {
        "restroom": "Concourse A restroom queue exceeds 15 minutes. ACTION: Dispatch 2 guest marshals to redirect crowd to Concourse B restrooms immediately.",
        "exit": "Egress congestion building at Gate B. DECISION SUPPORT: Open secondary emergency exit doors and deploy 3 security officers to West Plaza.",
        "food": "Concourse concession stands show a 20-minute bottleneck. ACTION: Instruct vendor to open additional POS terminals at Stand 12.",
        "seat": "Section 114 reporting heavy seating block traffic. DECISION: Deploy 2 customer assistance volunteers to Section 114 entrance tunnel.",
        "transport": "Metro station queue wait time is 25 minutes. DECISION SUPPORT: Dispatch 2 extra standby shuttle buses to Lot C to relieve crowd pressure.",
        "sustain": "Recycling station bins at West Plaza are 90% full. ACTION: Direct janitorial staff to replace bins at West Plaza immediately.",
    },
    "wheelchair": {
        "restroom": "Step-free, accessible restrooms are located directly on the main concourse near Section 112 (left of the entrance ramp).",
        "exit": "Step-free exit routes and ADA ramps are located at Gate A and Gate C. Elevators are available adjacent to the main ticketing concourse.",
        "food": "Accessible lower-counter concessions are available at Section 105 (Burger Grill) and Section 120 (Taco Stand), both have ramp access.",
        "seat": "Your wheelchair-accessible seating platform is in Section 114, Row W. Follow the ramp on the left.",
        "transport": "ADA-compliant shuttle buses depart from Lot C every 10 minutes. Accessible rideshare pickup is at Gate 2.",
        "sustain": "Accessible recycling bins and water bottle refill stations are located at Section 108 next to the elevator.",
    },
    "visual": {
        "restroom": "Restrooms are located 50 feet ahead on your left, past the concession stand at Section 112. The door has tactile braille signs.",
        "exit": "The nearest exit is Gate A, located straight ahead for 150 yards from the Section 101 corridor.",
        "food": "Concessions are 30 yards to the right. Stands include Section 105 (Burger Grill) and Section 120 (Taco Stand).",
        "seat": "To find Section 114, locate the Section 112 marker on your left, then walk 20 paces forward.",
        "transport": "Metro station entrance is 200 yards directly east of the main gate. Accessible shuttle buses are parked in Lot C to the north-east.",
        "sustain": "A water refill station is 10 paces past Section 108 on the right side wall.",
    },
    "cognitive": {
        "restroom": "Restrooms are at Section 112. They are easy to find and have large signs.",
        "exit": "Exits are at Gate A. Just follow the green exit signs.",
        "food": "Food stands are at Section 105 and Section 120. They sell burgers, hotdogs, and water.",
        "seat": "Go to Section 114. Look for the blue seat signs. Staff in yellow shirts can help you.",
        "transport": "Buses are in Lot C. The Metro is nearby. Both are safe and clean.",
        "sustain": "Recycle bottles in the blue bins. Water stations are near Section 108.",
    },
    "default": {
        "restroom": "Restrooms are located on the main concourse near Sections 112 and 131.",
        "exit": "Exits are located at Gate A (North), Gate B (East), and Gate C (South).",
        "food": "Concession stands are located throughout the concourse. Popular options include the Burger Grill at Section 105 and Taco Stand at Section 120.",
        "seat": "Please look at the directional signage on the concourse walls. Section numbers are clearly marked above the seating entry tunnels.",
        "transport": "The Metro station is a 5-minute walk from Gate A. Shuttle buses are located in Lot C. Rideshare pickup is at Gate 2.",
        "sustain": "Please use the blue recycling bins located at every section entrance. Water refill stations are available near Section 108 and 124.",
    },
}


class GenAIClient:
    """
    Singleton wrapper for the Anthropic API client.
    Supports a transparent fallback to a rule-based mock mode if no API key is provided
    or if API calls fail, protecting the application from 500 errors.
    """

    def __init__(self) -> None:
        self._client: Anthropic | None = None
        self._mode: str = "mock"

        if settings.genai_mode == "live":
            try:
                # Construct client only if live mode is enabled.
                # Wrap in try/except to prevent import-time crashes if SDK initialization fails.
                self._client = Anthropic(api_key=settings.anthropic_api_key)
                self._mode = "live"
                logger.info("Anthropic client initialized successfully in 'live' mode.")
            except Exception as e:
                logger.error(
                    f"Failed to initialize Anthropic client: {e}. "
                    "Falling back to 'mock' mode."
                )
                self._client = None
                self._mode = "mock"
        else:
            logger.info(
                "Initializing GenAIClient in 'mock' mode (no API key configured)."
            )

    @property
    def mode(self) -> str:
        """Returns the current operating mode: 'live' or 'mock'."""
        return self._mode

    def complete(
        self, system_prompt: str, user_message: str, max_tokens: int = 400
    ) -> str:
        """
        Generates a text completion using Claude in live mode,
        or falls back to a deterministic rules engine in mock mode.
        """
        if self._mode == "live" and self._client:
            try:
                response = self._client.messages.create(
                    model=settings.anthropic_model,
                    max_tokens=max_tokens,
                    system=system_prompt,
                    messages=[{"role": "user", "content": user_message}],
                )
                # Parse the response text block
                if response.content and len(response.content) > 0:
                    return response.content[0].text
                raise ValueError("Received empty content from Anthropic API")
            except Exception as e:
                # Log error server-side, but degrade gracefully to avoid 500 error
                logger.error(
                    f"Anthropic API call failed: {e}. Falling back to mock completion."
                )
                return self._mock_complete(system_prompt, user_message)
        else:
            return self._mock_complete(system_prompt, user_message)

    def _build_role_responses(
        self,
        is_organizer: bool,
        is_wheelchair: bool,
        is_visual: bool,
        is_cognitive: bool,
    ) -> dict[str, str]:
        """
        Builds a topic → response-string mapping for the active user role.

        Why a dict lookup: keeps the method under 15 lines and avoids multi-branch boilerplate.
        """
        if is_organizer:
            role_key = "organizer"
        elif is_wheelchair:
            role_key = "wheelchair"
        elif is_visual:
            role_key = "visual"
        elif is_cognitive:
            role_key = "cognitive"
        else:
            role_key = "default"

        return _ROLE_RESPONSES[role_key]

    def _select_response(
        self, msg: str, tips: dict[str, str], is_organizer: bool
    ) -> str | None:
        """
        Matches keywords in the user message to a topic and returns the reply.

        Returns None when no keyword matches, so _mock_complete can fall
        through to the generic greeting without duplicating that logic here.
        Phrasing constants (_TOPIC_KEYWORDS, _FAN_PREFIX, etc.) are defined
        at module level to keep this function purely algorithmic.
        """
        pfx = _ORGANIZER_PREFIX if is_organizer else _FAN_PREFIX
        sfx = {t: "" for t in _ORGANIZER_PREFIX} if is_organizer else _FAN_SUFFIX

        for topic, keywords in _TOPIC_KEYWORDS:
            if any(kw in msg for kw in keywords):
                return f"{pfx[topic]}{tips[topic]}{sfx[topic]}"

        if any(kw in msg for kw in _ACCESSIBILITY_KEYWORDS):
            label = (
                "Accessibility Incident Report: "
                if is_organizer
                else "Accessibility Guidance: "
            )
            return f"{label}{tips['exit']} {tips['restroom']}"

        return None

    def _mock_complete(self, system_prompt: str, user_message: str) -> str:
        """
        A deterministic, keyword-matching rule-based fallback.

        This method serves as a reliable safety net for offline runs, local testing,
        and live demo fail-safes. It customizes replies depending on accessibility
        preferences parsed from the system prompt.
        """
        msg = user_message.lower()
        sys_prompt = system_prompt.lower()

        is_organizer = (
            "organizer" in sys_prompt
            or "operations control" in sys_prompt
            or "organizer" in msg
        )
        is_wheelchair = "wheelchair" in sys_prompt or "wheelchair" in msg
        is_visual = "visual" in sys_prompt or "visual" in msg
        is_cognitive = "cognitive" in sys_prompt or "cognitive" in msg

        tips = self._build_role_responses(
            is_organizer, is_wheelchair, is_visual, is_cognitive
        )
        matched = self._select_response(msg, tips, is_organizer)
        if matched is not None:
            return matched

        # Generic fallback greeting
        if is_organizer:
            return (
                "FIFA 2026 Operations Command Center Assistant. "
                "Current Status: Active. Operational bottlenecks detected at Gate B (82% density). "
                "DECISION SUPPORT: Recommend reallocating 4 guest marshals from Gate A to Gate B to manage entry queues."
            )
        return (
            "Hello! I am your FIFA World Cup 2026 Stadium Assistant. "
            "I can help you locate restrooms, find food stalls, get step-free routing, "
            "view transport schedules, or learn about our stadium recycling program. "
            "What can I help you with today?"
        )


# Global client singleton instance
genai_client = GenAIClient()
