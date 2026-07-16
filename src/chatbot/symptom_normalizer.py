"""
symptom_normalizer.py — Text Cleaning & Tokenization
======================================================
Responsibilities
----------------
1. Clean raw user text (lower, strip, normalize whitespace, remove punctuation)
2. Tokenize into candidate n-gram windows (unigrams through 5-grams)
3. Expose normalize(text) → clean string
4. Expose tokenize(text) → list of candidate phrases (longest first)

No ML, no LLM, no external deps beyond stdlib.
"""

import re
import unicodedata

# ---------------------------------------------------------------------------
# Contraction expansion — run before tokenization
# ---------------------------------------------------------------------------

_CONTRACTIONS: dict[str, str] = {
    "i'm": "i am",
    "i've": "i have",
    "i'll": "i will",
    "i'd": "i would",
    "i can't": "i cannot",
    "can't": "cannot",
    "don't": "do not",
    "doesn't": "does not",
    "didn't": "did not",
    "haven't": "have not",
    "hasn't": "has not",
    "won't": "will not",
    "wouldn't": "would not",
    "couldn't": "could not",
    "shouldn't": "should not",
    "it's": "it is",
    "that's": "that is",
    "there's": "there is",
    "they're": "they are",
    "we're": "we are",
    "you're": "you are",
    "i'm not": "i am not",
    "i don't": "i do not",
    "it doesn't": "it does not",
}


def _expand_contractions(text: str) -> str:
    """Expand common contractions before tokenization."""
    lower = text.lower()
    for contraction, expansion in _CONTRACTIONS.items():
        lower = lower.replace(contraction, expansion)
    return lower


# ---------------------------------------------------------------------------
# Normalization
# ---------------------------------------------------------------------------

def normalize(text: str) -> str:
    """
    Return a cleaned, lowercased, whitespace-normalized version of the text.

    Steps:
    1. Unicode normalize (NFKD → ASCII where possible)
    2. Expand contractions
    3. Remove non-printable characters
    4. Collapse multiple spaces
    5. Strip
    """
    # Unicode normalize
    text = unicodedata.normalize("NFKD", text)
    text = text.encode("ascii", "ignore").decode("ascii")

    # Lowercase + contractions
    text = _expand_contractions(text)

    # Remove non-printable
    text = re.sub(r"[^\x20-\x7E]", " ", text)

    # Collapse whitespace
    text = re.sub(r"\s+", " ", text).strip()

    return text


# ---------------------------------------------------------------------------
# Tokenization into n-gram candidate phrases
# ---------------------------------------------------------------------------

_STOP_WORDS = frozenset({
    "a", "an", "the", "and", "or", "but", "is", "are", "was", "were",
    "be", "been", "being", "have", "has", "had", "do", "does", "did",
    "will", "would", "shall", "should", "may", "might", "must",
    "can", "could", "to", "for", "from", "with", "at", "by", "on",
    "in", "out", "of", "up", "about", "into", "through",
    "i", "me", "my", "myself", "we", "our", "you", "your", "he",
    "she", "it", "they", "them", "this", "that", "these", "those",
    "am", "im", "ive",
})


def _clean_for_tokenization(text: str) -> str:
    """Remove punctuation that is not part of medical terms (keep hyphens, apostrophes in words)."""
    # Keep alphanumeric, space, hyphen, apostrophe
    text = re.sub(r"[^a-z0-9\s'\-]", " ", text)
    return re.sub(r"\s+", " ", text).strip()


def tokenize(text: str, max_ngram: int = 5) -> list[str]:
    """
    Tokenize normalized text into candidate phrases (n-grams from max_ngram down to 1).
    Longer phrases are yielded first so exact multi-word symptoms take priority.

    Parameters
    ----------
    text     : normalized text (output of normalize())
    max_ngram: maximum n-gram window size

    Returns
    -------
    list of candidate phrase strings, longest first, deduped
    """
    cleaned = _clean_for_tokenization(text)
    tokens = cleaned.split()

    seen: set[str] = set()
    candidates: list[str] = []

    # Yield from largest window downward
    for n in range(max_ngram, 0, -1):
        for i in range(len(tokens) - n + 1):
            phrase = " ".join(tokens[i : i + n])
            if phrase not in seen:
                seen.add(phrase)
                candidates.append(phrase)

    return candidates
