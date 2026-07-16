"""
negation_detector.py — Negation Detection
==========================================
Determines whether symptom candidates in a sentence are negated.

Algorithm
---------
1. Tokenize the sentence
2. Find all negation cue positions
3. For any token within NEGATION_WINDOW positions after a cue, mark as negated
4. Expose is_negated(phrase, text) for single-phrase checks
5. Expose negated_positions(text) → set[int] for full-sentence analysis

No ML, no external deps.
"""

import re
from src.chatbot.constants import NEGATION_CUES, NEGATION_WINDOW


def _tokenize(text: str) -> list[str]:
    """Simple whitespace tokenizer (lowercased, punctuation stripped)."""
    # Strip trailing punctuation from each token so 'headache.' == 'headache'
    tokens = re.split(r"\s+", text.lower().strip())
    return [re.sub(r"[^\w'-]", "", t) for t in tokens if re.sub(r"[^\w'-]", "", t)]


def negated_token_positions(text: str) -> set[int]:
    """
    Return the set of token indices that are within the negation window
    of any negation cue.

    Example
    -------
    "I do not have fever or headache" → {4, 5, 6} (fever, or, headache)
    """
    tokens = _tokenize(text)
    negated: set[int] = set()

    # Multi-word cues must be checked first (longest match)
    multi_cues = sorted(
        [c for c in NEGATION_CUES if " " in c],
        key=lambda c: -len(c.split()),
    )
    single_cues = [c for c in NEGATION_CUES if " " not in c]

    n = len(tokens)
    cue_positions: set[int] = set()

    # Check multi-word cues
    for cue in multi_cues:
        cue_tokens = cue.split()
        cue_len = len(cue_tokens)
        for i in range(n - cue_len + 1):
            if tokens[i : i + cue_len] == cue_tokens:
                cue_positions.add(i)
                # Mark the tokens of the cue itself as the boundary
                for j in range(i, min(i + cue_len + NEGATION_WINDOW, n)):
                    negated.add(j)

    # Check single-word cues (only if not already part of multi-word)
    for i, token in enumerate(tokens):
        if token in single_cues and i not in cue_positions:
            cue_positions.add(i)
            for j in range(i, min(i + 1 + NEGATION_WINDOW, n)):
                negated.add(j)

    return negated


def is_negated(phrase: str, text: str) -> bool:
    """
    Return True if the phrase appears to be negated within text.

    Strategy: find the phrase in the token sequence and check if any
    of its token positions are in the negated set.
    """
    tokens = _tokenize(text)
    phrase_tokens = _tokenize(phrase)
    phrase_len = len(phrase_tokens)
    negated = negated_token_positions(text)

    for i in range(len(tokens) - phrase_len + 1):
        if tokens[i : i + phrase_len] == phrase_tokens:
            # If any token of the phrase is in the negated window → negated
            if any((i + k) in negated for k in range(phrase_len)):
                return True

    return False


def split_clauses(text: str) -> list[str]:
    """
    Split text into clauses at conjunctions and punctuation so that
    negation scope does not bleed across clause boundaries.

    Example
    -------
    "I don't have fever but I do have cough" → ["I don't have fever", "I do have cough"]
    """
    # Split on: ', but', '. ', '; ', ' and ', ' however ', ' although '
    parts = re.split(r"[,;]\s*|\s+but\s+|\s+however\s+|\s+although\s+|\.\s+", text, flags=re.IGNORECASE)
    return [p.strip() for p in parts if p.strip()]
