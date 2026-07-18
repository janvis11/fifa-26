"""
Stadium data module for the Fan Journey Concierge.

Contains information about the host stadiums for the FIFA World Cup 2026,
including names, locations, and active zones. Provides a safe retrieval helper.
"""

from typing import Dict, Any, List

# Static dictionary of FIFA World Cup 2026 host stadiums
STADIUMS: Dict[str, Dict[str, Any]] = {
    "metlife": {
        "id": "metlife",
        "name": "MetLife Stadium",
        "city": "East Rutherford, NJ",
        "zones": [
            "Concourse A",
            "Concourse B",
            "Concourse C",
            "Concourse D",
            "West Plaza",
            "East Gate",
        ],
    },
    "sofi": {
        "id": "sofi",
        "name": "SoFi Stadium",
        "city": "Inglewood, CA",
        "zones": [
            "Entry Plaza",
            "Level 4 Concourse",
            "Level 6 Concourse",
            "VIP Club East",
            "South Canopy",
        ],
    },
    "azteca": {
        "id": "azteca",
        "name": "Estadio Azteca",
        "city": "Mexico City",
        "zones": [
            "General Concourse",
            "Preferente Concourse",
            "Platea Gate",
            "Special Access Ramp",
            "Especial Club",
        ],
    },
    "bc_place": {
        "id": "bc_place",
        "name": "BC Place",
        "city": "Vancouver, BC",
        "zones": [
            "Main Concourse",
            "Upper Level 400",
            "Terry Fox Plaza",
            "West Gate Entrance",
            "Disabled Seating Deck",
        ],
    },
}

# Default fallback stadium to prevent raising errors when user enters an invalid ID
DEFAULT_STADIUM_ID = "metlife"


def get_stadium(stadium_id: str | None) -> Dict[str, Any]:
    """
    Retrieves stadium configuration details by its ID.

    If the requested stadium_id is not found or is None, it defaults to the MetLife stadium configuration
    to prevent application crashes on invalid user input.
    """
    if not stadium_id:
        return STADIUMS[DEFAULT_STADIUM_ID]

    normalized_id = stadium_id.strip().lower()
    return STADIUMS.get(normalized_id, STADIUMS[DEFAULT_STADIUM_ID])


def get_all_stadiums() -> List[Dict[str, str]]:
    """
    Returns a list of all supported stadiums with their ID, name, and city.
    Useful for populating dropdown selections in the UI.
    """
    return [
        {"id": key, "name": val["name"], "city": val["city"]}
        for key, val in STADIUMS.items()
    ]
