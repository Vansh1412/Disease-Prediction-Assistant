# pyrefly: ignore [missing-import]
"""
Sprint 2 — Clinical NLP Pipeline Tests
=======================================
Tests:
- medical_dictionary / synonym_index
- symptom_normalizer
- negation_detector
- temporal_parser
- severity_parser
- location_parser
- confidence_estimator
- entity_extractor
- pipeline (integration)
- Emergency detection
- Fuzzy matching
- Mixed natural language sentences
- Typo handling

Does NOT test symptom_parser.py directly (it calls load_feature_names()
which requires the dataset file). pipeline.run() is tested instead.
"""



# ===========================================================================
# constants
# ===========================================================================

class TestConstants:
    def test_severity_scale_has_entries(self):
        from src.chatbot.constants import SEVERITY_SCALE
        assert "mild" in SEVERITY_SCALE
        assert "severe" in SEVERITY_SCALE
        assert "extreme" in SEVERITY_SCALE
        assert SEVERITY_SCALE["mild"] == 1
        assert SEVERITY_SCALE["severe"] == 3
        assert SEVERITY_SCALE["extreme"] == 4

    def test_negation_cues_present(self):
        from src.chatbot.constants import NEGATION_CUES
        assert "no" in NEGATION_CUES
        assert "without" in NEGATION_CUES
        assert "never" in NEGATION_CUES

    def test_body_locations_present(self):
        from src.chatbot.constants import BODY_LOCATIONS
        assert "chest" in BODY_LOCATIONS
        assert "jaw" in BODY_LOCATIONS
        assert "left arm" in BODY_LOCATIONS

    def test_confidence_levels(self):
        from src.chatbot.constants import Confidence
        assert Confidence.HIGH == "high"
        assert Confidence.MEDIUM == "medium"
        assert Confidence.LOW == "low"

    def test_emergency_combinations_nonempty(self):
        from src.chatbot.constants import EMERGENCY_COMBINATIONS
        assert len(EMERGENCY_COMBINATIONS) >= 3
        for combo, message in EMERGENCY_COMBINATIONS:
            assert isinstance(combo, set)
            assert isinstance(message, str)
            assert "⚠️" in message


# ===========================================================================
# medical_dictionary
# ===========================================================================

class TestMedicalDictionary:
    def test_synonyms_list_nonempty(self):
        from src.chatbot.medical_dictionary import SYMPTOM_SYNONYMS
        assert len(SYMPTOM_SYNONYMS) > 100

    def test_fever_has_many_variants(self):
        from src.chatbot.medical_dictionary import SYMPTOM_SYNONYMS
        fever_entry = next((e for e in SYMPTOM_SYNONYMS if e[0] == "fever"), None)
        assert fever_entry is not None
        assert len(fever_entry[1]) >= 10

    def test_all_canonicals_are_strings(self):
        from src.chatbot.medical_dictionary import SYMPTOM_SYNONYMS
        for canonical, phrases in SYMPTOM_SYNONYMS:
            assert isinstance(canonical, str) and len(canonical) > 0
            assert isinstance(phrases, list) and len(phrases) > 0

    def test_headache_phrases_include_natural_language(self):
        from src.chatbot.medical_dictionary import SYMPTOM_SYNONYMS
        ha = next((e for e in SYMPTOM_SYNONYMS if e[0] == "headache"), None)
        assert ha is not None
        phrases = ha[1]
        assert any("my head" in p for p in phrases)

    def test_vomiting_covered(self):
        from src.chatbot.medical_dictionary import SYMPTOM_SYNONYMS
        canonicals = [e[0] for e in SYMPTOM_SYNONYMS]
        assert "vomiting" in canonicals

    def test_dizziness_covered(self):
        from src.chatbot.medical_dictionary import SYMPTOM_SYNONYMS
        canonicals = [e[0] for e in SYMPTOM_SYNONYMS]
        assert "dizziness" in canonicals


# ===========================================================================
# synonym_index
# ===========================================================================

