"""
Chat service for the Fan Journey Concierge.

Handles building the system prompt from the user context, calling the GenAI client,
and generating dynamic suggested action cards based on the reply text.
"""

from backend.models import ChatRequest, ChatResponse
from backend.genai_client import genai_client
from backend.personas import build_system_prompt

# ---------------------------------------------------------------------------
# Module-level keyword sets for suggested-action detection.
# Keeping them here avoids re-allocating the same lists on every request.
# ---------------------------------------------------------------------------

_TRANSPORT_KW: list[str] = [
    "transport",
    "metro",
    "bus",
    "shuttle",
    "uber",
    "rideshare",
    "walk",
    "lot",
]
_FOOD_KW: list[str] = ["food", "eat", "drink", "beer", "hungry", "concession", "snack"]
_RESTROOM_KW: list[str] = ["restroom", "toilet", "bathroom", "wc"]
_SUSTAIN_KW: list[str] = [
    "sustainability",
    "recycle",
    "water",
    "green",
    "trash",
    "environment",
]


def _build_suggested_actions(reply_lower: str) -> list[str]:
    """
    Derives context-aware quick-action labels from the reply text.

    Why keyword-scanning the reply rather than the request: the GenAI response
    may introduce topics the user didn't explicitly ask about (e.g. mentioning
    the Metro when answering a seating question), so scanning the reply gives
    more relevant action cards than scanning the incoming message.
    """
    actions: list[str] = []
    if any(kw in reply_lower for kw in _TRANSPORT_KW):
        actions.append("View Transport Options")
    if any(kw in reply_lower for kw in _FOOD_KW):
        actions.append("Locate Concessions")
    if any(kw in reply_lower for kw in _RESTROOM_KW):
        actions.append("Find Nearest Restroom")
    if any(kw in reply_lower for kw in _SUSTAIN_KW):
        actions.append("View Sustainability Tips")

    # Guarantee at least two action cards for UX consistency
    if not actions:
        return ["Check Crowd Levels", "Find Near Exit"]
    if len(actions) < 2:
        fallback = (
            "Find Near Exit"
            if "Check Crowd Levels" in actions
            else "Check Crowd Levels"
        )
        actions.append(fallback)
    return actions


def get_chat_response(request: ChatRequest) -> ChatResponse:
    """
    Processes a chat request and returns a persona-aware reply with action cards.

    The user's free-text message is passed exclusively to the GenAI `user`
    message slot — it never touches the system prompt — to prevent prompt injection.
    Suggested actions are derived from the reply content, not the request.
    """
    system_prompt = build_system_prompt(request.context)

    # Securely call GenAI complete (free text goes ONLY in user message slot)
    reply = genai_client.complete(
        system_prompt=system_prompt, user_message=request.message, max_tokens=400
    )

    suggested_actions = _build_suggested_actions(reply.lower())

    return ChatResponse(
        reply=reply,
        persona=request.context.persona,
        mode=genai_client.mode,
        suggested_actions=suggested_actions,
    )
