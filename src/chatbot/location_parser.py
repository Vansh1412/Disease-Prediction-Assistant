"""
location_parser.py — Body Location Detection
=============================================
Extracts body location mentions from user text.

Output
------
- detect_locations(text) → list[str]
  Returns list of normalized body location labels found in text.

Uses the BODY_LOCATIONS lookup from constants.py.
No external deps.
"""

import re
from src.chatbot.constants import BODY_LOCATIONS

# Build a flat phrase → location_label lookup, longest phrase first
_PHRASE_TO_LOCATION: dict[str, str] = {}
for location, phrases in BODY_LOCATIONS.items():
    for phrase in phrases:
        _PHRASE_TO_LOCATION[phrase.lower()] = location

_SORTED_PHRASES = sorted(_PHRASE_TO_LOCATION.keys(), key=len, reverse=True)


def detect_locations(text: str) -> list[str]:
    """
    Detect all body location references in text.

    Returns a deduplicated list of canonical body location labels.
    Longer phrases take priority (e.g., 'lower abdomen' before 'abdomen').

    Parameters
    ----------
    text : raw or normalized user text

    Returns
    -------
    list[str] of canonical location names found
    """
    lower = text.lower()
    found_locations: list[str] = []
    matched_spans: list[tuple[int, int]] = []

    for phrase in _SORTED_PHRASES:
        pattern = r"(?<!\w)" + re.escape(phrase) + r"(?!\w)"
        for m in re.finditer(pattern, lower):
            start, end = m.span()
            # Ensure no overlap with already matched spans
            if not any(s < end and start < e for s, e in matched_spans):
                location = _PHRASE_TO_LOCATION[phrase]
                if location not in found_locations:
                    found_locations.append(location)
                matched_spans.append((start, end))

    return found_locations


def enrich_symptom_with_location(symptom: str, locations: list[str]) -> list[str]:
    """
    Given a generic symptom (e.g. 'pain') and detected locations,
    try to construct more specific symptom names.

    This is a best-effort heuristic — if no specific symptom exists,
    the original is returned unchanged.

    Examples
    --------
    enrich_symptom_with_location("pain", ["arm"])  → ["arm pain"]
    enrich_symptom_with_location("pain", ["lower back"])  → ["low back pain"]
    """
    # Mapping from generic symptom + location to specific canonical symptom
    _ENRICHMENT_MAP: dict[tuple[str, str], str] = {
        ("pain", "arm"): "arm pain",
        ("pain", "back"): "back pain",
        ("pain", "lower back"): "low back pain",
        ("pain", "neck"): "neck pain",
        ("pain", "chest"): "chest tightness",
        ("pain", "knee"): "knee pain",
        ("pain", "shoulder"): "shoulder pain",
        ("pain", "leg"): "leg pain",
        ("pain", "foot"): "foot or toe pain",
        ("pain", "hand"): "hand or finger pain",
        ("pain", "wrist"): "wrist pain",
        ("pain", "elbow"): "elbow pain",
        ("pain", "hip"): "hip pain",
        ("pain", "ankle"): "ankle pain",
        ("pain", "abdomen"): "upper abdominal pain",
        ("pain", "lower abdomen"): "lower abdominal pain",
        ("pain", "upper abdomen"): "upper abdominal pain",
        ("pain", "jaw"): "jaw pain",
        ("pain", "ear"): "ear pain",
        ("pain", "eye"): "pain in eye",
        ("swelling", "ankle"): "ankle swelling",
        ("swelling", "leg"): "leg swelling",
        ("swelling", "knee"): "knee swelling",
        ("swelling", "arm"): "arm swelling",
        ("stiffness", "knee"): "knee stiffness or tightness",
        ("stiffness", "back"): "back stiffness or tightness",
        ("stiffness", "neck"): "neck stiffness or tightness",
        ("weakness", "arm"): "arm weakness",
        ("weakness", "leg"): "leg weakness",
    }

    enriched = []
    for loc in locations:
        key = (symptom.lower(), loc.lower())
        if key in _ENRICHMENT_MAP:
            enriched.append(_ENRICHMENT_MAP[key])

    return enriched if enriched else [symptom]