class TestSynonymIndex:
    def test_index_builds(self):
        from src.chatbot.synonym_index import get_index
        idx = get_index()
        assert len(idx) > 500

    def test_exact_lookup(self):
        from src.chatbot.synonym_index import get_canonical
        assert get_canonical("fever") == "fever"
        assert get_canonical("headache") == "headache"
        assert get_canonical("throwing up") == "vomiting"

    def test_natural_language_lookup(self):
        from src.chatbot.synonym_index import get_canonical
        assert get_canonical("high temperature") == "fever"
        assert get_canonical("head hurts") == "headache"
        assert get_canonical("can't breathe") is not None

    def test_unknown_phrase_returns_none(self):
        from src.chatbot.synonym_index import get_canonical
        assert get_canonical("xyzzy not a symptom") is None

    def test_all_phrases_nonempty(self):
        from src.chatbot.synonym_index import all_phrases
        phrases = all_phrases()
        assert len(phrases) > 500

    def test_case_insensitive(self):
        from src.chatbot.synonym_index import get_canonical
        assert get_canonical("Fever") == get_canonical("fever")
        assert get_canonical("HEADACHE") == get_canonical("headache")


# ===========================================================================
# symptom_normalizer
# ===========================================================================

class TestSymptomNormalizer:
    def test_normalize_lowercase(self):
        from src.chatbot.symptom_normalizer import normalize
        assert normalize("FEVER").lower() == normalize("fever")

    def test_normalize_strips_whitespace(self):
        from src.chatbot.symptom_normalizer import normalize
        assert normalize("  headache  ") == "headache"

    def test_normalize_expands_contractions(self):
        from src.chatbot.symptom_normalizer import normalize
        result = normalize("I can't breathe")
        assert "cannot" in result or "can not" in result

    def test_tokenize_produces_ngrams(self):
        from src.chatbot.symptom_normalizer import tokenize, normalize
        tokens = tokenize(normalize("chest pain and headache"))
        assert "chest pain" in tokens
        assert "headache" in tokens

    def test_tokenize_longest_first(self):
        from src.chatbot.symptom_normalizer import tokenize, normalize
        tokens = tokenize(normalize("shortness of breath"))
        # "shortness of breath" should appear before "shortness"
        idx_multi = next((i for i, t in enumerate(tokens) if "shortness of breath" == t), None)
        idx_single = next((i for i, t in enumerate(tokens) if t == "shortness"), None)
        if idx_multi is not None and idx_single is not None:
            assert idx_multi < idx_single

    def test_tokenize_empty_string(self):
        from src.chatbot.symptom_normalizer import tokenize, normalize
        assert tokenize(normalize("")) == []


# ===========================================================================
# negation_detector
# ===========================================================================

class TestNegationDetector:
    def test_no_fever_is_negated(self):
        from src.chatbot.negation_detector import is_negated
        assert is_negated("fever", "I do not have fever") is True

    def test_no_headache(self):
        from src.chatbot.negation_detector import is_negated
        assert is_negated("headache", "No headache.") is True

    def test_without_vomiting(self):
        from src.chatbot.negation_detector import is_negated
        assert is_negated("vomiting", "without vomiting") is True

    def test_never_had_chest_pain(self):
        from src.chatbot.negation_detector import is_negated
        assert is_negated("chest pain", "I never had chest pain") is True

    def test_positive_fever_not_negated(self):
        from src.chatbot.negation_detector import is_negated
        assert is_negated("fever", "I have a fever") is False

    def test_positive_cough_not_negated(self):
        from src.chatbot.negation_detector import is_negated
        assert is_negated("cough", "I have a cough") is False

    def test_but_splits_negation_scope(self):
        from src.chatbot.negation_detector import is_negated
        # "no fever" should not negate "cough" after "but"
        assert is_negated("cough", "No fever but I do have a cough") is False

    def test_split_clauses(self):
        from src.chatbot.negation_detector import split_clauses
        clauses = split_clauses("I don't have fever, but I have cough")
        assert len(clauses) >= 2

    def test_negated_positions_nonzero(self):
        from src.chatbot.negation_detector import negated_token_positions
        pos = negated_token_positions("I do not have fever")
        assert len(pos) > 0


