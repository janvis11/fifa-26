"""
Transport service for the Fan Journey Concierge.

Returns simulated transit options and generates a context-aware GenAI recommendation
based on the user's accessibility need and the time left to kickoff.
"""

import datetime
from backend.models import TransportResponse, TransportOption, AccessibilityNeed
from backend.genai_client import genai_client


def _get_default_options() -> list[TransportOption]:
    """Returns baseline simulated transit options for stadium egress/ingress."""
    return [
        TransportOption(
            mode="Metro Rail",
            eta_minutes=10,
            accessibility_friendly=True,
            notes="Station is located 400m East of Gate A. Fully accessible elevators available.",
        ),
        TransportOption(
            mode="Express Shuttle",
            eta_minutes=15,
            accessibility_friendly=True,
            notes="Departs from Lot C (North Deck) every 10 minutes. Ramp and kneeling buses.",
        ),
        TransportOption(
            mode="Rideshare Zone",
            eta_minutes=25,
            accessibility_friendly=False,
            notes="Designated zone at Gate 2. Expect traffic congestion and longer wait times.",
        ),
        TransportOption(
            mode="General Walkway",
            eta_minutes=0,
            accessibility_friendly=True,
            notes="Well-lit paved pathways to external parking lots. Steep ramp near South Lot.",
        ),
    ]


def _get_mock_transport_recommendation(
    accessibility_need: AccessibilityNeed,
    minutes_to_kickoff: int | None,
) -> str:
    """Provides deterministic rule-based recommendations when running in offline/mock mode."""
    if accessibility_need == "wheelchair":
        return (
            "The Express Shuttle (Lot C) is recommended. It features specialized ADA-compliant ramps, "
            "lower boarding heights, and direct drops to the main gate with zero stairways."
        )
    if minutes_to_kickoff is not None and minutes_to_kickoff < 30:
        return (
            "The Metro Rail is the fastest choice to reach the gate before kickoff (10 minutes wait time). "
            "Avoid the rideshare zone as traffic lines are highly congested."
        )
    return (
        "The Metro Rail is recommended as the most efficient and reliable public transit option. "
        "It is a short walk from Gate A and runs on dedicated tracks away from road traffic."
    )


def _generate_transport_recommendation(
    options: list[TransportOption],
    accessibility_need: AccessibilityNeed,
    minutes_to_kickoff: int | None,
) -> str:
    """Orchestrates GenAI recommendation generation with fallback to deterministic rules."""
    system_prompt = (
        "You are a Stadium Transport Coordinator. Review the available transit options and the fan's context "
        "to suggest the single best transport option. Be concise (2 sentences max)."
    )

    context_str = f"Accessibility Need: {accessibility_need}. "
    if minutes_to_kickoff is not None:
        context_str += f"Time to Kickoff: {minutes_to_kickoff} minutes. "
    else:
        context_str += "Time to Kickoff: Not specified (post-match exit). "

    options_summary = "; ".join(
        [
            f"{o.mode} (ETA: {o.eta_minutes}m, ADA: {o.accessibility_friendly}, Notes: {o.notes})"
            for o in options
        ]
    )

    user_message = f"User Context: {context_str}. Available options: {options_summary}. What is the best transit recommendation?"

    recommendation = genai_client.complete(
        system_prompt=system_prompt, user_message=user_message, max_tokens=150
    )

    if genai_client.mode == "mock":
        return _get_mock_transport_recommendation(
            accessibility_need, minutes_to_kickoff
        )

    return recommendation


def get_transport_options(
    _stadium_id: str,
    accessibility_need: AccessibilityNeed = "none",
    minutes_to_kickoff: int | None = None,
) -> TransportResponse:
    """
    Returns available transit choices and computes the best recommendation via GenAI.
    """
    options = _get_default_options()
    recommendation = _generate_transport_recommendation(
        options, accessibility_need, minutes_to_kickoff
    )
    generated_at = datetime.datetime.now(datetime.UTC).isoformat() + "Z"

    return TransportResponse(
        options=options,
        recommendation=recommendation,
        mode=genai_client.mode,
        generated_at=generated_at,
    )
