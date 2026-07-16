"""
question_bank.py — Structured Clinical Question Bank
=====================================================
Provides all follow-up questions organized by symptom group.

Structure per group
--------------------
  primary      — first questions to ask about this symptom
  secondary    — deeper follow-up once primary is answered
  confirmation — yes/no checks to confirm symptom is present
  red_flag     — questions probing dangerous features

NO logic here — pure data.
Used by followup_generator.py to select questions.
"""

from __future__ import annotations

# ---------------------------------------------------------------------------
# Type alias
# ---------------------------------------------------------------------------

QuestionGroup = dict[str, list[str]]

# ---------------------------------------------------------------------------
# Master bank
# key  = canonical symptom name (or symptom cluster)
# ---------------------------------------------------------------------------

QUESTION_BANK: dict[str, QuestionGroup] = {

    # ── Fever ───────────────────────────────────────────────────────────────
    "fever": {
        "primary": [
            "Have you measured your temperature? If so, what was it?",
            "How long have you had the fever?",
            "Are you experiencing any chills or shivering?",
        ],
        "secondary": [
            "Are you sweating heavily?",
            "Have you taken any fever-reducing medication like paracetamol or ibuprofen?",
            "Is the fever constant or does it come and go in waves?",
        ],
        "confirmation": [
            "Is the temperature above 38°C (100.4°F)?",
            "Do you feel hot to the touch?",
        ],
        "red_flag": [
            "Are you experiencing any confusion or difficulty staying awake?",
            "Do you have a stiff neck along with the fever?",
            "Have you had any febrile seizures?",
        ],
    },

    # ── Headache ────────────────────────────────────────────────────────────
    "headache": {
        "primary": [
            "Is the headache on one side or both sides of your head?",
            "How long has the headache lasted?",
            "How would you rate the pain on a scale of 1 to 10?",
        ],
        "secondary": [
            "Is the headache throbbing, pressing, or stabbing?",
            "Does it get worse with light, sound, or movement?",
            "Are you experiencing any nausea or vomiting with it?",
        ],
        "confirmation": [
            "Is this headache different from ones you have had before?",
            "Do you have any visual disturbances like flashing lights?",
        ],
        "red_flag": [
            "Did the headache come on very suddenly — like a thunderclap?",
            "Do you have any neck stiffness along with the headache?",
            "Is there any weakness or numbness in your limbs?",
        ],
    },

    # ── Chest pain / tightness ─────────────────────────────────────────────
    "chest pain": {
        "primary": [
            "Is the chest pain sharp and stabbing, or more of a pressure or squeezing sensation?",
            "Where exactly in the chest is the pain?",
            "How long has the pain been present?",
        ],
        "secondary": [
            "Does the pain radiate to your left arm, jaw, neck, or back?",
            "Are you short of breath along with the chest pain?",
            "Are you sweating or feeling nauseous?",
        ],
        "confirmation": [
            "Does the pain get worse when you breathe deeply or cough?",
            "Does it improve with rest or antacids?",
        ],
        "red_flag": [
            "Are you having any palpitations or feeling that your heart is racing?",
            "Have you fainted or nearly fainted?",
            "Do you have a history of heart disease?",
        ],
    },
    "chest tightness": {
        "primary": [
            "Is the tightness constant or does it come and go?",
            "Does it get worse with physical activity?",
            "Are you having any difficulty breathing along with the tightness?",
        ],
        "secondary": [
            "Do you hear any wheezing when you breathe?",
            "Does the tightness spread to your arm, jaw, or back?",
            "Have you had episodes like this before?",
        ],
        "confirmation": [
            "Is there any cough with the chest tightness?",
        ],
        "red_flag": [
            "Are you sweating or feeling very anxious suddenly?",
            "Do you have any numbness in your left arm?",
        ],
    },

    # ── Cough ───────────────────────────────────────────────────────────────
    "cough": {
        "primary": [
            "Is your cough dry or are you producing mucus or phlegm?",
            "How long have you been coughing?",
            "Is the cough worse at any particular time of day?",
        ],
        "secondary": [
            "What colour is the mucus, if any? (clear, yellow, green, or bloody?)",
            "Are you experiencing any shortness of breath with the cough?",
            "Do you have a fever alongside the cough?",
        ],
        "confirmation": [
            "Is the cough persistent throughout the day?",
            "Does it worsen when you lie down?",
        ],
        "red_flag": [
            "Have you coughed up any blood?",
            "Do you have night sweats or unexplained weight loss?",
        ],
    },

    # ── Shortness of breath ─────────────────────────────────────────────────
    "shortness of breath": {
        "primary": [
            "Is the breathlessness present at rest or only during activity?",
            "How long have you been experiencing difficulty breathing?",
            "Do you hear any wheezing or whistling when you breathe?",
        ],
        "secondary": [
            "Do you have any chest tightness along with it?",
            "Are you able to lie flat comfortably, or do you need to sit up?",
            "Have you had any recent exposure to allergens, smoke, or chemicals?",
        ],
        "confirmation": [
            "Are you unable to speak full sentences without pausing to breathe?",
        ],
        "red_flag": [
            "Are your lips or fingertips turning blue?",
            "Did the breathlessness come on very suddenly?",
        ],
    },
    "difficulty breathing": {
        "primary": [
            "Is it harder to breathe in, breathe out, or both?",
            "Did it start suddenly or gradually?",
            "Is there any wheezing or chest tightness?",
        ],
        "secondary": [
            "Are you at rest or did it start after exertion?",
            "Have you been around any triggers such as dust, pollen, or animals?",
        ],
        "confirmation": [],
        "red_flag": [
            "Are your lips or fingernails turning blue or grey?",
            "Are you feeling confused or very drowsy?",
        ],
    },

    # ── Nausea / vomiting ───────────────────────────────────────────────────
    "nausea": {
        "primary": [
            "How long have you been feeling nauseous?",
            "Is the nausea related to eating, or does it occur on its own?",
            "Have you actually vomited, or just felt the urge to?",
        ],
        "secondary": [
            "Is there any abdominal pain associated with the nausea?",
            "Have you recently eaten anything unusual or that could be spoiled?",
            "Are you able to keep fluids down?",
        ],
        "confirmation": [
            "Does the nausea come in waves or is it constant?",
        ],
        "red_flag": [
            "Is there any blood in what you vomited?",
            "Are you severely dehydrated — very dry mouth, no urine output?",
        ],
    },
    "vomiting": {
        "primary": [
            "How many times have you vomited?",
            "How long has the vomiting been going on?",
            "Are you able to keep any fluids down at all?",
        ],
        "secondary": [
            "Is there blood in the vomit?",
            "Do you have abdominal pain along with it?",
            "Have you had any diarrhoea as well?",
        ],
        "confirmation": [
            "Do you feel better after vomiting, or does the nausea persist?",
        ],
        "red_flag": [
            "Is the vomit dark brown or coffee-ground coloured?",
            "Are you unable to keep even small sips of water down for more than a few hours?",
        ],
    },

    # ── Abdominal pain variants ─────────────────────────────────────────────
    "lower abdominal pain": {
        "primary": [
            "Is the pain constant or does it come and go in cramps?",
            "Does it spread to your back or groin?",
            "Do you have any urinary symptoms like burning or increased frequency?",
        ],
        "secondary": [
            "For women: is this related to your menstrual cycle?",
            "Do you have any diarrhoea, constipation, or changes in bowel habit?",
            "Is the pain worse when you press on the area?",
        ],
        "confirmation": [
            "Is the pain below the navel?",
        ],
        "red_flag": [
            "Is the pain severe and sudden, like a knife?",
            "Do you have any fever with the abdominal pain?",
        ],
    },
    "upper abdominal pain": {
        "primary": [
            "Does the pain get worse after eating, drinking alcohol, or fatty meals?",
            "Is the pain burning or gnawing in character?",
            "Does it spread to your back?",
        ],
        "secondary": [
            "Do you have heartburn or acid reflux?",
            "Have you taken NSAIDs like aspirin or ibuprofen recently?",
            "Is there any nausea or vomiting?",
        ],
        "confirmation": [
            "Is the pain mainly in the centre or right side of the upper abdomen?",
        ],
        "red_flag": [
            "Is the pain very severe and sudden in onset?",
            "Is your skin or the whites of your eyes turning yellow?",
        ],
    },
    "abdominal pain": {
        "primary": [
            "Where exactly in the abdomen is the pain — upper, lower, central, or all over?",
            "Is the pain sharp, dull, crampy, or burning?",
            "How long have you had the pain?",
        ],
        "secondary": [
            "Is it related to eating or bowel movements?",
            "Do you have any nausea, vomiting, or diarrhoea?",
        ],
        "confirmation": [],
        "red_flag": [
            "Is the abdomen hard or very tender to touch?",
            "Do you have a high fever with the pain?",
        ],
    },

    # ── Dizziness ───────────────────────────────────────────────────────────
    "dizziness": {
        "primary": [
            "Does the dizziness feel like the room is spinning (vertigo), or more like you might faint?",
            "Is it worse when you change position, such as standing up quickly?",
            "How long does each episode last?",
        ],
        "secondary": [
            "Is it associated with any nausea or vomiting?",
            "Have you had any changes in your hearing or ringing in your ears?",
            "Have you had any falls as a result?",
        ],
        "confirmation": [
            "Is the dizziness constant or does it come in episodes?",
        ],
        "red_flag": [
            "Do you have any difficulty speaking or walking alongside the dizziness?",
            "Did you have any head injury recently?",
        ],
    },

    # ── Fatigue ─────────────────────────────────────────────────────────────
    "fatigue": {
        "primary": [
            "How long have you been feeling this way?",
            "Is the tiredness present even after a full night's sleep?",
            "Is it affecting your ability to carry out daily activities?",
        ],
        "secondary": [
            "Have you had any recent illness, infection, or significant stress?",
            "Do you have any changes in your appetite or weight?",
            "Are you sleeping more than usual or having trouble sleeping?",
        ],
        "confirmation": [
            "Is this fatigue new, or have you always been low in energy?",
        ],
        "red_flag": [
            "Do you have any unexplained weight loss along with the fatigue?",
            "Are you experiencing night sweats?",
        ],
    },

    # ── Back / musculoskeletal ───────────────────────────────────────────────
    "back pain": {
        "primary": [
            "Is the pain in your upper, middle, or lower back?",
            "Does it radiate down into your legs?",
            "Is it constant, or does it come and go?",
        ],
        "secondary": [
            "Does rest improve it or make it worse?",
            "Have you had any recent injury, fall, or heavy lifting?",
            "Is there any numbness or tingling in your legs or feet?",
        ],
        "confirmation": [
            "Is it worse first thing in the morning?",
        ],
        "red_flag": [
            "Do you have any loss of bladder or bowel control?",
            "Do you have any weakness in your legs?",
        ],
    },
    "low back pain": {
        "primary": [
            "Does the pain travel down one or both legs?",
            "Is there any numbness or tingling in your legs or feet?",
            "Is it worse when sitting, standing, or walking?",
        ],
        "secondary": [
            "Have you had any recent injury or sudden movement?",
            "Does it improve when you lie down?",
        ],
        "confirmation": [],
        "red_flag": [
            "Have you had any loss of control of your bladder or bowel?",
            "Is there any weakness in your legs?",
        ],
    },

    # ── Joint pain ──────────────────────────────────────────────────────────
    "joint pain": {
        "primary": [
            "Which joints are affected?",
            "Are the joints swollen, red, or warm to touch?",
            "How long have you had joint pain?",
        ],
        "secondary": [
            "Is the pain symmetric — affecting the same joints on both sides?",
            "Is it worse in the morning and does it improve after moving around?",
            "Have you had any recent injury or infection?",
        ],
        "confirmation": [
            "Is joint stiffness present, especially in the morning?",
        ],
        "red_flag": [
            "Is any single joint severely swollen, hot, and very painful?",
            "Do you have a fever along with joint pain?",
        ],
    },

    # ── Skin ────────────────────────────────────────────────────────────────
    "skin rash": {
        "primary": [
            "Where on your body is the rash?",
            "Is it raised, flat, blistered, or scaly?",
            "How long has it been present?",
        ],
        "secondary": [
            "Is it itchy, painful, or neither?",
            "Have you been exposed to any new substances, foods, or environments?",
            "Does anyone else at home or work have a similar rash?",
        ],
        "confirmation": [
            "Is the rash spreading?",
        ],
        "red_flag": [
            "Do you have difficulty breathing or swelling of the face with the rash?",
            "Is the rash associated with a high fever?",
        ],
    },

    # ── Respiratory ─────────────────────────────────────────────────────────
    "sore throat": {
        "primary": [
            "Is it painful to swallow?",
            "How long have you had the sore throat?",
            "Do you have a fever along with it?",
        ],
        "secondary": [
            "Do you see any white patches or pus on the tonsils?",
            "Do you have any swollen glands in your neck?",
            "Do you have a runny nose or nasal congestion as well?",
        ],
        "confirmation": [
            "Is the throat visibly red when you look in the mirror?",
        ],
        "red_flag": [
            "Is it painful or difficult to open your mouth fully?",
            "Is the uvula (the hanging bit at the back) pushed to one side?",
        ],
    },

    # ── Sleep / mood ─────────────────────────────────────────────────────────
    "insomnia": {
        "primary": [
            "Do you have trouble falling asleep, staying asleep, or both?",
            "How many hours of sleep are you getting on average?",
            "How long has the sleep problem been going on?",
        ],
        "secondary": [
            "Are you experiencing anxiety, stress, or racing thoughts at night?",
            "Do you wake up early and cannot go back to sleep?",
            "Are you doing anything in bed other than sleeping, like using your phone?",
        ],
        "confirmation": [
            "Do you feel refreshed after the sleep you do get?",
        ],
        "red_flag": [],
    },
    "depression": {
        "primary": [
            "How long have you been feeling this way?",
            "Are you able to enjoy activities you used to enjoy?",
            "How is your sleep and appetite?",
        ],
        "secondary": [
            "Are you experiencing low energy or motivation?",
            "Have you had any thoughts of self-harm or hopelessness?",
            "Are you finding it difficult to concentrate?",
        ],
        "confirmation": [
            "Is this a significant change from how you normally feel?",
        ],
        "red_flag": [
            "Are you having any thoughts of harming yourself or others?",
        ],
    },
    "anxiety and nervousness": {
        "primary": [
            "How long have you been feeling anxious?",
            "Is there a specific trigger, or does it feel like a constant background anxiety?",
            "Are you having any panic attacks?",
        ],
        "secondary": [
            "Is the anxiety affecting your daily life, work, or relationships?",
            "Are you experiencing any physical symptoms like a racing heart or shortness of breath?",
            "Are you avoiding situations because of the anxiety?",
        ],
        "confirmation": [
            "Is the anxiety new or have you struggled with it before?",
        ],
        "red_flag": [
            "Are you having thoughts of harming yourself?",
        ],
    },

    # ── Urinary ─────────────────────────────────────────────────────────────
    "frequent urination": {
        "primary": [
            "How many times are you urinating in a 24-hour period?",
            "Is there any burning or pain when you urinate?",
            "Are you also drinking more fluids than usual?",
        ],
        "secondary": [
            "Do you wake up at night to urinate?",
            "Is there any blood in your urine?",
            "Do you have any lower abdominal or back pain?",
        ],
        "confirmation": [
            "Is the amount of urine each time normal, or just small amounts?",
        ],
        "red_flag": [
            "Is there blood in your urine?",
            "Do you have a fever and lower back pain — which could indicate a kidney infection?",
        ],
    },

    # ── Cardiac ─────────────────────────────────────────────────────────────
    "irregular heartbeat": {
        "primary": [
            "Does your heart feel like it is racing, fluttering, pounding, or skipping beats?",
            "How long do episodes last?",
            "How often do they occur?",
        ],
        "secondary": [
            "Are you dizzy or light-headed during an episode?",
            "Do you have chest pain or shortness of breath with it?",
            "Have you had any blackouts or near-fainting?",
        ],
        "confirmation": [
            "Can you tap the rhythm of the palpitations for me to understand the pattern?",
        ],
        "red_flag": [
            "Have you ever lost consciousness during an episode?",
            "Do you have a known heart condition?",
        ],
    },
    "palpitations": {
        "primary": [
            "How would you describe the palpitations — racing, fluttering, or irregular?",
            "How long do they last?",
            "Are they brought on by anything, such as caffeine, stress, or exercise?",
        ],
        "secondary": [
            "Do you have chest pain, breathlessness, or dizziness with them?",
        ],
        "confirmation": [],
        "red_flag": [
            "Have you ever fainted or nearly fainted during an episode?",
        ],
    },

    # ── General / catch-all ─────────────────────────────────────────────────
    "default": {
        "primary": [
            "How long have you been experiencing this?",
            "How severe would you say it is on a scale of 1 to 10?",
            "Is it constant or does it come and go?",
        ],
        "secondary": [
            "Have you tried any treatments or taken any medications for it?",
            "Are there any other symptoms you have noticed alongside this?",
            "Does anything make it better or worse?",
        ],
        "confirmation": [
            "Is this a new problem or something you have had before?",
        ],
        "red_flag": [
            "Have you had any sudden worsening recently?",
        ],
    },
}