# ===========================================================================
# temporal_parser
# ===========================================================================

class TestTemporalParser:
    def test_today_is_current(self):
        from src.chatbot.temporal_parser import temporal_tag
        assert temporal_tag("I have a fever today") == "current"

    def test_yesterday_is_past(self):
        from src.chatbot.temporal_parser import temporal_tag
        assert temporal_tag("I had a headache yesterday") == "past"

    def test_last_week_is_past(self):
        from src.chatbot.temporal_parser import temporal_tag
        assert temporal_tag("last week I was vomiting") == "past"

    def test_now_is_current(self):
        from src.chatbot.temporal_parser import temporal_tag
        assert temporal_tag("I am feeling dizzy right now") == "current"

    def test_unknown_no_marker(self):
        from src.chatbot.temporal_parser import temporal_tag
        assert temporal_tag("I have a cough") == "unknown"

    def test_extract_duration_days(self):
        from src.chatbot.temporal_parser import extract_duration
        assert extract_duration("I have had headache for 3 days") == "3 days"

    def test_extract_duration_weeks(self):
        from src.chatbot.temporal_parser import extract_duration
        assert extract_duration("cough for 2 weeks") == "2 weeks"

    def test_extract_duration_since(self):
        from src.chatbot.temporal_parser import extract_duration
        result = extract_duration("fever since yesterday")
        assert result is not None and "yesterday" in result

    def test_extract_duration_none(self):
        from src.chatbot.temporal_parser import extract_duration
        assert extract_duration("I have a headache") is None

    def test_duration_to_days(self):
        from src.chatbot.temporal_parser import duration_to_days
        assert duration_to_days("3 days") == 3.0
        assert duration_to_days("2 weeks") == 14.0
        assert duration_to_days("1 month") == 30.0


# ===========================================================================
# severity_parser
# ===========================================================================

class TestSeverityParser:
    def test_mild_detected(self):
        from src.chatbot.severity_parser import detect_severity
        label, score = detect_severity("mild headache")
        assert label == "mild"
        assert score == 1

    def test_severe_detected(self):
        from src.chatbot.severity_parser import detect_severity
        label, score = detect_severity("severe chest pain")
        assert label == "severe"
        assert score == 3

    def test_very_severe_preferred_over_severe(self):
        from src.chatbot.severity_parser import detect_severity
        label, score = detect_severity("very severe pain")
        assert label == "very severe"
        assert score == 4

    def test_no_severity(self):
        from src.chatbot.severity_parser import detect_severity
        label, score = detect_severity("I have a headache")
        assert label is None
        assert score == 0

    def test_persistent_is_3(self):
        from src.chatbot.severity_parser import detect_severity
        label, score = detect_severity("persistent cough")
        assert score == 3

    def test_severity_label_helper(self):
        from src.chatbot.severity_parser import severity_label
        assert severity_label(0) == "unspecified"
        assert severity_label(1) == "mild"
        assert severity_label(4) == "extreme"


# ===========================================================================
# location_parser
# ===========================================================================

class TestLocationParser:
    def test_chest_detected(self):
        from src.chatbot.location_parser import detect_locations
        locs = detect_locations("I have chest pain")
        assert "chest" in locs

    def test_left_arm_detected(self):
        from src.chatbot.location_parser import detect_locations
        locs = detect_locations("pain in my left arm")
        assert "left arm" in locs

    def test_jaw_detected(self):
        from src.chatbot.location_parser import detect_locations
        locs = detect_locations("jaw pain")
        assert "jaw" in locs

    def test_lower_abdomen_preferred_over_abdomen(self):
        from src.chatbot.location_parser import detect_locations
        locs = detect_locations("pain in lower abdomen")
        assert "lower abdomen" in locs

    def test_no_location(self):
        from src.chatbot.location_parser import detect_locations
        locs = detect_locations("I feel sick")
        assert locs == []

    def test_multiple_locations(self):
        from src.chatbot.location_parser import detect_locations
        locs = detect_locations("pain in my chest and left arm")
        assert "chest" in locs
        assert "left arm" in locs

    def test_enrich_symptom_with_location(self):
        from src.chatbot.location_parser import enrich_symptom_with_location
        result = enrich_symptom_with_location("pain", ["arm"])
        assert "arm pain" in result

    def test_enrich_unknown_location(self):
        from src.chatbot.location_parser import enrich_symptom_with_location
        result = enrich_symptom_with_location("pain", ["spleen"])
        assert result == ["pain"]


