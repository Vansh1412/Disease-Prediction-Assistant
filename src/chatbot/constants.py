"""
constants.py — Clinical NLP Pipeline Constants
================================================
Single source of truth for all shared constants used across the NLP modules.
Nothing is imported from other chatbot modules here to avoid circular deps.
"""

# ---------------------------------------------------------------------------
# Severity scale
# ---------------------------------------------------------------------------

SEVERITY_SCALE: dict[str, int] = {
    "mild":       1,
    "slight":     1,
    "minor":      1,
    "light":      1,
    "moderate":   2,
    "medium":     2,
    "significant":2,
    "severe":     3,
    "strong":     3,
    "intense":    3,
    "serious":    3,
    "very severe":4,
    "extreme":    4,
    "excruciating":4,
    "unbearable": 4,
    "worst":      4,
    "persistent": 3,
    "constant":   3,
    "continuous":  3,
    "chronic":    3,
    "recurring":  2,
    "occasional": 1,
    "intermittent":1,
    "on and off":  1,
    "comes and goes":1,
}

# ---------------------------------------------------------------------------
# Negation cues
# ---------------------------------------------------------------------------

NEGATION_CUES: list[str] = [
    "no", "not", "don't", "do not", "doesn't", "does not",
    "didn't", "did not", "haven't", "have not", "hasn't", "has not",
    "without", "never", "none", "neither", "nor", "lack of",
    "absence of", "deny", "denies", "denied", "free from", "negative for",
    "no history of", "no sign of", "ruled out",
]

# Negation scope: max tokens after a negation cue to mark as negated
NEGATION_WINDOW: int = 6

# ---------------------------------------------------------------------------
# Temporal cues — maps phrase → category
# ---------------------------------------------------------------------------

TEMPORAL_CURRENT: list[str] = [
    "today", "now", "currently", "right now", "at the moment",
    "just", "just now", "since morning", "this morning", "tonight",
    "this evening", "this afternoon", "this week", "recently",
    "at present", "ongoing",
]

TEMPORAL_PAST: list[str] = [
    "yesterday", "last week", "last month", "last year",
    "last night", "two days ago", "three days ago",
    "a week ago", "a month ago", "before", "previously",
    "in the past", "used to", "had", "once", "formerly",
    "a few days ago", "some time ago", "earlier",
]

TEMPORAL_DURATION_PATTERNS: list[str] = [
    # Regex-compatible strings for duration extraction
    r"for (\d+)\s*(day|days|week|weeks|month|months|hour|hours|year|years)",
    r"(\d+)\s*(day|days|week|weeks|month|months|hour|hours|year|years)\s*ago",
    r"since (yesterday|last\s+\w+|this\s+\w+)",
    r"since (\d+)\s*(day|days|week|weeks|month|months)",
    r"past (\d+)\s*(day|days|week|weeks|month|months|hour|hours)",
    r"last (\d+)\s*(day|days|week|weeks|month|months|hour|hours)",
]

# ---------------------------------------------------------------------------
# Body location keywords
# ---------------------------------------------------------------------------

BODY_LOCATIONS: dict[str, list[str]] = {
    "left arm":      ["left arm", "left hand", "left wrist", "left elbow", "left shoulder"],
    "right arm":     ["right arm", "right hand", "right wrist", "right elbow", "right shoulder"],
    "left chest":    ["left chest", "left side of chest", "left breast"],
    "right chest":   ["right chest", "right side of chest", "right breast"],
    "chest":         ["chest", "breast bone", "sternum", "thorax"],
    "jaw":           ["jaw", "chin", "mandible"],
    "neck":          ["neck", "throat", "nape"],
    "abdomen":       ["abdomen", "belly", "stomach area", "tummy"],
    "lower abdomen": ["lower abdomen", "lower belly", "pelvic area", "groin", "lower stomach"],
    "upper abdomen": ["upper abdomen", "upper belly", "epigastric", "below ribs"],
    "back":          ["back", "spine", "spinal", "vertebrae", "lumbar", "upper back"],
    "lower back":    ["lower back", "lumbar region", "lumbosacral"],
    "eye":           ["eye", "eyes", "eyelid", "pupil", "retina", "iris"],
    "ear":           ["ear", "ears", "inner ear", "eardrum"],
    "leg":           ["leg", "calf", "shin", "thigh", "lower leg"],
    "knee":          ["knee", "kneecap", "patella"],
    "foot":          ["foot", "feet", "toe", "toes", "heel", "ankle"],
    "hand":          ["hand", "finger", "fingers", "thumb", "palm"],
    "shoulder":      ["shoulder", "rotator cuff"],
    "hip":           ["hip", "pelvis"],
    "head":          ["head", "scalp", "skull", "forehead", "temple"],
    "face":          ["face", "cheek", "nose", "nostril", "forehead", "facial"],
    "skin":          ["skin", "body surface", "dermal"],
    "groin":         ["groin", "inguinal"],
    "wrist":         ["wrist", "carpal"],
    "elbow":         ["elbow"],
    "ankle":         ["ankle", "malleolus"],
}

# ---------------------------------------------------------------------------
# Emergency symptom combinations
# ---------------------------------------------------------------------------

# Each tuple: (set_of_symptoms_that_together_are_emergencies, warning_message)
EMERGENCY_COMBINATIONS: list[tuple[set, str]] = [
    (
        {"chest pain", "chest tightness", "left arm pain", "arm pain", "sweating", "nausea", "jaw pain"},
        "⚠️ Possible cardiac emergency (heart attack). Call emergency services immediately."
    ),
    (
        {"facial pain", "slurring words", "arm weakness", "difficulty speaking", "dizziness", "loss of sensation"},
        "⚠️ Possible stroke. Call emergency services immediately — time is critical."
    ),
    (
        {"shortness of breath", "difficulty breathing", "chest tightness", "wheezing"},
        "⚠️ Severe breathing difficulty detected. Seek immediate medical attention."
    ),
    (
        {"seizures", "loss of consciousness", "fainting"},
        "⚠️ Neurological emergency detected. Call emergency services immediately."
    ),
    (
        {"vomiting blood", "blood in stool", "rectal bleeding", "hemoptysis"},
        "⚠️ Serious bleeding detected. Seek emergency care immediately."
    ),
]

# Keywords that alone trigger emergency (single-symptom emergencies)
EMERGENCY_SINGLE_KEYWORDS: list[str] = [
    "heart attack", "stroke", "anaphylaxis", "anaphylactic", "cardiac arrest",
    "can't breathe", "cannot breathe", "not breathing", "stopped breathing",
    "bleeding out", "kill myself", "suicide", "suicidal",
    "loss of consciousness", "passed out", "unconscious", "overdose",
]

# ---------------------------------------------------------------------------
# Fuzzy matching threshold
# ---------------------------------------------------------------------------

FUZZY_HIGH_THRESHOLD: int = 90    # → HIGH confidence
FUZZY_MEDIUM_THRESHOLD: int = 75  # → MEDIUM confidence
FUZZY_LOW_THRESHOLD: int = 60     # → LOW confidence (included but flagged)

# ---------------------------------------------------------------------------
# Confidence labels
# ---------------------------------------------------------------------------

class Confidence:
    HIGH   = "high"
    MEDIUM = "medium"
    LOW    = "low"
