"""
Translation service for the Fan Journey Concierge.

Provides multilingual assistance. Utilizes GenAI in live mode,
and a local phrasebook dictionary in mock mode with a placeholder fallback.
"""

from backend.models import TranslateResponse
from backend.genai_client import genai_client

# Local phrasebook dictionary for mock mode
PHRASEBOOK = {
    "where is the nearest restroom?": {
        "es": "¿Dónde está el baño más cercano?",
        "fr": "Où sont les toilettes les plus proches?",
        "de": "Wo ist die nächste Toilette?",
        "pt": "Onde fica o banheiro mais próximo?",
    },
    "how do i exit the stadium?": {
        "es": "¿Cómo salgo del estadio?",
        "fr": "Comment sortir du stade?",
        "de": "Wie verlasse ich das Stadion?",
        "pt": "Como faço para sair do estádio?",
    },
    "where can i find food?": {
        "es": "¿Dónde puedo encontrar comida?",
        "fr": "Où puis-je trouver de la nourriture?",
        "de": "Wo finde ich Essen?",
        "pt": "Onde posso encontrar comida?",
    },
    "where is my seat?": {
        "es": "¿Dónde está mi asiento?",
        "fr": "Où est mon siège?",
        "de": "Wo ist mein Sitzplatz?",
        "pt": "Onde fica o meu assento?",
    },
    "thank you": {"es": "Gracias", "fr": "Merci", "de": "Danke", "pt": "Obrigado"},
}


def translate(text: str, target_lang: str) -> TranslateResponse:
    """
    Translates input text into the target language.
    Uses Anthropic in live mode and a phrasebook/placeholder logic in mock mode.
    """
    normalized_lang = target_lang.strip().lower()
    normalized_text = text.strip().lower().rstrip(".?!")

    # Check if we should use the live GenAI client
    if genai_client.mode == "live":
        system_prompt = (
            "You are a professional translator. Translate the user's text into the target language "
            f"code '{normalized_lang}'. Return ONLY the translated text, with no explanations, "
            "no preamble, and no conversational filler."
        )
        translated_text = genai_client.complete(
            system_prompt=system_prompt, user_message=text, max_tokens=500
        )
        return TranslateResponse(translated_text=translated_text.strip(), mode="live")
    else:
        # Mock mode phrasebook lookup
        # Clean up input text for matching
        lookup_key = (
            normalized_text + "?"
            if "restroom" in normalized_text
            or "exit" in normalized_text
            or "food" in normalized_text
            or "seat" in normalized_text
            else normalized_text
        )

        # Check phrasebook
        matched_dict = PHRASEBOOK.get(normalized_text) or PHRASEBOOK.get(lookup_key)
        if matched_dict and normalized_lang in matched_dict:
            return TranslateResponse(
                translated_text=matched_dict[normalized_lang], mode="mock"
            )

        # Fallback text if not matched
        fallback_text = f"[{normalized_lang}] {text}"
        return TranslateResponse(translated_text=fallback_text, mode="mock")
