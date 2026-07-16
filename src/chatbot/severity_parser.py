"""
severity_parser.py — Severity Detection
========================================
Extracts severity information from user text and maps it to a numeric score.

Output
------
- detect_severity(text) → tuple[str | None, int]
  returns (severity_label, severity_score) where score is 1-4.
  Returns (None, 0) if no severity marker found.

Scale (from constants.py):
  1 = mild / slight / occasional
  2 = moderate / recurring
  3 = severe / persistent / continuous
  4 = extreme / excruciating / very severe

No external deps.
"""

import re
from src.chatbot.constants import SEVERITY_SCALE


# Sort phrases by length (longest first) to prefer specific matches
_SORTED_SEVERITY_PHRASES = sorted(
    SEVERITY_SCALE.keys(),
    key=len,
    reverse=True,
)


def detect_severity(text: str) -> tuple[str | None, int]:
    """
    Detect severity level from text.

    Returns
    -------
    (label, score) where label is the matched phrase and score is 1-4.
    (None, 0) if no severity marker found.
    """
    lower = text.lower()

    # Try longest match first
    for phrase in _SORTED_SEVERITY_PHRASES:
        # Use word-boundary aware matching
        pattern = r"(?<!\w)" + re.escape(phrase) + r"(?!\w)"
        if re.search(pattern, lower):
            score = SEVERITY_SCALE[phrase]
            return phrase, score

    return None, 0


def severity_label(score: int) -> str:
    """Return a human-readable label for a severity score."""
    if score == 0:
        return "unspecified"
    if score == 1:
        return "mild"
    if score == 2:
        return "moderate"
    if score == 3:
        return "severe"
    return "extreme"
