"""
Chat service for the Fan Journey Concierge.

Handles building the system prompt from the user context, calling the GenAI client,
and generating dynamic suggested action cards based on the reply text.
"""

from typing import List
from backend.models import ChatRequest, ChatResponse
from backend.genai_client import genai_client
from backend.personas import build_system_prompt


def get_chat_response(request: ChatRequest) -> ChatResponse:
    """
    Processes chat requests using the built persona prompts and context attributes.

    Determines dynamic suggested action cards based on keywords in the reply.
    """
    system_prompt = build_system_prompt(request.context)

    # Securely call GenAI complete (free text goes ONLY in user message slot)
    reply = genai_client.complete(
        system_prompt=system_prompt, user_message=request.message, max_tokens=400
    )

    # Suggested actions based on response content keyword matching (efficiency rule)
    reply_lower = reply.lower()
    suggested_actions: List[str] = []

    if any(
        kw in reply_lower
        for kw in [
            "transport",
            "metro",
            "bus",
            "shuttle",
            "uber",
            "rideshare",
            "walk",
            "lot",
        ]
    ):
        suggested_actions.append("View Transport Options")
    if any(
        kw in reply_lower
        for kw in ["food", "eat", "drink", "beer", "hungry", "concession", "snack"]
    ):
        suggested_actions.append("Locate Concessions")
    if any(kw in reply_lower for kw in ["restroom", "toilet", "bathroom", "wc"]):
        suggested_actions.append("Find Nearest Restroom")
    if any(
        kw in reply_lower
        for kw in [
            "sustainability",
            "recycle",
            "water",
            "green",
            "trash",
            "environment",
        ]
    ):
        suggested_actions.append("View Sustainability Tips")

    # Standard fallback actions
    if not suggested_actions:
        suggested_actions = ["Check Crowd Levels", "Find Near Exit"]
    elif len(suggested_actions) < 2:
        if "Check Crowd Levels" not in suggested_actions:
            suggested_actions.append("Check Crowd Levels")
        else:
            suggested_actions.append("Find Near Exit")

    return ChatResponse(
        reply=reply,
        persona=request.context.persona,
        mode=genai_client.mode,
        suggested_actions=suggested_actions,
    )
