"""
medical_dictionary.py — Clinical Synonym Dictionary
=====================================================
Maps natural human language expressions → canonical dataset symptom names.

Coverage: all 377 symptom columns in the ML dataset.
Expressions per symptom: 20-50 natural language variants including:
  - Lay person descriptions
  - Medical terminology
  - Common misspellings (handled by fuzzy matcher, not listed here)
  - Colloquial phrases
  - Regional variations

This file is pure data — no logic, no imports.
"""

# ---------------------------------------------------------------------------
# SYMPTOM_MAP: phrase (lowercase) → canonical symptom name
# Each entry is a tuple of phrases that all map to the same canonical name.
# Built as a list of (canonical, [phrases]) and then flattened in synonym_index.
# ---------------------------------------------------------------------------

SYMPTOM_SYNONYMS: list[tuple[str, list[str]]] = [

    # ── A ──────────────────────────────────────────────────────────────────

    ("abdominal distention", [
        "abdominal distention", "distended abdomen", "belly distention",
        "abdominal bloat", "bloated stomach", "stomach is distended",
        "belly looks swollen", "abdomen distended", "pot belly",
        "tummy looks bloated", "visibly distended abdomen",
        "extended belly", "abdomen looks big", "protuberant abdomen",
        "belly protrudes",
    ]),

    ("abnormal appearing skin", [
        "abnormal skin appearance", "skin looks abnormal", "strange skin",
        "discolored skin patches", "skin color change", "odd looking skin",
        "skin appears unusual", "skin discoloration", "skin looks weird",
        "blotchy skin", "mottled skin", "skin looks different",
        "changes in skin", "skin changed color", "skin abnormality",
    ]),

    ("abnormal appearing tongue", [
        "tongue looks abnormal", "tongue color change", "strange tongue",
        "tongue looks weird", "tongue discoloration", "unusual tongue",
        "tongue is patchy", "tongue appears odd", "tongue abnormality",
        "weird tongue", "tongue looks different", "tongue changed",
    ]),

    ("abnormal breathing sounds", [
        "abnormal breathing sounds", "breathing noises", "noisy breathing",
        "breathing sounds odd", "crackling breath sounds", "rattling breath",
        "crackles on breathing", "breath sounds abnormal", "chest sounds",
        "stridor", "wheezy breath sounds", "ronchi", "breath crackles",
        "gurgling breath", "breathing sounds like whistling",
    ]),

    ("abnormal involuntary movements", [
        "involuntary movements", "uncontrolled movements", "body moves on its own",
        "limbs move involuntarily", "shaking uncontrollably", "tremors",
        "involuntary shaking", "muscles move by themselves", "twitching",
        "unintentional movement", "jerky movements", "spastic movements",
        "body jerks", "uncontrolled jerking", "dyskinesia",
    ]),

    ("abnormal movement of eyelid", [
        "eyelid twitching", "eyelid movement abnormal", "eye twitch",
        "eyelid spasm", "eye twitching", "eyelid drooping",
        "uncontrolled eyelid movement", "my eye keeps twitching",
        "eyelid flutters", "ptosis", "droopy eyelid",
    ]),

    ("abnormal size or shape of ear", [
        "ear looks abnormal", "ear size abnormal", "misshapen ear",
        "ear deformity", "ear looks different", "unusual ear shape",
        "ear structure abnormal", "malformed ear",
    ]),

    ("absence of menstruation", [
        "absence of menstruation", "missed period", "no period",
        "periods stopped", "amenorrhea", "menstruation stopped",
        "haven't had period", "no monthly cycle", "period missing",
        "skipped period", "period did not come", "lost my period",
        "no menstrual cycle", "menstrual absence", "no periods for months",
        "missed monthly period", "period late", "menstruation absent",
        "no bleeding this month", "cycle stopped",
    ]),

    ("abusing alcohol", [
        "abusing alcohol", "alcohol abuse", "drinking too much",
        "heavy drinking", "excessive alcohol use", "alcoholism",
        "drinking problem", "cannot stop drinking", "dependent on alcohol",
        "alcohol addiction", "binge drinking", "chronic drinker",
    ]),

    ("ache all over", [
        "ache all over", "body ache", "pain all over body",
        "hurts everywhere", "generalized body pain", "my whole body hurts",
        "full body ache", "aching all over", "everything hurts",
        "all over body pain", "diffuse body pain", "body pain everywhere",
        "generalized aching", "widespread pain", "body feels sore all over",
        "systemic ache", "total body ache", "I hurt everywhere",
        "muscles ache all over", "overall body soreness",
    ]),

    ("acne or pimples", [
        "acne", "pimples", "blackheads", "whiteheads", "zits",
        "breakouts", "skin breakout", "facial pimples", "spots on face",
        "blemishes", "comedones", "cystic acne", "skin bumps",
        "skin eruptions", "pimple breakout", "pimple on face",
        "face full of pimples", "pimple on back", "bacne",
        "hormonal acne", "teenage acne",
    ]),

    ("allergic reaction", [
        "allergic reaction", "allergy", "allergic response", "allergy attack",
        "having an allergic reaction", "reacting to something",
        "anaphylaxis", "hypersensitivity", "allergy flare",
        "immune reaction", "allergic to something", "allergy symptoms",
        "reacting badly to food", "hives from allergy",
    ]),

    ("ankle pain", [
        "ankle pain", "ankle hurts", "pain in ankle", "sore ankle",
        "ankle is painful", "painful ankle", "ankle discomfort",
        "ankle ache", "hurting ankle", "my ankle hurts",
        "ankle soreness", "ankle injury pain", "ankle throbbing",
    ]),

    ("ankle stiffness or tightness", [
        "ankle stiffness", "stiff ankle", "ankle tightness",
        "tight ankle", "ankle feels stiff", "ankle mobility reduced",
        "ankle hard to move", "ankle locked up",
    ]),

    ("ankle swelling", [
        "ankle swelling", "swollen ankle", "ankle is swollen",
        "puffy ankle", "ankle edema", "ankles are swollen",
        "my ankles are puffy", "ankle looks swollen",
    ]),

    ("ankle weakness", [
        "ankle weakness", "weak ankle", "ankle gives way",
        "ankle feels weak", "can't support weight on ankle",
        "ankle instability", "wobbly ankle",
    ]),

    ("antisocial behavior", [
        "antisocial behavior", "withdrawing from people", "social withdrawal",
        "avoiding others", "isolating myself", "don't want to be around people",
        "anti social", "staying away from social situations",
        "not wanting to socialize",
    ]),

    ("anxiety and nervousness", [
        "anxiety", "nervous", "anxious", "feeling anxious",
        "nervousness", "worry", "excessive worry", "panic",
        "feeling panicky", "on edge", "stressed out", "tense",
        "feeling tense", "apprehensive", "jittery", "keyed up",
        "restless anxiety", "scared for no reason", "heart racing with anxiety",
        "overthinking", "cannot calm down", "constant worry",
        "generalized anxiety", "nervous all the time",
    ]),

    ("apnea", [
        "apnea", "sleep apnea", "stopping breathing during sleep",
        "breath stops during sleep", "choking during sleep",
        "waking up gasping", "not breathing in sleep",
        "breathing pauses", "obstructive apnea",
    ]),

    # Generic abdominal pain — used as a catch-all mapping; validated against
    # dataset_symptoms at runtime so only maps to real columns when they exist.
    ("abdominal pain", [
        "abdominal pain", "stomach pain", "stomach ache", "tummy ache",
        "belly pain", "stomach hurts", "pain in stomach", "pain in abdomen",
        "gut pain", "belly ache", "ache in stomach", "pain in belly",
        "my stomach hurts", "my tummy hurts", "sore stomach",
        "stomach is sore", "crampy stomach", "stomach discomfort",
    ]),

    ("arm cramps or spasms", [
        "arm cramps", "arm spasms", "arm muscle cramps",
        "muscle cramps in arm", "arm seizing up",
        "arm cramping", "painful arm cramp",
    ]),

    ("arm lump or mass", [
        "lump on arm", "arm lump", "arm mass", "growth on arm",
        "bump on arm", "arm swelling lump", "hard lump on arm",
    ]),

    ("arm pain", [
        "arm pain", "arm hurts", "pain in arm", "sore arm",
        "arm ache", "aching arm", "my arm is hurting",
        "arm discomfort", "arm throbbing", "arm is painful",
    ]),

    ("arm stiffness or tightness", [
        "stiff arm", "arm stiffness", "arm tightness",
        "arm feels tight", "arm is stiff", "arm mobility reduced",
    ]),

    ("arm swelling", [
        "swollen arm", "arm swelling", "arm is swollen",
        "arm edema", "puffy arm",
    ]),

    ("arm weakness", [
        "arm weakness", "weak arm", "arm feels weak",
        "can't lift arm", "arm strength reduced", "my arm is weak",
        "arm giving out", "difficulty lifting arm",
    ]),

    # ── B ──────────────────────────────────────────────────────────────────

    ("back cramps or spasms", [
        "back cramps", "back spasms", "back muscle spasm",
        "muscle spasm in back", "back goes into spasm",
        "back cramp", "back seizing up", "back charley horse",
    ]),

    ("back mass or lump", [
        "lump on back", "back mass", "back lump", "growth on back",
        "bump on back", "hard lump on back",
    ]),

    ("back pain", [
        "back pain", "backache", "back hurts", "my back hurts",
        "sore back", "pain in back", "back ache",
        "aching back", "back discomfort", "back is painful",
        "back throbbing", "spine pain", "spinal pain",
        "dull back pain", "sharp back pain", "back stiffness",
        "upper back pain", "mid back pain",
    ]),

    ("back stiffness or tightness", [
        "stiff back", "back stiffness", "back tightness",
        "back feels tight", "back is stiff", "tight back muscles",
        "back hard to move", "can't straighten back",
    ]),

    ("back swelling", [
        "swollen back", "back swelling", "swelling on back",
        "back looks swollen",
    ]),

    ("back weakness", [
        "back weakness", "weak back", "back feels weak",
        "back muscles are weak", "can't hold back straight",
    ]),

    ("bedwetting", [
        "bedwetting", "wetting the bed", "nocturnal enuresis",
        "wetting bed at night", "urinating in sleep",
        "child wetting bed", "nighttime accidents",
    ]),

    ("bladder mass", [
        "bladder mass", "bladder lump", "mass in bladder",
        "growth in bladder", "bladder tumor symptoms",
    ]),

    ("bleeding from ear", [
        "bleeding from ear", "ear bleeding", "blood from ear",
        "blood coming out of ear", "blood in ear canal",
    ]),

    ("bleeding from eye", [
        "bleeding from eye", "eye bleeding", "blood from eye",
        "blood in eye", "eye hemorrhage",
    ]),

    ("bleeding gums", [
        "bleeding gums", "gums bleeding", "my gums bleed",
        "blood when brushing teeth", "gum bleeding",
        "gums bleed when I brush", "bleeding from gums",
    ]),

    ("bleeding in mouth", [
        "bleeding in mouth", "mouth bleeding", "blood in mouth",
        "blood inside mouth", "oral bleeding",
    ]),

    ("bleeding or discharge from nipple", [
        "nipple discharge", "blood from nipple", "nipple bleeding",
        "discharge from breast", "breast discharge",
        "fluid from nipple", "milky nipple discharge",
    ]),

    ("blindness", [
        "blindness", "cannot see", "lost vision", "vision loss",
        "went blind", "sudden blindness", "complete vision loss",
        "no sight", "total loss of vision",
    ]),

    ("blood clots during menstrual periods", [
        "blood clots during period", "clots in period blood",
        "passing clots during menstruation", "menstrual clots",
        "period blood clots", "clots when on period",
    ]),

    ("blood in stool", [
        "blood in stool", "blood in poop", "bloody stool",
        "rectal blood", "blood when I poop", "blood in feces",
        "red blood in stool", "stool has blood",
        "dark blood in stool", "bright red blood in poop",
    ]),

    ("blood in urine", [
        "blood in urine", "blood in pee", "bloody urine",
        "pink urine", "red urine", "hematuria",
        "urine has blood", "blood when urinating",
        "blood in my pee", "pee is pink or red",
    ]),

    ("bones are painful", [
        "bone pain", "bones hurt", "painful bones",
        "bone ache", "deep bone pain", "bone tenderness",
        "bones are sore", "my bones hurt", "bone soreness",
    ]),

    ("bowlegged or knock-kneed", [
        "bowlegged", "knock-kneed", "bow legs",
        "legs curve outward", "legs curve inward", "genu varum", "genu valgum",
    ]),

    ("breathing fast", [
        "breathing fast", "fast breathing", "rapid breathing",
        "tachypnea", "hyperventilation", "breathing quickly",
        "breath is rapid", "can't slow down breathing",
        "panting", "huffing", "breathing too quickly",
        "rapid respiration", "quick breaths",
    ]),

    ("bumps on penis", [
        "bumps on penis", "penile bumps", "spots on penis",
        "pimples on penis", "growth on penis", "lesions on penis",
    ]),

    ("burning abdominal pain", [
        "burning abdominal pain", "burning stomach pain",
        "burning sensation in stomach", "stomach burns",
        "burning belly pain", "acid burning in stomach",
        "stomach on fire", "burning in abdomen",
    ]),

    ("burning chest pain", [
        "burning chest pain", "chest burns", "burning in chest",
        "burning sensation in chest", "heartburn",
        "chest on fire", "acid reflux burning", "burning behind sternum",
        "esophageal burning", "burning feeling in chest",
    ]),

    # ── C ──────────────────────────────────────────────────────────────────

    ("change in skin mole size or color", [
        "mole changing", "mole got bigger", "mole changed color",
        "skin mole changed", "mole is different", "mole looks abnormal",
        "mole growth", "mole darkened", "mole irregular",
    ]),

    ("changes in stool appearance", [
        "stool color change", "poop looks different", "unusual stool",
        "stool appearance change", "abnormal stool",
        "stool changed", "unusual bowel movement", "abnormal poop",
        "black stools", "clay colored stool", "pale stool",
    ]),

    ("chest tightness", [
        "chest tightness", "tight chest", "chest feels tight",
        "pressure in chest", "chest pressure", "chest squeezing",
        "heaviness in chest", "chest feels heavy",
        "band around chest", "chest constriction",
        "tightness in chest", "chest feels like it is squeezed",
        "pressure on chest", "weighted chest",
        "crushing feeling in chest", "chest feels compressed",
        "something pressing on chest",
    ]),

    ("chills", [
        "chills", "feeling cold suddenly", "shivering",
        "cold shivers", "rigors", "shaking with cold",
        "teeth chattering", "body shivering", "cold chills",
        "shaking uncontrollably from cold", "chilling feeling",
        "getting the chills", "feeling chilly and shivering",
        "uncontrollable shivering", "ice cold feeling",
    ]),

    ("cloudy eye", [
        "cloudy eye", "cloudy vision", "foggy eye",
        "eye looks cloudy", "blurry eye appearance",
        "milky eye", "eye cloudiness", "cataract symptom",
    ]),

    ("congestion in chest", [
        "chest congestion", "congestion in chest", "chest feels congested",
        "phlegm in chest", "mucus in chest", "chest full of phlegm",
        "rattling in chest", "chest is congested",
        "chest crackle", "gunk in chest",
    ]),

    ("constipation", [
        "constipation", "can't poop", "haven't had bowel movement",
        "hard to pass stool", "difficulty pooping",
        "bowel movement blocked", "no bowel movement",
        "straining to poop", "no stool for days",
        "not able to poop", "infrequent stools",
        "hard stool", "unable to defecate", "blocked bowels",
        "stool is hard and dry", "trapped stool",
        "bowel irregularity", "irregular bowel", "infrequent bowel",
    ]),

    ("coryza", [
        "coryza", "runny nose", "nasal discharge",
        "nose running", "snot running from nose",
        "clear nasal discharge", "nasal drip", "running nose",
        "nose is dripping", "nose dripping", "rhinorrhea",
        "watery nasal discharge",
    ]),

    ("cough", [
        "cough", "coughing", "persistent cough", "dry cough",
        "wet cough", "hacking cough", "coughing a lot",
        "constant cough", "cough won't stop", "chesty cough",
        "deep cough", "productive cough", "I keep coughing",
        "coughing up stuff", "cough and cold", "barking cough",
        "whooping cough feeling", "continuous coughing",
        "tickling cough", "irritating cough",
    ]),

    ("coughing up sputum", [
        "coughing up sputum", "coughing up mucus", "coughing up phlegm",
        "phlegm when coughing", "mucus with cough",
        "productive cough with phlegm", "bringing up phlegm",
        "hacking up mucus", "coughing up green stuff",
        "coughing out thick mucus",
    ]),

    ("cramps and spasms", [
        "cramps", "muscle cramps", "muscle spasms", "spasms",
        "muscle cramping", "painful cramps", "muscles seizing",
        "cramp", "body cramps", "general cramps and spasms",
    ]),

    ("cross-eyed", [
        "cross-eyed", "strabismus", "eyes going in different directions",
        "squinting", "eyes not aligned", "eye misalignment",
        "lazy eye", "eyes cross", "eyes don't look same direction",
    ]),

    # ── D ──────────────────────────────────────────────────────────────────

    ("decreased appetite", [
        "decreased appetite", "not hungry", "loss of appetite",
        "not feeling like eating", "no desire to eat",
        "don't want to eat", "poor appetite", "food not appealing",
        "appetite loss", "reduced appetite", "not eating much",
        "can't eat", "skipping meals", "food tastes bland",
        "no interest in food", "anorexia", "not wanting to eat",
        "appetite gone", "eating less", "barely eating",
    ]),

    ("decreased heart rate", [
        "decreased heart rate", "slow heart rate", "low heart rate",
        "bradycardia", "slow pulse", "pulse is slow",
        "heart beating slowly", "low pulse rate",
    ]),

    ("delusions or hallucinations", [
        "delusions", "hallucinations", "seeing things",
        "hearing things", "hallucinating", "believing false things",
        "paranoid delusions", "psychosis", "psychotic episode",
        "seeing visions", "hearing voices", "visual hallucinations",
        "auditory hallucinations", "loss of reality",
    ]),

    ("depression", [
        "depression", "feeling depressed", "sad all the time",
        "depressed mood", "low mood", "feeling down",
        "hopelessness", "feeling hopeless", "feeling worthless",
        "persistent sadness", "clinical depression",
        "can't enjoy anything", "empty feeling", "no motivation",
        "despair", "feeling blue", "emotionally numb",
        "dark thoughts", "no joy in life",
    ]),

    ("depressive or psychotic symptoms", [
        "depressive symptoms", "psychotic symptoms",
        "depression and psychosis", "mental health crisis",
        "depressive psychosis",
    ]),

    ("diaper rash", [
        "diaper rash", "nappy rash", "rash from diaper",
        "baby diaper rash", "redness from diaper", "rash in diaper area",
    ]),

    ("diarrhea", [
        "diarrhea", "loose stools", "watery stools",
        "loose bowels", "runny poop", "frequent loose stool",
        "liquid stools", "can't control bowels",
        "upset stomach diarrhea", "stomach flu diarrhea",
        "bowel looseness", "frequent watery stools",
        "runny stool", "gut runs", "the runs",
        "traveler's diarrhea", "diarrhoea",
    ]),

    ("difficulty breathing", [
        "difficulty breathing", "breathlessness", "can't breathe",
        "breathing difficulty", "trouble breathing",
        "hard to breathe", "breathing problems",
        "out of breath", "labored breathing", "struggling to breathe",
        "shortness of breath", "dyspnea", "breathing is hard",
        "cannot get enough air", "gasping for breath",
        "suffocating feeling", "air hunger",
        "feeling suffocated", "breathing issues",
        "breathing hurts", "winded",
    ]),

    ("difficulty eating", [
        "difficulty eating", "trouble eating", "hard to eat",
        "can't eat properly", "eating problems",
        "pain when eating", "eating is difficult",
    ]),

    ("difficulty in swallowing", [
        "difficulty swallowing", "trouble swallowing",
        "hard to swallow", "pain when swallowing",
        "dysphagia", "food gets stuck", "can't swallow properly",
        "something stuck in throat", "swallowing is painful",
        "choking when eating", "food won't go down",
    ]),

    ("difficulty speaking", [
        "difficulty speaking", "trouble speaking",
        "hard to speak", "speech problems", "slurred speech",
        "can't speak properly", "speech is difficult",
        "words won't come out", "struggling to speak",
        "communication problems", "speech impaired",
    ]),

    ("diminished hearing", [
        "diminished hearing", "hearing loss", "can't hear well",
        "hearing impaired", "deaf", "partial deafness",
        "reduced hearing", "hard of hearing",
        "hearing is going", "hearing reduced", "sound muffled",
        "muffled hearing",
    ]),

    ("diminished vision", [
        "diminished vision", "reduced vision", "poor eyesight",
        "vision loss", "blurry vision", "can't see clearly",
        "eyesight getting worse", "vision impaired",
        "eyes getting weaker", "vision deteriorating",
    ]),

    ("discharge in stools", [
        "discharge in stools", "mucus in stool", "slimy stool",
        "mucous in poop", "jelly like stool",
    ]),

    ("disturbance of memory", [
        "memory loss", "forgetfulness", "can't remember things",
        "memory problems", "poor memory", "forgetting things",
        "short term memory loss", "memory impairment",
        "dementia symptoms", "cognitive decline",
        "trouble remembering", "memory disturbance",
    ]),

    ("disturbance of smell or taste", [
        "loss of smell", "loss of taste", "can't smell",
        "can't taste food", "food tastes different",
        "smell is gone", "taste is gone", "anosmia",
        "ageusia", "smell reduced", "parosmia",
        "things smell weird", "food tastes bland",
        "altered smell", "altered taste",
    ]),

    ("dizziness", [
        "dizziness", "dizzy", "feeling dizzy",
        "light headed", "lightheaded", "vertigo",
        "room is spinning", "spinning sensation",
        "woozy", "wobbly", "off balance",
        "unsteady", "head is spinning", "feeling faint",
        "nearly fainting", "giddy", "giddiness",
        "swimming feeling in head", "head rush",
    ]),

    ("double vision", [
        "double vision", "seeing double", "diplopia",
        "two images", "blurred double vision", "ghost images",
    ]),

    ("drainage in throat", [
        "drainage in throat", "postnasal drip", "mucus dripping down throat",
        "throat drainage", "mucus in throat", "phlegm draining into throat",
        "back of throat dripping", "sinus drainage",
    ]),

    ("drug abuse", [
        "drug abuse", "drug addiction", "substance abuse",
        "using drugs", "addicted to drugs", "drug dependence",
        "narcotics abuse",
    ]),

    ("dry lips", [
        "dry lips", "chapped lips", "cracked lips",
        "lips are dry", "parched lips", "lips peeling",
        "dehydrated lips",
    ]),

    ("dry or flaky scalp", [
        "dry scalp", "flaky scalp", "dandruff",
        "scalp flaking", "scaly scalp", "scalp is dry",
        "itchy dry scalp", "scalp peeling",
    ]),

    # ── E ──────────────────────────────────────────────────────────────────

    ("ear pain", [
        "ear pain", "earache", "pain in ear",
        "sore ear", "ear hurts", "my ear hurts",
        "ear is painful", "throbbing ear", "ear ache",
        "sharp ear pain", "deep ear pain",
    ]),

    ("early or late onset of menopause", [
        "early menopause", "late menopause", "premature menopause",
        "perimenopause", "menopause symptoms",
    ]),

    ("elbow cramps or spasms", [
        "elbow cramps", "elbow spasm", "elbow muscle cramp",
    ]),

    ("elbow lump or mass", [
        "elbow lump", "lump on elbow", "elbow mass", "bump on elbow",
    ]),

    ("elbow pain", [
        "elbow pain", "elbow hurts", "pain in elbow",
        "sore elbow", "elbow ache", "elbow discomfort",
        "tennis elbow", "golfer's elbow", "my elbow hurts",
    ]),

    ("elbow stiffness or tightness", [
        "stiff elbow", "elbow stiffness", "elbow tightness",
        "elbow won't bend", "elbow locked",
    ]),

    ("elbow swelling", [
        "swollen elbow", "elbow swelling", "elbow is swollen",
        "puffy elbow", "elbow edema",
    ]),

    ("elbow weakness", [
        "weak elbow", "elbow weakness", "elbow gives out",
    ]),

    ("emotional symptoms", [
        "emotional problems", "emotional instability",
        "mood problems", "emotional distress",
        "feeling emotional", "emotionally unstable",
    ]),

    ("excessive anger", [
        "excessive anger", "anger issues", "uncontrollable anger",
        "rage", "violent anger", "getting angry easily",
        "hot-tempered", "losing temper easily", "irritable rage",
        "explosive anger", "angry outbursts",
    ]),

    ("excessive appetite", [
        "excessive appetite", "overeating", "always hungry",
        "can't stop eating", "insatiable appetite",
        "extreme hunger", "polyphagia", "constant hunger",
        "binge eating", "eating too much",
    ]),

    ("excessive growth", [
        "excessive growth", "abnormal growth", "overgrowth",
        "growing too fast", "gigantism symptoms",
    ]),

    ("excessive urination at night", [
        "excessive urination at night", "nocturia", "waking to urinate",
        "peeing at night", "urinating frequently at night",
        "getting up multiple times to pee",
    ]),

    ("eye burns or stings", [
        "eye burns", "burning eye", "stinging eye",
        "eye is burning", "eye stings", "eyes are burning",
        "eye burning sensation",
    ]),

    ("eye deviation", [
        "eye deviation", "eye turned", "eye looking sideways",
        "eye not straight", "deviated eye",
    ]),

    ("eye moves abnormally", [
        "eye moves abnormally", "abnormal eye movement",
        "nystagmus", "eye shaking", "eye flickering",
        "eye movement disorder",
    ]),

    ("eye redness", [
        "eye redness", "red eyes", "bloodshot eyes",
        "eyes are red", "pink eye", "conjunctivitis",
        "red eye", "eye is red", "inflamed eye",
        "eyes look red", "sclera is red",
    ]),

    ("eye strain", [
        "eye strain", "eyes tired", "eye fatigue",
        "tired eyes", "eyes hurt from screen",
        "eyestrain", "eyes ache", "eyes feel strained",
    ]),

    ("eyelid lesion or rash", [
        "eyelid lesion", "rash on eyelid", "eyelid rash",
        "spot on eyelid", "blister on eyelid",
    ]),

    ("eyelid retracted", [
        "eyelid retracted", "eyelid pulled back",
        "eyelid not closing properly", "exophthalmos related eyelid",
    ]),

    ("eyelid swelling", [
        "swollen eyelid", "eyelid swelling", "puffy eyelid",
        "eyelid is swollen", "swollen eye lid", "puffy eye",
    ]),

    # ── F ──────────────────────────────────────────────────────────────────

    ("facial pain", [
        "facial pain", "face pain", "pain in face",
        "face hurts", "cheek pain", "jaw pain facial",
        "face is painful", "facial ache",
        "pain in my face", "sore face",
    ]),

    ("fainting", [
        "fainting", "fainted", "blacking out",
        "passed out", "syncope", "loss of consciousness",
        "falling unconscious", "going limp and falling",
        "near fainting", "almost fainted",
        "collapse", "feeling like I will faint",
    ]),

    ("fatigue", [
        "fatigue", "tiredness", "tired all the time",
        "exhaustion", "exhausted", "no energy",
        "feeling drained", "low energy", "constantly tired",
        "chronic fatigue", "worn out", "run down",
        "always sleepy", "lethargic", "lethargy",
        "weakness from tiredness", "can't get out of bed",
        "energy drained", "total exhaustion", "burnout",
        "physically drained", "mental fatigue",
    ]),

    ("fears and phobias", [
        "fears", "phobia", "irrational fear",
        "anxiety from fear", "excessive fear", "panic from fear",
        "phobic reaction",
    ]),

    ("feeling cold", [
        "feeling cold", "always cold", "cold all the time",
        "feels cold", "chilly feeling", "cold sensation",
        "body feels cold", "cold hands and feet",
        "chills without fever", "constantly cold",
    ]),

    ("feeling hot", [
        "feeling hot", "body feels hot", "hot all the time",
        "overheated", "burning up", "feverish feeling",
        "warm all over", "heat sensation",
    ]),

    ("feeling hot and cold", [
        "feeling hot and cold", "alternating hot and cold",
        "hot then cold", "temperature swings",
        "chills and sweats", "sweating and shivering",
    ]),

    ("feeling ill", [
        "feeling ill", "feeling sick", "not well",
        "unwell", "malaise", "generally unwell",
        "feeling off", "feel terrible", "feeling bad",
        "under the weather", "feeling awful",
        "not feeling myself", "feeling grotty",
        "general feeling of illness",
    ]),

    ("fever", [
        "fever", "high temperature", "temperature",
        "burning up", "running a fever", "feverish",
        "body is hot", "hot body", "high fever",
        "low grade fever", "slight fever",
        "pyrexia", "elevated temperature", "febrile",
        "body feels warm", "feeling feverish",
        "thermometer high reading", "temperature raised",
        "had a temperature", "my temperature is high",
    ]),

    ("flatulence", [
        "flatulence", "gas", "farting", "excessive gas",
        "bloating and gas", "passing gas", "bloated with gas",
        "flatulency", "intestinal gas", "gassy",
        "abdominal gas", "stomach gas",
    ]),

    ("flu-like syndrome", [
        "flu-like symptoms", "flu symptoms", "flu syndrome",
        "like having flu", "influenza-like", "flu feeling",
        "feel like I have flu", "body aches and fever",
        "flu-like illness",
    ]),

    ("fluid in ear", [
        "fluid in ear", "water in ear", "ear fluid",
        "blocked ear from fluid", "ear feels blocked with fluid",
    ]),

    ("fluid retention", [
        "fluid retention", "water retention", "edema",
        "retaining fluid", "swelling from fluid",
        "excess fluid in body", "fluid build up",
    ]),

    ("flushing", [
        "flushing", "face flushing", "face turns red",
        "sudden facial redness", "hot flush",
        "skin flushing", "redness and warmth in face",
        "hot face", "flushed cheeks",
    ]),

    ("focal weakness", [
        "focal weakness", "weakness in one area",
        "weakness on one side", "localized weakness",
        "one limb weak",
    ]),

    ("foot or toe cramps or spasms", [
        "foot cramps", "toe cramps", "foot spasm",
        "toe spasm", "foot muscle cramp",
        "cramp in foot", "curled toes from cramp",
    ]),

    ("foot or toe lump or mass", [
        "lump on foot", "foot lump", "toe lump",
        "growth on foot", "bump on foot",
    ]),

    ("foot or toe pain", [
        "foot pain", "toe pain", "pain in foot",
        "pain in toe", "sore foot", "sore toe",
        "foot hurts", "toe hurts", "foot ache",
    ]),

    ("foot or toe stiffness or tightness", [
        "stiff foot", "stiff toes", "foot stiffness",
        "toe stiffness", "foot tightness",
    ]),

    ("foot or toe swelling", [
        "swollen foot", "swollen toes", "foot swelling",
        "toe swelling", "puffy feet",
    ]),

    ("foot or toe weakness", [
        "foot weakness", "toe weakness", "weak foot",
        "can't move toes", "foot drop",
    ]),

    ("foreign body sensation in eye", [
        "something in eye", "eye feels like something is in it",
        "gritty eye", "foreign body in eye",
        "sand in eye feeling", "eye irritation like foreign body",
    ]),

    ("frequent menstruation", [
        "frequent periods", "period coming too often",
        "menstruation too frequent", "periods every 2-3 weeks",
        "polymenorrhea",
    ]),

    ("frequent urination", [
        "frequent urination", "urinating frequently",
        "peeing a lot", "urinary frequency",
        "going to bathroom often", "constant urge to urinate",
        "urge to pee all the time", "too many bathroom trips",
        "excessive urination", "polyuria",
        "peeing every hour", "frequent need to pee",
    ]),

    ("frontal headache", [
        "frontal headache", "forehead headache",
        "pain in forehead", "pain in front of head",
        "headache at front", "forehead pain",
    ]),

    # ── G ──────────────────────────────────────────────────────────────────

    ("groin mass", [
        "groin mass", "lump in groin", "groin lump",
        "growth in groin area",
    ]),

    ("groin pain", [
        "groin pain", "pain in groin", "groin hurts",
        "inner thigh pain", "inguinal pain",
    ]),

    ("gum pain", [
        "gum pain", "gums hurt", "painful gums",
        "gum ache", "gum soreness",
    ]),

    # ── H ──────────────────────────────────────────────────────────────────

    ("hand or finger cramps or spasms", [
        "hand cramps", "finger cramps", "hand spasm",
        "finger spasm", "hand seizing up", "hand cramping",
    ]),

    ("hand or finger lump or mass", [
        "lump on hand", "finger lump", "hand mass",
        "growth on finger", "bump on hand",
    ]),

    ("hand or finger pain", [
        "hand pain", "finger pain", "pain in hand",
        "pain in finger", "sore hand", "sore fingers",
        "hand hurts", "fingers hurt",
    ]),

    ("hand or finger stiffness or tightness", [
        "stiff hands", "stiff fingers", "hand stiffness",
        "finger stiffness", "hands are tight",
        "can't open hand", "fingers won't bend",
    ]),

    ("hand or finger swelling", [
        "swollen hand", "swollen fingers", "hand swelling",
        "puffy fingers", "finger edema",
    ]),

    ("hand or finger weakness", [
        "weak hands", "weak fingers", "hand weakness",
        "finger weakness", "can't grip", "grip is weak",
    ]),

    ("headache", [
        "headache", "head hurts", "head pain",
        "migraine", "splitting headache", "pounding headache",
        "throbbing headache", "pressure in head",
        "my head is killing me", "head is pounding",
        "tension headache", "dull headache",
        "head is throbbing", "head discomfort",
        "head ache", "cephalalgia", "head pressure",
        "cranial pain", "pain in my head",
        "bad headache", "headaches every day",
    ]),

    ("heartburn", [
        "heartburn", "acid reflux", "indigestion",
        "burning in chest after eating", "stomach acid rising",
        "acid coming up", "reflux", "gastric reflux",
        "sour stomach", "gerd symptoms",
        "burning after eating", "heart burn",
        "acid in throat", "sour taste from acid",
    ]),

    ("heavy menstrual flow", [
        "heavy period", "heavy menstrual flow", "heavy bleeding during period",
        "menorrhagia", "soaking through pads", "excessive period bleeding",
        "flooding during period", "very heavy period",
    ]),

    ("hemoptysis", [
        "coughing up blood", "blood when coughing", "hemoptysis",
        "blood in sputum", "blood from lungs", "bloody cough",
    ]),

    ("hesitancy", [
        "hesitancy", "urinary hesitancy", "difficulty starting urination",
        "can't start urinating", "weak urine stream",
        "straining to urinate",
    ]),

    ("hip lump or mass", [
        "hip lump", "lump on hip", "hip mass", "growth on hip",
    ]),

    ("hip pain", [
        "hip pain", "hip hurts", "pain in hip",
        "sore hip", "hip ache", "hip is painful",
    ]),

    ("hip stiffness or tightness", [
        "stiff hip", "hip stiffness", "hip tightness",
        "hip won't move", "tight hip",
    ]),

    ("hip swelling", [
        "swollen hip", "hip swelling", "hip is swollen",
    ]),

    ("hip weakness", [
        "hip weakness", "weak hip", "hip gives out",
    ]),

    ("hoarse voice", [
        "hoarse voice", "hoarseness", "raspy voice",
        "voice is hoarse", "croaky voice", "gravelly voice",
        "voice sounds hoarse", "voice went hoarse",
        "my voice is raspy", "losing voice",
    ]),

    ("hostile behavior", [
        "hostile behavior", "aggression", "aggressive behavior",
        "acting hostile", "being aggressive",
    ]),

    ("hot flashes", [
        "hot flashes", "hot flush", "sudden heat wave",
        "feeling very hot suddenly", "sweating and hot flash",
        "menopausal hot flash", "hot wave",
    ]),

    ("hurts to breath", [
        "hurts to breathe", "pain when breathing", "breathing is painful",
        "chest pain on breathing", "pleuritic pain",
        "sharp pain with breath", "painful breathing",
        "breathing causes pain",
    ]),

    # ── I ──────────────────────────────────────────────────────────────────

    ("impotence", [
        "impotence", "erectile dysfunction", "can't get erection",
        "ed", "inability to maintain erection", "sexual dysfunction",
        "not able to perform sexually",
    ]),

    ("incontinence of stool", [
        "incontinence of stool", "stool incontinence", "fecal incontinence",
        "unable to control bowels", "bowel accidents",
        "leaking stool", "cannot hold stool",
    ]),

    ("increased heart rate", [
        "increased heart rate", "fast heart rate", "rapid heart rate",
        "tachycardia", "racing heart", "heart racing",
        "palpitations fast", "heart beating fast",
        "heart is pounding fast", "rapid pulse",
    ]),

    ("infant feeding problem", [
        "infant feeding problem", "baby won't feed", "baby not eating",
        "breastfeeding problem", "feeding difficulty in baby",
        "baby refuses milk",
    ]),

    ("infant spitting up", [
        "baby spitting up", "infant reflux", "spitting up milk",
        "baby keeps vomiting", "baby regurgitating",
        "newborn spitting up",
    ]),

    ("infertility", [
        "infertility", "can't get pregnant", "not getting pregnant",
        "trying to conceive", "fertility problems",
        "difficulty conceiving", "inability to have children",
    ]),

    ("infrequent menstruation", [
        "infrequent periods", "irregular periods",
        "oligomenorrhea", "periods come rarely",
        "long gap between periods",
    ]),

    ("insomnia", [
        "insomnia", "can't sleep", "unable to sleep",
        "sleeping problems", "sleep problems", "trouble sleeping",
        "waking up in middle of night", "difficulty falling asleep",
        "staying awake all night", "poor sleep",
        "restless sleep", "sleep disorder",
        "sleep disturbance", "not getting enough sleep",
        "lying awake all night",
    ]),

    ("intermenstrual bleeding", [
        "intermenstrual bleeding", "bleeding between periods",
        "spotting between periods", "mid cycle bleeding",
    ]),

    ("involuntary urination", [
        "involuntary urination", "bladder leakage", "urinary incontinence",
        "leaking urine", "wetting yourself", "cannot hold urine",
        "bladder control problem", "urinary leakage",
    ]),

    ("irregular appearing nails", [
        "nail abnormality", "nails look abnormal", "irregular nails",
        "nail changes", "ridged nails", "brittle nails",
        "nails breaking", "discolored nails",
    ]),

    ("irregular appearing scalp", [
        "scalp abnormality", "irregular scalp", "scalp changes",
        "unusual scalp", "scalp lesions",
    ]),

    ("irregular belly button", [
        "belly button abnormal", "irregular navel", "navel problem",
        "protruding belly button",
    ]),

    ("irregular heartbeat", [
        "irregular heartbeat", "arrhythmia", "heart palpitations",
        "heart skipping beats", "heart fluttering",
        "uneven heartbeat", "heartbeat irregular",
        "heart rhythm problem", "skipped heartbeat",
        "palpitations and irregular beat",
    ]),

    ("irritable infant", [
        "irritable infant", "fussy baby", "baby won't stop crying",
        "colicky baby", "baby extremely irritable",
        "baby in distress",
    ]),

    ("itchiness of eye", [
        "itchy eye", "eye itching", "eyes are itchy",
        "itchy eyes", "eye pruritus",
        "want to rub my eyes", "eyes itch",
    ]),

    ("itching of scrotum", [
        "scrotal itching", "itchy scrotum", "scrotum itches",
    ]),

    ("itching of skin", [
        "skin itching", "itchy skin", "skin itch",
        "pruritus", "generalized itching",
        "itchy all over", "itchy body",
        "skin is itchy", "scratching skin",
    ]),

    ("itching of the anus", [
        "anal itching", "itchy anus", "rectal itching",
        "pruritus ani", "anal pruritus",
    ]),

    ("itchy ear(s)", [
        "itchy ears", "itchy ear", "ear itching",
        "ear itch", "ears itch",
    ]),

    ("itchy eyelid", [
        "itchy eyelid", "eyelid itching", "eyelid itch",
    ]),

    ("itchy scalp", [
        "itchy scalp", "scalp itching", "scalp itch",
        "head is itchy", "dandruff itch",
    ]),

    # ── J ──────────────────────────────────────────────────────────────────

    ("jaundice", [
        "jaundice", "yellow skin", "yellowing of skin",
        "yellow eyes", "skin is yellow", "yellowing of eyes",
        "yellow tinge", "jaundiced", "icterus",
        "yellow complexion", "bile buildup",
    ]),

    ("jaw pain", [
        "jaw pain", "pain in jaw", "jaw hurts",
        "jaw ache", "painful jaw", "jaw discomfort",
        "sore jaw", "temporomandibular pain", "TMJ pain",
        "jaw clicking and pain", "jaw throbbing",
    ]),

    ("jaw swelling", [
        "jaw swelling", "swollen jaw", "jaw is swollen",
        "swelling around jaw",
    ]),

    ("joint pain", [
        "joint pain", "joint ache", "pain in joints",
        "aching joints", "arthralgia",
        "joints are painful", "joints hurt",
        "joint discomfort", "sore joints",
        "painful joints", "pain in multiple joints",
    ]),

    ("joint stiffness or tightness", [
        "stiff joints", "joint stiffness", "joint tightness",
        "joints are stiff", "joints won't move well",
        "morning stiffness in joints",
    ]),

    ("joint swelling", [
        "swollen joints", "joint swelling", "joints are swollen",
        "puffy joints", "joint edema", "inflamed joints",
    ]),

    # ── K ──────────────────────────────────────────────────────────────────

    ("kidney mass", [
        "kidney mass", "mass in kidney", "kidney lump",
        "growth in kidney",
    ]),

    ("knee cramps or spasms", [
        "knee cramps", "knee spasm", "cramp in knee",
    ]),

    ("knee lump or mass", [
        "knee lump", "lump on knee", "knee mass",
        "growth on knee", "bump on knee",
    ]),

    ("knee pain", [
        "knee pain", "knee hurts", "pain in knee",
        "sore knee", "knee ache", "knee is painful",
        "my knee hurts", "knee discomfort",
        "patella pain", "kneecap pain",
    ]),

    ("knee stiffness or tightness", [
        "stiff knee", "knee stiffness", "knee tightness",
        "knee won't bend", "tight knee",
    ]),

    ("knee swelling", [
        "swollen knee", "knee swelling", "knee is swollen",
        "puffy knee", "fluid in knee",
    ]),

    ("knee weakness", [
        "knee weakness", "weak knee", "knee gives out",
        "knee buckling", "knee instability",
    ]),

    # ── L ──────────────────────────────────────────────────────────────────

    ("lack of growth", [
        "lack of growth", "not growing", "growth failure",
        "stunted growth", "growth retardation",
    ]),

    ("lacrimation", [
        "lacrimation", "watery eyes", "eyes watering",
        "excessive tearing", "tears flowing",
        "tears rolling down", "eyes are teary",
    ]),

    ("leg cramps or spasms", [
        "leg cramps", "leg spasm", "muscle cramp in leg",
        "leg charley horse", "calf cramp", "leg seizing up",
        "cramp in leg", "nighttime leg cramps",
    ]),

    ("leg lump or mass", [
        "lump on leg", "leg mass", "growth on leg",
        "bump on leg",
    ]),

    ("leg pain", [
        "leg pain", "leg hurts", "pain in leg",
        "sore leg", "leg ache", "aching legs",
        "my legs hurt", "leg discomfort",
        "calf pain", "thigh pain",
    ]),

    ("leg stiffness or tightness", [
        "stiff legs", "leg stiffness", "leg tightness",
        "tight legs", "leg muscles tight",
    ]),

    ("leg swelling", [
        "swollen legs", "leg swelling", "legs are swollen",
        "puffy legs", "leg edema",
    ]),

    ("leg weakness", [
        "leg weakness", "weak legs", "legs feel weak",
        "can't stand on legs", "legs giving out",
        "difficulty walking due to weakness",
    ]),

    ("lip sore", [
        "lip sore", "sore on lip", "lip ulcer",
        "cold sore on lip", "blister on lip",
    ]),

    ("lip swelling", [
        "swollen lip", "lip swelling", "lip is swollen",
        "puffy lip",
    ]),

    ("long menstrual periods", [
        "long periods", "prolonged menstruation",
        "period lasts too long", "periods lasting more than a week",
    ]),

    ("loss of sensation", [
        "loss of sensation", "numbness", "feeling numb",
        "can't feel", "reduced sensation",
        "numbness in limbs", "tingling and numbness",
        "area feels numb", "no feeling",
    ]),

    ("loss of sex drive", [
        "loss of sex drive", "low libido", "no sexual desire",
        "not interested in sex", "reduced libido",
        "decreased sex drive",
    ]),

    ("low back cramps or spasms", [
        "lower back cramps", "lower back spasm",
        "lumbar spasm", "back goes out",
        "low back goes into spasm",
    ]),

    ("low back pain", [
        "low back pain", "lower back pain", "lumbar pain",
        "my lower back hurts", "pain in lower back",
        "lumbago", "lower back ache",
        "lower back is killing me", "sore lower back",
    ]),

    ("low back stiffness or tightness", [
        "stiff lower back", "lower back stiffness",
        "lower back tightness", "lumbar stiffness",
        "lower back feels tight",
    ]),

    ("low back swelling", [
        "lower back swelling", "swollen lower back",
    ]),

    ("low back weakness", [
        "lower back weakness", "weak lower back",
    ]),

    ("low self-esteem", [
        "low self esteem", "feeling worthless",
        "poor self image", "low confidence",
        "feeling inadequate", "no self worth",
    ]),

    ("low urine output", [
        "low urine output", "dark urine", "little urine",
        "not urinating much", "oliguria",
        "urine output reduced", "barely peeing",
    ]),

    ("lower abdominal pain", [
        "lower abdominal pain", "lower stomach pain",
        "lower belly pain", "pelvic pain",
        "pain in lower abdomen", "lower tummy pain",
        "suprapubic pain", "lower gut pain",
    ]),

    ("lower body pain", [
        "lower body pain", "pain in lower body",
        "pain below waist", "lower extremity pain",
    ]),

    ("lump in throat", [
        "lump in throat", "sensation of lump in throat",
        "globus sensation", "something stuck in throat",
        "throat feels blocked", "can't swallow properly lump",
        "throat tightness lump",
    ]),

    ("lump or mass of breast", [
        "breast lump", "lump in breast", "breast mass",
        "breast lump found", "hard lump in breast",
        "breast swelling lump",
    ]),

    ("lump over jaw", [
        "jaw lump", "lump over jaw", "lump near jaw",
    ]),

    ("lymphedema", [
        "lymphedema", "lymph swelling", "swollen lymph channels",
        "leg swelling from lymphedema", "arm swelling from lymphedema",
    ]),

    # ── M ──────────────────────────────────────────────────────────────────

    ("mass in scrotum", [
        "scrotal mass", "lump in scrotum", "mass in scrotum",
        "testicular lump",
    ]),

    ("mass on ear", [
        "mass on ear", "ear lump", "lump on ear",
    ]),

    ("mass on eyelid", [
        "eyelid mass", "lump on eyelid", "mass on eyelid",
        "chalazion", "stye",
    ]),

    ("mass on vulva", [
        "vulvar mass", "lump on vulva", "mass on vulva",
    ]),

    ("mass or swelling around the anus", [
        "anal mass", "swelling around anus", "perianal mass",
        "lump near anus", "piles", "hemorrhoid lump",
    ]),

    ("melena", [
        "melena", "black tarry stool", "dark stool",
        "tarry poop", "black stool", "dark tarry poop",
    ]),

    ("mouth dryness", [
        "dry mouth", "mouth is dry", "xerostomia",
        "cotton mouth", "mouth feels dry",
        "not enough saliva", "parched mouth",
        "mouth dryness", "dehydrated mouth",
    ]),

    ("mouth pain", [
        "mouth pain", "pain in mouth", "sore mouth",
        "oral pain", "mouth hurts", "mouth is painful",
    ]),

    ("mouth ulcer", [
        "mouth ulcer", "oral ulcer", "canker sore",
        "sore in mouth", "mouth sore",
        "aphthous ulcer", "blisters in mouth",
    ]),

    ("muscle cramps, contractures, or spasms", [
        "muscle cramps", "muscle spasms", "muscle contractures",
        "painful muscle cramp", "muscle locking up",
        "charlie horse", "charley horse", "muscle knot",
        "muscle seizes up",
    ]),

    ("muscle pain", [
        "muscle pain", "myalgia", "sore muscles",
        "muscles hurt", "aching muscles", "muscle ache",
        "painful muscles", "muscles are sore",
        "muscle soreness", "body muscle pain",
    ]),

    ("muscle stiffness or tightness", [
        "muscle stiffness", "stiff muscles", "tight muscles",
        "muscle tightness", "muscles feel stiff",
        "muscles won't relax",
    ]),

    ("muscle swelling", [
        "muscle swelling", "swollen muscle", "muscle is swollen",
        "puffy muscle",
    ]),

    ("muscle weakness", [
        "muscle weakness", "weak muscles", "muscles feel weak",
        "loss of muscle strength", "muscular weakness",
        "muscles are not working", "myasthenia",
    ]),

    # ── N ──────────────────────────────────────────────────────────────────

    ("nailbiting", [
        "nail biting", "biting nails", "chewing nails",
        "onychophagia",
    ]),

    ("nasal congestion", [
        "nasal congestion", "blocked nose", "stuffy nose",
        "congested nose", "nose is stuffed",
        "blocked nasal passage", "can't breathe through nose",
        "nose is blocked", "nose is congested",
        "nasal blockage", "stuffed up nose",
        "snoring from congestion",
    ]),

    ("nausea", [
        "nausea", "nauseous", "feeling sick to stomach",
        "wanting to vomit", "queasy", "upset stomach",
        "stomach feels sick", "feel like throwing up",
        "sick feeling", "stomach turning",
        "stomach is upset", "feeling nauseated",
        "gut is turning", "stomach flip",
        "seasick feeling", "morning sickness",
        "sick to my stomach",
    ]),

    ("neck cramps or spasms", [
        "neck cramps", "neck spasm", "neck muscle spasm",
        "neck seizing up", "torticollis",
    ]),

    ("neck mass", [
        "neck mass", "lump in neck", "neck lump",
        "swelling in neck",
    ]),

    ("neck pain", [
        "neck pain", "neck hurts", "pain in neck",
        "sore neck", "neck ache", "stiff neck",
        "cervical pain", "my neck hurts",
    ]),

    ("neck stiffness or tightness", [
        "stiff neck", "neck stiffness", "neck tightness",
        "neck feels tight", "neck hard to turn",
        "rigid neck", "neck mobility reduced",
    ]),

    ("neck swelling", [
        "swollen neck", "neck swelling", "neck is swollen",
        "neck looks puffy",
    ]),

    ("neck weakness", [
        "neck weakness", "weak neck", "can't hold head up",
        "neck feels weak",
    ]),

    ("nightmares", [
        "nightmares", "bad dreams", "night terrors",
        "vivid bad dreams", "recurring nightmares",
        "disturbing dreams", "waking from nightmare",
    ]),

    ("nose deformity", [
        "nose deformity", "deviated septum", "nasal deformity",
        "crooked nose", "nose looks abnormal",
    ]),

    ("nosebleed", [
        "nosebleed", "nose bleeding", "blood from nose",
        "epistaxis", "bloody nose", "nose keeps bleeding",
    ]),

    # ── O ──────────────────────────────────────────────────────────────────

    ("obsessions and compulsions", [
        "obsessions", "compulsions", "ocd", "obsessive thoughts",
        "compulsive behavior", "can't stop thinking about something",
        "repetitive behaviors", "ritualistic behavior",
    ]),

    # ── P ──────────────────────────────────────────────────────────────────

    ("pain during intercourse", [
        "pain during sex", "painful intercourse", "dyspareunia",
        "pain during intimacy", "sex is painful",
        "intercourse hurts",
    ]),

    ("pain during pregnancy", [
        "pain during pregnancy", "pregnancy pain", "pain while pregnant",
    ]),

    ("pain in eye", [
        "eye pain", "pain in eye", "eye hurts",
        "ocular pain", "eye ache", "sore eye",
    ]),

    ("pain in gums", [
        "gum pain", "pain in gums", "gums are painful",
        "aching gums",
    ]),

    ("pain in testicles", [
        "testicular pain", "pain in testicle", "sore testicle",
        "testicle hurts", "scrotal pain",
    ]),

    ("pain of the anus", [
        "anal pain", "pain in anus", "rectal pain",
        "sore anus", "anus hurts",
    ]),

    ("pain or soreness of breast", [
        "breast pain", "sore breast", "breast tenderness",
        "tender breasts", "mastalgia", "breast soreness",
        "breasts are sore", "painful breasts",
    ]),

    ("painful menstruation", [
        "painful periods", "period pain", "menstrual cramps",
        "dysmenorrhea", "severe period cramps",
        "painful menstruation", "stomach cramps with period",
        "period is very painful",
    ]),

    ("painful sinuses", [
        "sinus pain", "sinusitis", "painful sinuses",
        "pain around sinuses", "sinus pressure",
        "sinus headache", "face pain from sinuses",
    ]),

    ("painful urination", [
        "painful urination", "pain when peeing", "burning when peeing",
        "dysuria", "urination hurts", "stinging when urinating",
        "burning urination", "painful pee",
        "it burns when I pee", "discomfort when urinating",
    ]),

    ("pallor", [
        "pallor", "pale skin", "looking pale",
        "skin has no color", "ashen face",
        "pale face", "washed out appearance",
        "pale complexion", "loss of color",
    ]),

    ("palpitations", [
        "palpitations", "heart pounding", "heart racing",
        "heart fluttering", "heart skipping",
        "irregular heartbeat feeling", "feel my heartbeat",
        "heart thumping", "heart beating hard",
        "aware of heartbeat", "heart hammering",
        "heart is racing", "can feel my heart beating",
    ]),

    ("paresthesia", [
        "paresthesia", "tingling", "pins and needles",
        "numbness and tingling", "prickling sensation",
        "electric feeling in skin", "burning and tingling",
        "skin prickling", "extremities tingling",
    ]),

    ("pelvic pain", [
        "pelvic pain", "lower pelvic pain", "pain in pelvis",
        "pelvic ache", "pelvic discomfort",
        "pain in pelvic area", "lower pelvic discomfort",
    ]),

    ("pelvic pressure", [
        "pelvic pressure", "pressure in pelvis",
        "feeling of pressure in lower abdomen",
        "fullness in pelvis",
    ]),

    ("penile discharge", [
        "penile discharge", "discharge from penis",
        "pus from penis", "fluid from penis",
    ]),

    ("penis pain", [
        "penis pain", "pain in penis", "penile pain",
    ]),

    ("penis redness", [
        "redness on penis", "penis is red", "penile redness",
    ]),

    ("peripheral edema", [
        "peripheral edema", "swelling in extremities",
        "swollen hands and feet", "limb edema",
        "fluid in legs and arms", "extremity swelling",
    ]),

    ("plugged feeling in ear", [
        "plugged ear", "ear feels plugged", "blocked ear",
        "muffled hearing in ear", "ear feels full",
        "pressure in ear",
    ]),

    ("polyuria", [
        "polyuria", "excessive urination", "urinating too much",
        "producing too much urine", "large volume of urine",
    ]),

    ("poor circulation", [
        "poor circulation", "bad circulation", "cold extremities",
        "hands and feet always cold", "circulation problems",
    ]),

    ("posture problems", [
        "posture problems", "poor posture", "slouching",
        "bad posture", "spine alignment problem",
    ]),

    ("premature ejaculation", [
        "premature ejaculation", "early ejaculation",
        "sexual performance issue",
    ]),

    ("premenstrual tension or irritability", [
        "pms", "premenstrual syndrome", "irritable before period",
        "mood swings before period", "pmt",
        "premenstrual tension",
    ]),

    # ── R ──────────────────────────────────────────────────────────────────

    ("recent weight loss", [
        "weight loss", "losing weight unintentionally",
        "unexplained weight loss", "dropping weight",
        "unintentional weight loss", "lost weight for no reason",
        "body weight decreasing",
    ]),

    ("rectal bleeding", [
        "rectal bleeding", "blood from rectum", "bleeding rectum",
        "blood after passing stool",
    ]),

    ("redness in ear", [
        "red ear", "ear is red", "redness in ear",
        "ear looks inflamed",
    ]),

    ("redness in or around nose", [
        "red nose", "nose is red", "redness around nose",
        "inflamed nose",
    ]),

    ("regurgitation", [
        "regurgitation", "food coming back up", "burping up food",
        "stomach contents rising", "acid regurgitation",
    ]),

    ("restlessness", [
        "restlessness", "can't sit still", "always moving",
        "agitated", "agitation", "inner restlessness",
        "fidgeting constantly", "unable to relax",
    ]),

    ("retention of urine", [
        "urinary retention", "can't urinate", "unable to pee",
        "urine won't come out", "bladder full can't empty",
        "not able to urinate", "retention of urine",
    ]),

    ("rib pain", [
        "rib pain", "pain in ribs", "ribs hurt",
        "rib ache", "pain along ribs", "tender ribs",
    ]),

    ("ringing in ear", [
        "ringing in ear", "tinnitus", "ears ringing",
        "buzzing in ear", "ringing sound in ears",
        "high pitched ringing", "constant ringing",
    ]),

    # ── S ──────────────────────────────────────────────────────────────────

    ("scanty menstrual flow", [
        "light period", "scanty period", "oligomenorrhea light",
        "very little bleeding during period", "light flow",
    ]),

    ("seizures", [
        "seizures", "epileptic seizure", "fits",
        "convulsions", "seizing", "epilepsy episode",
        "grand mal seizure", "absence seizure",
        "body shaking uncontrollably",
    ]),

    ("sharp abdominal pain", [
        "sharp stomach pain", "stabbing abdominal pain",
        "sharp belly pain", "stabbing pain in stomach",
        "sharp pain in abdomen",
    ]),

    ("sharp chest pain", [
        "sharp chest pain", "stabbing chest pain",
        "sharp pain in chest", "knife-like chest pain",
        "piercing chest pain",
    ]),

    ("shortness of breath", [
        "shortness of breath", "short of breath", "breathlessness",
        "can't breathe", "difficulty breathing", "out of breath",
        "breathless", "SOB", "breathing problems",
        "labored breathing", "gasping for air",
        "can't get enough air", "wheezing and breathless",
        "feeling winded", "hard to breathe",
        "breathing is difficult",
    ]),

    ("shoulder cramps or spasms", [
        "shoulder cramps", "shoulder spasm", "shoulder muscle spasm",
    ]),

    ("shoulder lump or mass", [
        "shoulder lump", "lump on shoulder", "shoulder mass",
    ]),

    ("shoulder pain", [
        "shoulder pain", "shoulder hurts", "pain in shoulder",
        "sore shoulder", "shoulder ache",
        "rotator cuff pain", "my shoulder hurts",
    ]),

    ("shoulder stiffness or tightness", [
        "stiff shoulder", "shoulder stiffness", "shoulder tightness",
        "shoulder won't lift", "tight shoulder",
    ]),

    ("shoulder swelling", [
        "swollen shoulder", "shoulder swelling",
    ]),

    ("shoulder weakness", [
        "shoulder weakness", "weak shoulder", "can't raise arm",
    ]),

    ("side pain", [
        "side pain", "pain in side", "flank pain",
        "pain on side of body", "pain under ribs",
        "lateral pain",
    ]),

    ("sinus congestion", [
        "sinus congestion", "sinuses are congested",
        "sinus blockage", "stuffy sinuses",
        "sinus pressure", "congested sinuses",
        "sinuses blocked",
    ]),

    ("skin dryness, peeling, scaliness, or roughness", [
        "dry skin", "skin peeling", "scaly skin",
        "rough skin", "flaky skin",
        "skin is dry", "dehydrated skin",
        "skin scaling", "skin feels rough",
    ]),

    ("skin growth", [
        "skin growth", "growth on skin", "skin tag",
        "mole growth", "skin lesion growth",
        "new growth on skin",
    ]),

    ("skin irritation", [
        "skin irritation", "irritated skin", "skin is irritated",
        "skin sensitive", "skin reacting",
    ]),

    ("skin lesion", [
        "skin lesion", "lesion on skin", "patch on skin",
        "skin spot", "skin wound", "ulcer on skin",
    ]),

    ("skin moles", [
        "skin moles", "mole on skin", "moles",
        "pigmented mole", "dark spot on skin",
    ]),

    ("skin oiliness", [
        "oily skin", "greasy skin", "skin is oily",
        "shiny skin", "seborrhea",
    ]),

    ("skin on arm or hand looks infected", [
        "arm skin infected", "hand skin infected",
        "infection on arm", "infected arm skin",
        "red skin on arm looking infected",
    ]),

    ("skin on head or neck looks infected", [
        "scalp infection", "neck skin infected",
        "face skin infected", "head skin infected",
    ]),

    ("skin on leg or foot looks infected", [
        "leg skin infected", "foot skin infected",
        "infection on leg", "infected leg skin",
    ]),

    ("skin pain", [
        "skin pain", "painful skin", "skin is painful",
        "skin hurts to touch", "skin tenderness",
        "allodynia",
    ]),

    ("skin rash", [
        "skin rash", "rash", "rashes",
        "skin eruption", "red rash", "itchy rash",
        "hives", "urticaria", "rash on body",
        "rash on face", "blistering rash",
        "blotchy rash", "raised rash",
        "spreading rash", "macular rash",
    ]),

    ("skin swelling", [
        "skin swelling", "swollen skin", "skin is swollen",
        "localized skin edema", "skin puffiness",
    ]),

    ("sleepiness", [
        "sleepiness", "drowsiness", "feeling sleepy",
        "excessive sleepiness", "always tired and sleepy",
        "hypersomnia", "falling asleep easily",
        "daytime sleepiness", "somnolence",
    ]),

    ("sleepwalking", [
        "sleepwalking", "walking in sleep", "somnambulism",
        "walking at night while asleep",
    ]),

    ("slurring words", [
        "slurring words", "slurred speech", "slurring",
        "words coming out wrong", "speech is slurred",
        "mumbling", "dysarthria",
    ]),

    ("sneezing", [
        "sneezing", "frequent sneezing", "can't stop sneezing",
        "sneezing a lot", "constant sneezing",
        "allergy sneezing",
    ]),

    ("sore in nose", [
        "sore in nose", "nose sore", "nasal sore",
        "inside of nose sore",
    ]),

    ("sore throat", [
        "sore throat", "throat hurts", "throat is sore",
        "throat pain", "painful throat", "swallowing is painful",
        "scratchy throat", "raw throat",
        "throat is raw", "strep throat symptoms",
        "throat burning", "irritated throat",
    ]),

    ("spots or clouds in vision", [
        "spots in vision", "floaters", "visual floaters",
        "spots floating in vision", "clouds in vision",
        "dark spots in vision", "visual spots",
    ]),

    ("stiffness all over", [
        "stiff all over", "stiffness all over body",
        "generalized stiffness", "whole body stiff",
        "everything is stiff",
    ]),

    ("stomach bloating", [
        "stomach bloating", "bloated stomach", "bloated belly",
        "abdomen is bloated", "tummy is bloated",
        "feeling bloated", "abdominal bloat",
        "distended belly", "belly is full and bloated",
        "stomach feels full and puffy",
    ]),

    ("stuttering or stammering", [
        "stuttering", "stammering", "difficulty speaking fluently",
        "words won't come out smoothly",
    ]),

    ("suprapubic pain", [
        "suprapubic pain", "pain above pubic bone",
        "lower pelvic pain above pubis",
    ]),

    ("sweating", [
        "sweating", "excessive sweating", "sweats",
        "sweating a lot", "profuse sweating",
        "night sweats", "drenched in sweat",
        "clammy skin", "perspiration",
        "hyperhidrosis",
    ]),

    ("swelling of scrotum", [
        "scrotal swelling", "swollen scrotum",
        "swelling in scrotum",
    ]),

    ("swollen abdomen", [
        "swollen abdomen", "abdominal swelling",
        "distended abdomen", "belly is swollen",
        "tummy is swollen", "ascites",
    ]),

    ("swollen eye", [
        "swollen eye", "eye is swollen", "puffy eye",
        "swelling around eye", "periorbital swelling",
    ]),

    ("swollen lymph nodes", [
        "swollen lymph nodes", "swollen glands",
        "lymph nodes enlarged", "glands are swollen",
        "swollen neck glands", "swollen armpit glands",
        "lymphadenopathy", "enlarged lymph nodes",
    ]),

    ("swollen or red tonsils", [
        "swollen tonsils", "red tonsils", "tonsillitis",
        "tonsils are swollen", "inflamed tonsils",
        "tonsil swelling",
    ]),

    ("swollen tongue", [
        "swollen tongue", "tongue is swollen",
        "enlarged tongue", "tongue edema",
    ]),

    # ── T ──────────────────────────────────────────────────────────────────

    ("thirst", [
        "thirst", "excessive thirst", "always thirsty",
        "extreme thirst", "polydipsia", "can't quench thirst",
        "constantly thirsty", "drinking a lot of water",
    ]),

    ("throat feels tight", [
        "throat feels tight", "tight throat", "throat tightness",
        "throat is constricted", "throat squeezing",
        "strangling feeling in throat",
    ]),

    ("throat irritation", [
        "throat irritation", "irritated throat",
        "throat is irritated", "throat feels irritated",
        "throat scratchiness",
    ]),

    ("throat redness", [
        "throat redness", "red throat", "throat is red",
        "inflamed throat",
    ]),

    ("throat swelling", [
        "throat swelling", "swollen throat",
        "throat is swollen", "swelling in throat",
    ]),

    ("tongue bleeding", [
        "tongue bleeding", "bleeding tongue", "blood from tongue",
    ]),

    ("tongue lesions", [
        "tongue lesions", "sore on tongue", "ulcer on tongue",
        "tongue ulcer", "white patches on tongue",
    ]),

    ("tongue pain", [
        "tongue pain", "tongue hurts", "painful tongue",
        "sore tongue", "tongue is sore",
    ]),

    ("too little hair", [
        "hair loss", "losing hair", "hair falling out",
        "alopecia", "thinning hair", "bald spots",
        "hair is thin", "too little hair", "losing hair",
    ]),

    ("toothache", [
        "toothache", "tooth pain", "teeth hurt",
        "dental pain", "tooth ache", "pain in tooth",
        "throbbing tooth", "my tooth hurts",
    ]),

    # ── U ──────────────────────────────────────────────────────────────────

    ("underweight", [
        "underweight", "too thin", "very thin",
        "low body weight", "not weighing enough",
    ]),

    ("unusual color or odor to urine", [
        "urine smells unusual", "unusual urine color",
        "dark yellow urine", "cloudy urine", "foul smelling urine",
        "smelly urine", "urine has bad smell",
        "orange urine", "brown urine",
    ]),

    ("upper abdominal pain", [
        "upper abdominal pain", "upper stomach pain",
        "pain in upper abdomen", "epigastric pain",
        "pain under ribs upper", "upper belly pain",
    ]),

    # ── V ──────────────────────────────────────────────────────────────────

    ("vaginal bleeding after menopause", [
        "postmenopausal bleeding", "bleeding after menopause",
        "vaginal bleeding after menopause",
    ]),

    ("vaginal discharge", [
        "vaginal discharge", "vaginal fluid",
        "discharge from vagina", "white discharge",
        "yellow discharge from vagina",
    ]),

    ("vaginal dryness", [
        "vaginal dryness", "dry vagina", "dryness down there",
    ]),

    ("vaginal itching", [
        "vaginal itching", "itchy vagina", "vulvar itching",
        "itching down there", "vaginal pruritus",
    ]),

    ("vaginal pain", [
        "vaginal pain", "pain in vagina", "vaginal discomfort",
    ]),

    ("vaginal redness", [
        "vaginal redness", "red vagina", "vaginal inflammation",
    ]),

    ("vomiting", [
        "vomiting", "throwing up", "puking", "being sick",
        "vomit", "retching", "heaving",
        "feel like vomiting", "vomited", "threw up",
        "nausea and vomiting", "stomach emptying",
        "projectile vomiting",
    ]),

    ("vomiting blood", [
        "vomiting blood", "throwing up blood", "blood in vomit",
        "hematemesis", "bloody vomit",
    ]),

    # ── W ──────────────────────────────────────────────────────────────────

    ("warts", [
        "warts", "wart", "skin wart", "verruca",
        "plantar wart", "genital wart",
    ]),

    ("weakness", [
        "weakness", "general weakness", "feeling weak",
        "body weakness", "no strength", "lack of strength",
        "physically weak", "weakness all over",
        "feel too weak", "asthenia",
    ]),

    ("weight gain", [
        "weight gain", "gaining weight", "putting on weight",
        "unexplained weight gain", "body weight increasing",
        "weight increase",
    ]),

    ("wheezing", [
        "wheezing", "wheeze", "whistling breath",
        "breathing with wheeze", "noisy breathing wheeze",
        "chest wheeze", "high pitched breathing sound",
    ]),

    ("white discharge from eye", [
        "white eye discharge", "discharge from eye",
        "eye discharge", "crusty eye discharge",
        "gunk in eye", "eye matter",
    ]),

    ("wrist lump or mass", [
        "wrist lump", "lump on wrist", "ganglion cyst",
    ]),

    ("wrist pain", [
        "wrist pain", "wrist hurts", "pain in wrist",
        "sore wrist", "wrist ache",
    ]),

    ("wrist stiffness or tightness", [
        "stiff wrist", "wrist stiffness", "wrist tightness",
    ]),

    ("wrist swelling", [
        "swollen wrist", "wrist swelling", "wrist is swollen",
    ]),

    ("wrist weakness", [
        "weak wrist", "wrist weakness", "wrist gives out",
    ]),

    # ── Additional symptom flags ───────────────────────────────────────────

    ("postpartum problems of the breast", [
        "postpartum breast problems", "breastfeeding problems",
        "mastitis", "breast infection after delivery",
    ]),

    ("problems during pregnancy", [
        "pregnancy complications", "problems during pregnancy",
        "pregnancy issues",
    ]),

    ("problems with movement", [
        "movement problems", "difficulty moving", "mobility problems",
        "can't move properly", "movement disorder",
    ]),

    ("problems with orgasm", [
        "orgasm problems", "difficulty reaching orgasm",
        "anorgasmia",
    ]),

    ("problems with shape or size of breast", [
        "breast shape problem", "breast size abnormal",
        "asymmetric breasts",
    ]),

    ("pulling at ears", [
        "pulling at ears", "child pulling ears",
        "baby tugging on ears", "ear discomfort causing pulling",
    ]),

    ("pupils unequal", [
        "unequal pupils", "anisocoria", "one pupil bigger",
        "pupils different sizes",
    ]),

    ("pus draining from ear", [
        "pus from ear", "ear pus", "ear discharge pus",
        "draining ear infection",
    ]),

    ("pus in sputum", [
        "pus in sputum", "green sputum", "purulent sputum",
        "infected mucus", "yellow green phlegm",
    ]),

    ("pus in urine", [
        "pus in urine", "cloudy urine from pus", "pyuria",
        "infected urine",
    ]),

    ("recent pregnancy", [
        "recently pregnant", "postpartum", "just had baby",
        "recent delivery",
    ]),

    ("spotting or bleeding during pregnancy", [
        "bleeding during pregnancy", "spotting while pregnant",
        "pregnancy bleeding",
    ]),

    ("smoking problems", [
        "smoking problems", "smoking related symptoms", "smoker",
    ]),

    ("symptoms of bladder", [
        "bladder symptoms", "bladder problems", "bladder issues",
    ]),

    ("symptoms of eye", [
        "eye symptoms", "eye problems", "eye issues",
    ]),

    ("symptoms of infants", [
        "infant symptoms", "baby symptoms", "newborn symptoms",
    ]),

    ("symptoms of prostate", [
        "prostate symptoms", "prostate problems", "prostate issues",
    ]),

    ("symptoms of the face", [
        "facial symptoms", "face symptoms", "face problems",
    ]),

    ("symptoms of the kidneys", [
        "kidney symptoms", "kidney problems", "kidney issues",
    ]),

    ("symptoms of the scrotum and testes", [
        "scrotal symptoms", "testicular symptoms", "testis symptoms",
    ]),

    ("temper problems", [
        "temper problems", "anger management issues",
        "losing temper", "bad temper",
    ]),

    ("uterine contractions", [
        "uterine contractions", "contractions", "labor pains",
        "tightening of uterus", "braxton hicks",
    ]),

    ("unwanted hair", [
        "unwanted hair", "excess hair", "hirsutism",
        "facial hair on women", "body hair excessive",
    ]),

    ("unpredictable menstruation", [
        "unpredictable periods", "irregular menstruation",
        "irregular periods", "periods are unpredictable",
    ]),

    ("long menstrual periods", [
        "long periods", "period won't stop", "menstruation too long",
    ]),

    ("infrequent menstruation", [
        "infrequent periods", "periods far apart", "irregular rare periods",
    ]),

    ("hysterical behavior", [
        "hysterical behavior", "hysterics", "uncontrolled emotional outburst",
    ]),

    ("feeding", [
        "infant not feeding", "feeding issues",
    ]),

    ("feet turned in", [
        "feet turned in", "pigeon-toed", "intoeing",
    ]),

    ("vulvar irritation", [
        "vulvar irritation", "vulva irritation", "irritation down there",
    ]),

    ("vulvar sore", [
        "vulvar sore", "sore on vulva", "vulva ulcer",
    ]),

    ("wrinkles on skin", [
        "wrinkles", "skin wrinkles", "aging skin", "fine lines",
    ]),

]
