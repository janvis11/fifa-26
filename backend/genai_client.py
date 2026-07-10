"""
GenAI Client wrapper for the Anthropic Claude API.

Manages live calls to Anthropic's SDK and implements a robust, deterministic
mock fallback mode for offline testing, local runs, or in case of API errors.
"""

import logging
from anthropic import Anthropic
from backend.config import settings

logger = logging.getLogger(__name__)

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
            logger.info("Initializing GenAIClient in 'mock' mode (no API key configured).")

    @property
    def mode(self) -> str:
        """Returns the current operating mode: 'live' or 'mock'."""
        return self._mode

    def complete(
        self,
        system_prompt: str,
        user_message: str,
        max_tokens: int = 400
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
                    messages=[
                        {"role": "user", "content": user_message}
                    ]
                )
                # Parse the response text block
                if response.content and len(response.content) > 0:
                    return response.content[0].text
                raise ValueError("Received empty content from Anthropic API")
            except Exception as e:
                # Log error server-side, but degrade gracefully to avoid 500 error
                logger.error(f"Anthropic API call failed: {e}. Falling back to mock completion.")
                return self._mock_complete(system_prompt, user_message)
        else:
            return self._mock_complete(system_prompt, user_message)

    def _mock_complete(self, system_prompt: str, user_message: str) -> str:
        """
        A deterministic, keyword-matching rule-based fallback.
        
        This method serves as a reliable safety net for offline runs, local testing,
        and live demo fail-safes. It customizes replies depending on accessibility preferences
        parsed from the system prompt.
        """
        msg = user_message.lower()
        sys = system_prompt.lower()

        # Determine accessibility constraints from system prompt context
        is_wheelchair = "wheelchair" in sys or "wheelchair" in msg
        is_visual = "visual" in sys or "visual" in msg
        is_cognitive = "cognitive" in sys or "cognitive" in msg

        # Customize responses based on accessibility requirements
        if is_wheelchair:
            restroom_tip = "Step-free, accessible restrooms are located directly on the main concourse near Section 112 (left of the entrance ramp)."
            exit_tip = "Step-free exit routes and ADA ramps are located at Gate A and Gate C. Elevators are available adjacent to the main ticketing concourse."
            food_tip = "Accessible lower-counter concessions are available at Section 105 (Burger Grill) and Section 120 (Taco Stand), both have ramp access."
            seat_tip = "Your wheelchair-accessible seating platform is in Section 114, Row W. Follow the ramp on the left."
            transport_tip = "ADA-compliant shuttle buses depart from Lot C every 10 minutes. Accessible rideshare pickup is at Gate 2."
            sustain_tip = "Accessible recycling bins and water bottle refill stations are located at Section 108 next to the elevator."
        elif is_visual:
            restroom_tip = "Restrooms are located 50 feet ahead on your left, past the concession stand at Section 112. The door has tactile braille signs."
            exit_tip = "The nearest exit is Gate A, located straight ahead for 150 yards from the Section 101 corridor."
            food_tip = "Concessions are 30 yards to the right. Stands include Section 105 (Burger Grill) and Section 120 (Taco Stand)."
            seat_tip = "To find Section 114, locate the Section 112 marker on your left, then walk 20 paces forward."
            transport_tip = "Metro station entrance is 200 yards directly east of the main gate. Accessible shuttle buses are parked in Lot C to the north-east."
            sustain_tip = "A water refill station is 10 paces past Section 108 on the right side wall."
        elif is_cognitive:
            restroom_tip = "Restrooms are at Section 112. They are easy to find and have large signs."
            exit_tip = "Exits are at Gate A. Just follow the green exit signs."
            food_tip = "Food stands are at Section 105 and Section 120. They sell burgers, hotdogs, and water."
            seat_tip = "Go to Section 114. Look for the blue seat signs. Staff in yellow shirts can help you."
            transport_tip = "Buses are in Lot C. The Metro is nearby. Both are safe and clean."
            sustain_tip = "Recycle bottles in the blue bins. Water stations are near Section 108."
        else:
            restroom_tip = "Restrooms are located on the main concourse near Sections 112 and 131."
            exit_tip = "Exits are located at Gate A (North), Gate B (East), and Gate C (South)."
            food_tip = "Concession stands are located throughout the concourse. Popular options include the Burger Grill at Section 105 and Taco Stand at Section 120."
            seat_tip = "Please look at the directional signage on the concourse walls. Section numbers are clearly marked above the seating entry tunnels."
            transport_tip = "The Metro station is a 5-minute walk from Gate A. Shuttle buses are located in Lot C. Rideshare pickup is at Gate 2."
            sustain_tip = "Please use the blue recycling bins located at every section entrance. Water refill stations are available near Section 108 and 124."

        # Keyword matching
        if any(kw in msg for kw in ["restroom", "toilet", "bathroom", "wc"]):
            return f"{restroom_tip} Please let me know if you need help finding anything else."
        elif any(kw in msg for kw in ["exit", "gate", "leave", "out"]):
            return f"{exit_tip} Thank you for visiting the stadium today!"
        elif any(kw in msg for kw in ["food", "eat", "drink", "beer", "hungry", "thirsty", "concession"]):
            return f"Hungry? {food_tip} Soft drinks and water are also sold there."
        elif any(kw in msg for kw in ["seat", "section", "find", "where is my", "where's my"]):
            return f"{seat_tip} Volunteers in yellow vests are standing by to guide you."
        elif any(kw in msg for kw in ["transport", "metro", "bus", "shuttle", "uber", "rideshare", "park", "car"]):
            return f"Here is the transport info: {transport_tip} Expect moderate post-match delays."
        elif any(kw in msg for kw in ["sustainability", "recycle", "water", "green", "trash", "environment"]):
            return f"Eco Nudge: {sustain_tip} Help us keep the FIFA World Cup 2026 green!"
        elif any(kw in msg for kw in ["accessibility", "wheelchair", "step-free", "elevator", "ramp"]):
            return f"Accessibility Guidance: {exit_tip} {restroom_tip}"
        
        # Generic helpful assistant answer
        return (
            "Hello! I am your FIFA World Cup 2026 Stadium Assistant. "
            "I can help you locate restrooms, find food stalls, get step-free routing, "
            "view transport schedules, or learn about our stadium recycling program. "
            "What can I help you with today?"
        )

# Global client singleton instance
genai_client = GenAIClient()
