"""
temporal_parser.py — Temporal Expression Detection
===================================================
Classifies temporal expressions in user text as CURRENT, PAST, or UNKNOWN.

Output
------
- temporal_tag(text) → "current" | "past" | "unknown"
- extract_duration(text) → str | None  (e.g. "3 days", "2 weeks")

Only CURRENT symptoms should be forwarded to the ML predictor.
PAST symptoms are stored separately.

No external deps.
"""

import re
from src.chatbot.constants import TEMPORAL_CURRENT, TEMPORAL_PAST, TEMPORAL_DURATION_PATTERNS

# Time unit normalization (to days) for duration scoring
_UNIT_TO_DAYS: dict[str, float] = {
    "hour": 1 / 24, "hours": 1 / 24,
    "day": 1.0,     "days": 1.0,
    "week": 7.0,    "weeks": 7.0,
    "month": 30.0,  "months": 30.0,
    "year": 365.0,  "years": 365.0,
}


def temporal_tag(text: str) -> str:
    """
    Return the temporal classification of the text:
      "current" — symptoms are happening now / recently
      "past"    — symptoms happened in the past
      "unknown" — no temporal marker found (default to current)
    """
    lower = text.lower()

    # Check past markers first (more specific)
    for marker in TEMPORAL_PAST:
        if marker in lower:
            return "past"

    # Check current markers
    for marker in TEMPORAL_CURRENT:
        if marker in lower:
            return "current"

    # Regex patterns that imply ongoing ("for X days", "since")
    for pattern in TEMPORAL_DURATION_PATTERNS:
        if re.search(pattern, lower):
            return "current"

    return "unknown"


def extract_duration(text: str) -> str | None:
    """
    Extract a human-readable duration string from text if present.

    Examples
    --------
    "I've had a headache for 3 days" → "3 days"
    "fever since yesterday"          → "since yesterday"
    "cough for 2 weeks"              → "2 weeks"
    """
    lower = text.lower()

    # "for N unit"
    m = re.search(
        r"for (\d+)\s*(hours?|days?|weeks?|months?|years?)",
        lower,
    )
    if m:
        return f"{m.group(1)} {m.group(2)}"

    # "past N unit"
    m = re.search(
        r"past (\d+)\s*(hours?|days?|weeks?|months?|years?)",
        lower,
    )
    if m:
        return f"{m.group(1)} {m.group(2)}"

    # "since yesterday / last week / this morning"
    m = re.search(r"since (yesterday|last\s+\w+|this\s+\w+)", lower)
    if m:
        return f"since {m.group(1)}"

    # "N unit ago"
    m = re.search(
        r"(\d+)\s*(hours?|days?|weeks?|months?|years?)\s*ago",
        lower,
    )
    if m:
        return f"{m.group(1)} {m.group(2)} ago"

    return None


def duration_to_days(duration_str: str) -> float | None:
    """
    Convert a duration string like "3 days" or "2 weeks" to a float number of days.
    Returns None if it cannot be parsed.
    """
    if not duration_str:
        return None

    m = re.search(
        r"(\d+)\s*(hours?|days?|weeks?|months?|years?)",
        duration_str.lower(),
    )
    if m:
        qty = float(m.group(1))
        unit = m.group(2).lower()
        factor = _UNIT_TO_DAYS.get(unit, 1.0)
        return qty * factor

    return None
