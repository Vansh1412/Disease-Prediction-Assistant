"""
synonym_index.py — O(1) Reverse Lookup Index
=============================================
Builds a flat phrase → canonical_symptom dict from the medical dictionary.

Responsibilities
----------------
- Import medical_dictionary.SYMPTOM_SYNONYMS
- Flatten it into {phrase: canonical} with O(1) lookup
- Cache the result so it is built only once per process lifetime
- Expose get_canonical(phrase) for direct lookups

This module has NO external runtime dependencies beyond the stdlib.
"""

import logging
from functools import lru_cache
from src.chatbot.medical_dictionary import SYMPTOM_SYNONYMS

logger = logging.getLogger(__name__)


@lru_cache(maxsize=1)
def _build_index() -> dict[str, str]:
    """
    Build and return the phrase → canonical symptom reverse lookup dict.
    The lru_cache ensures this runs exactly once per process lifetime.
    """
    index: dict[str, str] = {}
    conflicts = 0
    for canonical, phrases in SYMPTOM_SYNONYMS:
        for phrase in phrases:
            key = phrase.lower().strip()
            if key in index and index[key] != canonical:
                logger.debug(
                    "SynonymIndex: phrase '%s' maps to both '%s' and '%s'; keeping first.",
                    key, index[key], canonical,
                )
                conflicts += 1
            else:
                index[key] = canonical
    logger.info(
        "SynonymIndex: built %d phrase → symptom mappings (%d conflicts).",
        len(index), conflicts,
    )
    return index


def get_index() -> dict[str, str]:
    """Return the complete phrase → canonical index."""
    return _build_index()


def get_canonical(phrase: str) -> str | None:
    """
    Return the canonical symptom name for a phrase, or None if not found.
    Lookup is O(1).
    """
    return _build_index().get(phrase.lower().strip())


def all_phrases() -> list[str]:
    """Return all known synonym phrases (useful for fuzzy matching corpus)."""
    return list(_build_index().keys())


def all_canonicals() -> list[str]:
    """Return all canonical symptom names covered by the dictionary."""
    return list(set(_build_index().values()))


def reset() -> None:
    """Clear the cached index (useful in tests after dictionary changes)."""
    _build_index.cache_clear()
