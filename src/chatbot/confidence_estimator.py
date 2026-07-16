"""
confidence_estimator.py — Match Confidence Scoring
====================================================
Assigns a confidence level to each matched symptom based on how
it was found.

Confidence levels (from constants.py):
  HIGH   — exact dictionary match (phrase in synonym_index)
  MEDIUM — fuzzy match above FUZZY_HIGH_THRESHOLD
  LOW    — fuzzy match in FUZZY_MEDIUM–FUZZY_HIGH range, or heuristic

Also exposes:
  confidence_score(level) → float  (HIGH=1.0, MEDIUM=0.7, LOW=0.4)

No external deps.
"""

from src.chatbot.constants import Confidence

# Numeric scores for downstream sorting / filtering
_SCORE_MAP: dict[str, float] = {
    Confidence.HIGH:   1.0,
    Confidence.MEDIUM: 0.7,
    Confidence.LOW:    0.4,
}


def confidence_score(level: str) -> float:
    """Return a float confidence score for the given level string."""
    return _SCORE_MAP.get(level, 0.0)


def estimate_from_fuzzy_score(fuzzy_score: int) -> str:
    """
    Translate a RapidFuzz integer similarity score (0-100) to a
    Confidence level.

    Parameters
    ----------
    fuzzy_score : int, 0-100

    Returns
    -------
    Confidence.HIGH | Confidence.MEDIUM | Confidence.LOW
    """
    from src.chatbot.constants import (
        FUZZY_HIGH_THRESHOLD,
        FUZZY_MEDIUM_THRESHOLD,
        FUZZY_LOW_THRESHOLD,
    )
    if fuzzy_score >= FUZZY_HIGH_THRESHOLD:
        return Confidence.HIGH
    if fuzzy_score >= FUZZY_MEDIUM_THRESHOLD:
        return Confidence.MEDIUM
    if fuzzy_score >= FUZZY_LOW_THRESHOLD:
        return Confidence.LOW
    return Confidence.LOW  # only reached if caller allows lower scores


def filter_by_confidence(
    items: list[tuple],
    min_level: str = Confidence.LOW,
    key_fn=None,
) -> list[tuple]:
    """
    Filter a list of (symptom, confidence_level) tuples by minimum confidence.

    Parameters
    ----------
    items     : list of tuples where one element is a confidence level string
    min_level : minimum acceptable confidence ("high", "medium", "low")
    key_fn    : callable that extracts the confidence level from each item
                (defaults to item[1])
    """
    if key_fn is None:
        key_fn = lambda item: item[1]

    min_score = _SCORE_MAP.get(min_level, 0.0)
    return [item for item in items if _SCORE_MAP.get(key_fn(item), 0.0) >= min_score]
