"""
Crowd service for the Fan Journey Concierge.

Simulates deterministic crowd density based on stadium zone names and current time,
and requests a GenAI recommendation for operations when bottlenecks exist.
"""

import datetime
import hashlib
from backend.models import CrowdResponse, ZoneStatus, DensityLevel
from backend.data.stadium_data import get_stadium
from backend.genai_client import genai_client


def _get_minute_bucket() -> str:
    """Returns the current UTC time bucketed to the nearest minute."""
    now = datetime.datetime.now(datetime.UTC)
    return now.strftime("%Y-%m-%d %H:%M")


def _generate_density_pct(stadium_id: str, zone_name: str, time_bucket: str) -> int:
    """
    Generates a deterministic density percentage (0-100) seeded by stadium,
    zone, and time. Process-independent and stable within the current minute.
    """
    seed_str = f"{stadium_id}:{zone_name}:{time_bucket}"
    hash_val = hashlib.sha256(seed_str.encode("utf-8")).hexdigest()
    # Take first 8 hex characters and map to range 0-100
    val = int(hash_val[:8], 16)
    return val % 101


def _get_density_level(pct: int) -> DensityLevel:
    """Maps density percentage to category level."""
    if pct < 35:
        return "low"
    elif pct < 65:
        return "medium"
    elif pct < 85:
        return "high"
    else:
        return "critical"


def _get_zone_recommendation(level: DensityLevel) -> str:
    """Returns a deterministic action recommendation based on density level."""
    if level == "low":
        return "Flow is smooth. Good time to visit this area."
    elif level == "medium":
        return "Standard congestion. Normal waits apply."
    elif level == "high":
        return "Heavy congestion. Avoid if possible; expect queues."
    else:
        return "Critical bottleneck. Restrict movement and follow staff directions."


def _calculate_trend_and_history(
    stadium_id: str, zone_name: str
) -> tuple[str, list[int]]:
    """
    Computes a deterministic historical trend (10m ago, 5m ago, now) for a zone.
    Why: Provides operational intelligence trends without requiring a live database.
    """
    now = datetime.datetime.now(datetime.UTC)
    t_now = now.strftime("%Y-%m-%d %H:%M")
    t_5 = (now - datetime.timedelta(minutes=5)).strftime("%Y-%m-%d %H:%M")
    t_10 = (now - datetime.timedelta(minutes=10)).strftime("%Y-%m-%d %H:%M")

    pct_10 = _generate_density_pct(stadium_id, zone_name, t_10)
    pct_5 = _generate_density_pct(stadium_id, zone_name, t_5)
    pct_now = _generate_density_pct(stadium_id, zone_name, t_now)

    history = [pct_10, pct_5, pct_now]

    # Calculate trend direction
    diff = pct_now - pct_10
    if diff > 10:
        trend = "rising"
    elif diff < -10:
        trend = "falling"
    else:
        trend = "stable"

    return trend, history


def _generate_zones_status(
    stadium: dict, time_bucket: str
) -> tuple[list[ZoneStatus], bool]:
    """
    Simulates crowd status for all stadium zones and checks if any zone is congested.
    Why: Keeps zone loop logic separated from prompt construction for better readability.
    """
    zones_status: list[ZoneStatus] = []
    has_congested_zone = False

    for zone_name in stadium["zones"]:
        zone_id = zone_name.strip().lower().replace(" ", "_")
        pct = _generate_density_pct(stadium["id"], zone_name, time_bucket)
        level = _get_density_level(pct)
        trend, history = _calculate_trend_and_history(stadium["id"], zone_name)

        if level in ("high", "critical"):
            has_congested_zone = True

        zones_status.append(
            ZoneStatus(
                zone_id=zone_id,
                name=zone_name,
                density_level=level,
                density_pct=pct,
                recommendation=_get_zone_recommendation(level),
                trend=trend,
                recent_history=history,
            )
        )
    return zones_status, has_congested_zone


def _get_overall_recommendation(
    zones_status: list[ZoneStatus], has_congested_zone: bool
) -> str:
    """
    Compiles an overall operations recommendation using GenAI or a default message.
    Why: Separates GenAI prompt generation details to keep the primary service entry point clean.
    """
    if has_congested_zone:
        system_prompt = (
            "You are a Stadium Operations Assistant. You review crowd status and provide "
            "a single short, action-oriented overall recommendation for organizers and fans."
        )
        zones_summary = ", ".join(
            [f"{z.name}: {z.density_level} ({z.density_pct}%)" for z in zones_status]
        )
        user_message = f"Here is the current stadium zone density: {zones_summary}. What is the overall recommendation?"

        return genai_client.complete(
            system_prompt=system_prompt, user_message=user_message, max_tokens=150
        )
    return "All zones operating within normal capacity limits. Standard egress patterns apply."


def get_crowd_status(stadium_id: str) -> CrowdResponse:
    """
    Generates the current crowd status simulation for a stadium.
    Calls GenAI for an overall recommendation ONLY if one or more zones are congested.
    """
    stadium = get_stadium(stadium_id)
    time_bucket = _get_minute_bucket()

    zones_status, has_congested_zone = _generate_zones_status(stadium, time_bucket)
    overall_recommendation = _get_overall_recommendation(
        zones_status, has_congested_zone
    )
    generated_at = datetime.datetime.now(datetime.UTC).isoformat() + "Z"

    return CrowdResponse(
        stadium_id=stadium["id"],
        generated_at=generated_at,
        zones=zones_status,
        overall_recommendation=overall_recommendation,
    )