# ---------------------------------------------------------------------------
# Demographic questions (asked early if unknown)
# ---------------------------------------------------------------------------

DEMOGRAPHIC_QUESTIONS: dict[str, str] = {
    "age":    "Could you tell me your age? This helps me give you more relevant information.",
    "gender": "Could you tell me your gender? This can be relevant for certain conditions.",
}

# ---------------------------------------------------------------------------
# Opening / greeting questions
# ---------------------------------------------------------------------------

OPENING_QUESTIONS: list[str] = [
    "Hello! I'm MediSense AI. I'm here to help you understand your symptoms. Could you describe how you are feeling today?",
    "Hello! I'll ask you a few questions to understand your symptoms better. Please start by telling me what's bothering you.",
    "Welcome to MediSense AI. I'm here to help you assess your symptoms. What are you experiencing today?",
]

# ---------------------------------------------------------------------------
# Closing / transition phrases
# ---------------------------------------------------------------------------

TRANSITION_TO_PREDICTION = (
    "Thank you for sharing that information. Based on what you've told me, "
    "I now have enough information to provide you with an assessment."
)

TRANSITION_TO_MORE_INFO = (
    "Thank you. I have a few more questions to better understand your situation."
)


# ---------------------------------------------------------------------------
# Helper
# ---------------------------------------------------------------------------

def get_questions_for_symptom(symptom: str) -> QuestionGroup:
    """Return the question group for a canonical symptom, or the default group."""
    return QUESTION_BANK.get(symptom, QUESTION_BANK["default"])
