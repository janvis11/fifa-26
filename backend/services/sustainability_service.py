"""
Sustainability service for the Fan Journey Concierge.

Provides static and template-based eco-friendly stadium tips.
Enforces the efficiency rule (no GenAI API calls for deterministic data).
"""

from backend.models import SustainabilityResponse
from backend.data.stadium_data import get_stadium


def get_sustainability_info(stadium_id: str) -> SustainabilityResponse:
    """
    Returns nearest recycling points and eco-tips for the given stadium.

    Deliberately avoids any GenAI API call: sustainability tips are static
    and deterministic, so calling the model would add latency and cost with
    zero benefit. Zone list indices are used to select locations so the
    result varies by stadium without hardcoding per-stadium values.
    """
    stadium = get_stadium(stadium_id)
    zones = stadium["zones"]

    # Deterministically select locations based on zones list
    nearest_recycling = zones[0] if len(zones) > 0 else "Main Entrance"
    nearest_water = (
        zones[2] if len(zones) > 2 else (zones[-1] if len(zones) > 0 else "Section 108")
    )

    # Generic, high-impact tips
    tips = [
        "Use the blue recycling bins located at every entry tunnel to dispose of plastic cups and cans.",
        f"Bring your reusable water bottle and fill it up for free at the station near '{nearest_water}'.",
        "Consider using the Metro Rail or public express shuttles to reduce your carbon footprint.",
        "Help us make FIFA World Cup 2026 zero-waste by sorting compostable food wrappers separately.",
    ]

    return SustainabilityResponse(
        tips=tips,
        nearest_recycling_zone=nearest_recycling,
        nearest_water_refill=nearest_water,
    )