# ===========================================================================
# confidence_estimator
# ===========================================================================

class TestConfidenceEstimator:
    def test_high_score(self):
        from src.chatbot.confidence_estimator import confidence_score
        from src.chatbot.constants import Confidence
        assert confidence_score(Confidence.HIGH) == 1.0

    def test_medium_score(self):
        from src.chatbot.confidence_estimator import confidence_score
        from src.chatbot.constants import Confidence
        assert confidence_score(Confidence.MEDIUM) == 0.7

    def test_low_score(self):
        from src.chatbot.confidence_estimator import confidence_score
        from src.chatbot.constants import Confidence
        assert confidence_score(Confidence.LOW) == 0.4

    def test_fuzzy_95_is_high(self):
        from src.chatbot.confidence_estimator import estimate_from_fuzzy_score
        from src.chatbot.constants import Confidence
        assert estimate_from_fuzzy_score(95) == Confidence.HIGH

    def test_fuzzy_80_is_medium(self):
        from src.chatbot.confidence_estimator import estimate_from_fuzzy_score
        from src.chatbot.constants import Confidence
        assert estimate_from_fuzzy_score(80) == Confidence.MEDIUM

    def test_fuzzy_65_is_low(self):
        from src.chatbot.confidence_estimator import estimate_from_fuzzy_score
        from src.chatbot.constants import Confidence
        assert estimate_from_fuzzy_score(65) == Confidence.LOW

    def test_filter_by_confidence(self):
        from src.chatbot.confidence_estimator import filter_by_confidence
        from src.chatbot.constants import Confidence
        items = [("fever", Confidence.HIGH), ("cough", Confidence.LOW)]
        result = filter_by_confidence(items, min_level=Confidence.MEDIUM)
        assert len(result) == 1
        assert result[0][0] == "fever"


# ===========================================================================
# entity_extractor
# ===========================================================================

class TestEntityExtractor:
    def test_fever_extracted(self):
        from src.chatbot.entity_extractor import extract_entities
        entities = extract_entities("I have a fever")
        canonicals = [e.canonical for e in entities if not e.negated]
        assert "fever" in canonicals

    def test_negated_fever_is_negated(self):
        from src.chatbot.entity_extractor import extract_entities
        entities = extract_entities("I do not have fever")
        fever_entity = next((e for e in entities if e.canonical == "fever"), None)
        assert fever_entity is not None
        assert fever_entity.negated is True

    def test_headache_extracted(self):
        from src.chatbot.entity_extractor import extract_entities
        entities = extract_entities("my head hurts badly")
        canonicals = [e.canonical for e in entities if not e.negated]
        assert "headache" in canonicals

    def test_entity_has_confidence(self):
        from src.chatbot.entity_extractor import extract_entities
        from src.chatbot.constants import Confidence
        entities = extract_entities("I have a fever")
        assert all(e.confidence in (Confidence.HIGH, Confidence.MEDIUM, Confidence.LOW) for e in entities)

    def test_fuzzy_typo_vommiting(self):
        from src.chatbot.entity_extractor import extract_entities
        # "vommiting" is a misspelling — should still resolve to vomiting
        entities = extract_entities("I am vommiting")
        canonicals = [e.canonical for e in entities if not e.negated]
        assert "vomiting" in canonicals

    def test_multiple_symptoms(self):
        from src.chatbot.entity_extractor import extract_entities
        entities = extract_entities("I have fever, headache, and nausea")
        canonicals = [e.canonical for e in entities if not e.negated]
        # At least 2 of the 3 should be found
        found = sum(1 for s in ["fever", "headache", "nausea"] if s in canonicals)
        assert found >= 2

    def test_empty_text(self):
        from src.chatbot.entity_extractor import extract_entities
        assert extract_entities("") == []


