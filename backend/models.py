"""
Data models for the Fan Journey Concierge.

Defines Pydantic schemas for request validation and response serialization.
Ensure strict type hints and length limits are applied to prevent unsafe inputs.
"""

from typing import List, Literal, Optional
from pydantic import BaseModel, Field, field_validator

# Enums defined using Literal as requested in the prompts
Persona = Literal["fan", "volunteer", "organizer", "venue_staff"]
AccessibilityNeed = Literal[
    "none", "wheelchair", "visual", "hearing", "cognitive", "elderly"
]
DensityLevel = Literal["low", "medium", "high", "critical"]


class UserContext(BaseModel):
    """
    Contextual information about the active user in the stadium.
    Allows customization of responses based on accessibility preferences,
    current location (gate, section), stadium, and language.
    """

    persona: Persona = Field(
        default="fan", description="The user persona navigating the stadium."
    )
    stadium_id: str = Field(
        ...,
        min_length=1,
        max_length=50,
        description="The unique identifier of the stadium.",
    )
    gate: Optional[str] = Field(None, max_length=20, description="Optional entry gate.")
    seat_section: Optional[str] = Field(
        None, max_length=20, description="Optional seating section."
    )
    language: str = Field(
        "en",
        min_length=2,
        max_length=8,
        description="Language preference (e.g. 'en', 'es').",
    )
    accessibility_need: AccessibilityNeed = Field(
        "none", description="Accessibility accommodations requested."
    )
    minutes_to_kickoff: Optional[int] = Field(
        None, ge=-180, le=360, description="Remaining minutes until match kickoff."
    )

    @field_validator("language")
    @classmethod
    def validate_language(cls, v: str) -> str:
        """Validates that language code is purely alphanumeric."""
        if not v.isalnum():
            raise ValueError("language code must contain only alphanumeric characters")
        return v.lower()


class ChatRequest(BaseModel):
    """
    Schema for user chat message requests.
    Validates limits on message length to mitigate potential abuse/DOS.
    """

    message: str = Field(
        ..., min_length=1, max_length=1000, description="The user's query or message."
    )
    context: UserContext = Field(
        ..., description="The context of the user sending the message."
    )


class ChatResponse(BaseModel):
    """
    Schema for the assistant's reply.
    Identifies which mode (live/mock) handled the response.
    """

    reply: str = Field(..., description="The assistant's text response.")
    persona: Persona = Field(..., description="The persona the assistant responded as.")
    mode: str = Field(..., description="The processing mode (live or mock).")
    suggested_actions: List[str] = Field(
        default_factory=list, description="Context-aware quick actions."
    )


class TranslateRequest(BaseModel):
    """
    Schema for translation requests.
    """

    text: str = Field(
        ..., min_length=1, max_length=5000, description="The text to translate."
    )
    target_lang: str = Field(
        ..., min_length=2, max_length=8, description="Target language code (e.g. 'es')."
    )

    @field_validator("target_lang")
    @classmethod
    def validate_target_lang(cls, v: str) -> str:
        """Validates that target language code is purely alphanumeric."""
        if not v.isalnum():
            raise ValueError("target_lang must contain only alphanumeric characters")
        return v.lower()


class TranslateResponse(BaseModel):
    """
    Schema for translation responses.
    """

    translated_text: str = Field(..., description="The translated text content.")
    mode: str = Field(..., description="The mode that performed the translation.")


class ZoneStatus(BaseModel):
    """
    Details of a specific stadium zone's crowd level.
    Used for both the fan experience and the operational dashboard.
    """

    zone_id: str = Field(..., description="Unique zone identifier.")
    name: str = Field(..., description="Human-readable zone name.")
    density_level: DensityLevel = Field(
        ..., description="Categorized crowd density level."
    )
    density_pct: int = Field(
        ..., ge=0, le=100, description="Simulated density percentage."
    )
    recommendation: str = Field(
        ..., description="Actionable recommendation for this zone."
    )
    trend: str = Field(
        default="stable",
        description="Trend direction over the last 10 minutes (rising, falling, stable).",
    )
    recent_history: List[int] = Field(
        default_factory=list,
        description="Historical density percentages at [-10m, -5m, now].",
    )


class CrowdResponse(BaseModel):
    """
    Aggregated crowd status response for a stadium.
    """

    stadium_id: str = Field(..., description="Stadium ID.")
    generated_at: str = Field(
        ..., description="ISO 8601 timestamp of simulation generation."
    )
    zones: List[ZoneStatus] = Field(
        ..., description="List of stadium zones with statuses."
    )
    overall_recommendation: str = Field(
        ..., description="Overall narrative recommendation."
    )


class TransportOption(BaseModel):
    """
    A single transportation option for leaving/arriving at the stadium.
    """

    mode: str = Field(..., description="Transport mode (e.g. 'Metro', 'Shuttle').")
    eta_minutes: int = Field(
        ..., ge=0, description="Estimated arrival/waiting time in minutes."
    )
    accessibility_friendly: bool = Field(
        ..., description="Whether this option supports accessibility needs."
    )
    notes: str = Field(..., description="Description or instructions.")


class TransportResponse(BaseModel):
    """
    Response schema returning available transport options and recommendations.
    """

    options: List[TransportOption] = Field(
        ..., description="List of available transport choices."
    )
    recommendation: str = Field(
        ..., description="GenAI recommendation for the best option."
    )
    mode: str = Field(..., description="Mode of generation (live or mock).")
    generated_at: str = Field(..., description="Generation timestamp.")


class SustainabilityResponse(BaseModel):
    """
    Sustainability tips and eco-friendly features near the user.
    """

    tips: List[str] = Field(
        ..., description="List of personalized sustainability tips."
    )
    nearest_recycling_zone: str = Field(
        ..., description="Name of the closest recycling point."
    )
    nearest_water_refill: str = Field(
        ..., description="Name of the closest water refill station."
    )