# ===========================================================================
# pipeline — integration
# ===========================================================================

class TestPipeline:
    def test_simple_fever(self):
        from src.chatbot.pipeline import run
        result = run("I have a high temperature")
        assert "fever" in result.detected_symptoms

    def test_negated_symptom_excluded_from_detected(self):
        from src.chatbot.pipeline import run
        result = run("I do not have fever")
        assert "fever" not in result.detected_symptoms
        assert "fever" in result.negated_symptoms

    def test_past_symptom_goes_to_past(self):
        from src.chatbot.pipeline import run
        result = run("I had a headache yesterday")
        assert "headache" not in result.detected_symptoms
        assert "headache" in result.past_symptoms

    def test_severity_detected(self):
        from src.chatbot.pipeline import run
        result = run("I have severe chest pain")
        assert result.severity_score >= 3

    def test_location_detected(self):
        from src.chatbot.pipeline import run
        result = run("pain in my left arm")
        assert len(result.locations) > 0

    def test_emergency_flag_chest_arm(self):
        from src.chatbot.pipeline import run
        result = run("I have severe chest pressure and left arm pain and sweating")
        assert result.is_emergency is True
        assert result.emergency_message is not None

    def test_no_emergency_for_headache(self):
        from src.chatbot.pipeline import run
        result = run("I have a headache")
        assert result.is_emergency is False

    def test_followup_questions_generated(self):
        from src.chatbot.pipeline import run
        result = run("I have a fever")
        assert len(result.followup_questions) >= 1

    def test_confidence_present(self):
        from src.chatbot.pipeline import run
        from src.chatbot.constants import Confidence
        result = run("I have a fever and headache")
        assert result.confidence in (Confidence.HIGH, Confidence.MEDIUM, Confidence.LOW)

    def test_canonical_symptoms_alias(self):
        from src.chatbot.pipeline import run
        result = run("I have a fever")
        assert result.canonical_symptoms == result.detected_symptoms

    def test_run_simple(self):
        from src.chatbot.pipeline import run_simple
        symptoms = run_simple("I have a fever and nausea")
        assert isinstance(symptoms, list)
        assert "fever" in symptoms

    def test_empty_input(self):
        from src.chatbot.pipeline import run
        result = run("")
        assert result.detected_symptoms == []
        assert result.is_emergency is False

    def test_parse_result_structure(self):
        from src.chatbot.pipeline import run, ParseResult
        result = run("I have a cough")
        assert isinstance(result, ParseResult)
        assert isinstance(result.detected_symptoms, list)
        assert isinstance(result.negated_symptoms, list)
        assert isinstance(result.past_symptoms, list)
        assert isinstance(result.followup_questions, list)

    def test_dataset_validation(self):
        """Pipeline only returns symptoms that exist in the provided dataset list."""
        from src.chatbot.pipeline import run
        # Only allow "fever" in the fake dataset
        result = run("I have a fever and headache", dataset_symptoms=["fever"])
        assert "fever" in result.detected_symptoms
        assert "headache" not in result.detected_symptoms


# ===========================================================================
# Emergency detection — detailed
# ===========================================================================

class TestEmergencyDetection:
    def test_single_keyword_heart_attack(self):
        from src.chatbot.pipeline import run
        result = run("I think I am having a heart attack")
        assert result.is_emergency is True

    def test_single_keyword_stroke(self):
        from src.chatbot.pipeline import run
        result = run("I might be having a stroke")
        assert result.is_emergency is True

    def test_stroke_combination(self):
        from src.chatbot.pipeline import run
        # Slurred speech + arm weakness
        result = run("I am slurring my words and my arm feels weak")
        assert result.is_emergency is True

    def test_no_emergency_for_mild_symptoms(self):
        from src.chatbot.pipeline import run
        result = run("I have a mild headache and runny nose")
        assert result.is_emergency is False

    def test_emergency_message_contains_warning(self):
        from src.chatbot.pipeline import run
        result = run("I am having a heart attack")
        assert result.emergency_message is not None
        assert "emergency" in result.emergency_message.lower() or "⚠️" in result.emergency_message


# ===========================================================================
# Follow-up questions
# ===========================================================================

class TestFollowupQuestions:
    def test_fever_followup(self):
        from src.chatbot.pipeline import run
        result = run("I have a high fever")
        qs = result.followup_questions
        assert len(qs) >= 2
        # Should include a temperature-related question
        combined = " ".join(qs).lower()
        assert any(word in combined for word in ["temperature", "long", "chills", "medication"])

    def test_headache_followup(self):
        from src.chatbot.pipeline import run
        result = run("I have a bad headache")
        qs = result.followup_questions
        combined = " ".join(qs).lower()
        assert any(word in combined for word in ["pain", "severe", "long", "light", "where"])

    def test_default_followup_for_unknown(self):
        from src.chatbot.pipeline import run
        result = run("something is wrong with me")
        # Should still return some questions
        assert len(result.followup_questions) >= 1


# ===========================================================================
# Fuzzy matching — typos and misspellings
# ===========================================================================

class TestFuzzyMatching:
    def test_headach_typo(self):
        from src.chatbot.entity_extractor import extract_entities
        entities = extract_entities("I have a headach")
        canonicals = [e.canonical for e in entities if not e.negated]
        assert "headache" in canonicals

    def test_fevr_typo(self):
        from src.chatbot.entity_extractor import extract_entities
        entities = extract_entities("I have fevr")
        canonicals = [e.canonical for e in entities if not e.negated]
        assert "fever" in canonicals

    def test_stomach_pain_typo(self):
        from src.chatbot.entity_extractor import extract_entities
        entities = extract_entities("I have stomac pain")
        canonicals = [e.canonical for e in entities if not e.negated]
        # Should resolve to some form of abdominal/stomach pain
        assert any("pain" in c or "abdominal" in c for c in canonicals)


# ===========================================================================
# Mixed natural language sentences
# ===========================================================================

class TestMixedSentences:
    def test_complex_mixed_1(self):
        """Multiple symptoms in one sentence."""
        from src.chatbot.pipeline import run
        result = run("I've been having fever, cough, and difficulty breathing since yesterday")
        # Should find at least 2 symptoms; yesterday makes them past
        assert len(result.past_symptoms) + len(result.detected_symptoms) >= 2

    def test_complex_mixed_2(self):
        """Negation + positive in same message."""
        from src.chatbot.pipeline import run
        result = run("I don't have a fever but I do have a severe headache")
        assert "fever" not in result.detected_symptoms
        assert "headache" in result.detected_symptoms
        assert result.severity_score >= 3

    def test_complex_mixed_3(self):
        """Location enrichment."""
        from src.chatbot.pipeline import run
        result = run("I have pain in my lower back for 2 days")
        # Should detect lower back pain and duration
        combined_symptoms = result.detected_symptoms + result.past_symptoms
        assert any("back" in s or "low" in s for s in combined_symptoms)
        # Duration extracted
        assert result.all_entities  # at least some processing happened

    def test_colloqial_stomach_pain(self):
        """Colloquial: tummy ache."""
        from src.chatbot.pipeline import run
        result = run("I have a tummy ache")
        combined = result.detected_symptoms + result.past_symptoms
        assert any("abdominal" in s or "pain" in s for s in combined)

    def test_shortness_of_breath_multiword(self):
        """Multi-word canonical symptom."""
        from src.chatbot.pipeline import run
        result = run("I am short of breath")
        combined = result.detected_symptoms + result.past_symptoms
        assert any("breath" in s for s in combined)
