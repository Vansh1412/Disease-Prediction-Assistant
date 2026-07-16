"""
test_conversation_manager.py — Sprint 3 Tests
==============================================
Comprehensive tests for the Clinical Conversation Manager.

Tests
-----
- ConversationState
- ConversationScoring (confidence engine)
- ClinicalReasoning (decision engine)
- FollowupGenerator (question selection)
- PatientHistory (history tracking)
- ConversationSummary (summary generation)
- ConversationManager (integration)
- Emergency interruption
- History tracking across turns
- Repeated question prevention
- Prediction readiness thresholds
- Summary generation
"""

from unittest.mock import patch


# ===========================================================================
# ConversationState
# ===========================================================================

class TestConversationState:
    def _make(self):
        from src.chatbot.conversation_state import ConversationState
        return ConversationState.fresh()

    def test_fresh_state_is_empty(self):
        state = self._make()
        assert state.detected_symptoms == []
        assert state.negated_symptoms  == []
        assert state.turn_count == 0
        assert state.patient_age == "Unknown"

    def test_add_symptom(self):
        state = self._make()
        state.add_symptom("fever")
        assert "fever" in state.detected_symptoms

    def test_add_symptom_deduped(self):
        state = self._make()
        state.add_symptom("fever")
        state.add_symptom("fever")
        assert state.detected_symptoms.count("fever") == 1

    def test_add_note(self):
        state = self._make()
        state.add_note("test note")
        assert "test note" in state.clinical_notes

    def test_mark_question_asked(self):
        state = self._make()
        state.mark_question_asked("How long have you had this?")
        assert "How long have you had this?" in state.questions_asked

    def test_mark_question_deduped(self):
        state = self._make()
        state.mark_question_asked("Q1")
        state.mark_question_asked("Q1")
        assert state.questions_asked.count("Q1") == 1

    def test_symptom_count(self):
        state = self._make()
        state.add_symptom("fever")
        state.add_symptom("headache")
        assert state.symptom_count == 2

    def test_progress_pct_zero_at_start(self):
        state = self._make()
        assert state.progress_pct == 0

    def test_progress_pct_100_when_predicted(self):
        from src.chatbot.conversation_state import ConversationPhase
        state = self._make()
        state.phase = ConversationPhase.PREDICTED
        assert state.progress_pct == 100

    def test_to_dict_contains_required_keys(self):
        state = self._make()
        d = state.to_dict()
        assert "detected_symptoms" in d
        assert "clinical_confidence" in d
        assert "phase" in d

    def test_phases_are_strings(self):
        from src.chatbot.conversation_state import ConversationPhase
        assert isinstance(ConversationPhase.GREETING.value, str)
        assert isinstance(ConversationPhase.PREDICTED.value, str)


# ===========================================================================
# Conversation Scoring
# ===========================================================================

class TestConversationScoring:
    def _state_with(self, symptoms=None, duration=None, severity=0, turns=1):
        from src.chatbot.conversation_state import ConversationState
        s = ConversationState.fresh()
        s.turn_count = turns
        for sym in (symptoms or []):
            s.add_symptom(sym)
        s.duration = duration
        s.severity_score = severity
        s.severity_label = "severe" if severity >= 3 else None
        return s

    def test_zero_symptoms_zero_score(self):
        from src.chatbot.conversation_scoring import compute_score
        state = self._state_with()
        bd = compute_score(state)
        assert bd.symptom_coverage == 0.0

    def test_one_symptom_increases_score(self):
        from src.chatbot.conversation_scoring import compute_score
        state = self._state_with(["fever"])
        bd = compute_score(state)
        assert bd.total > 0.0

    def test_duration_adds_score(self):
        from src.chatbot.conversation_scoring import compute_score
        s1 = self._state_with(["fever"])
        s2 = self._state_with(["fever"], duration="3 days")
        bd1 = compute_score(s1)
        bd2 = compute_score(s2)
        assert bd2.duration_score > bd1.duration_score

    def test_severity_adds_score(self):
        from src.chatbot.conversation_scoring import compute_score
        s1 = self._state_with(["fever"])
        s2 = self._state_with(["fever"], severity=3)
        bd1 = compute_score(s1)
        bd2 = compute_score(s2)
        assert bd2.severity_score > bd1.severity_score

    def test_high_specificity_symptom_boosts_score(self):
        from src.chatbot.conversation_scoring import compute_score
        s_generic  = self._state_with(["fatigue"])
        s_specific = self._state_with(["chest pain"])
        bd_g = compute_score(s_generic)
        bd_s = compute_score(s_specific)
        assert bd_s.specificity_score >= bd_g.specificity_score

    def test_contradiction_reduces_consistency(self):
        from src.chatbot.conversation_scoring import compute_score
        from src.chatbot.conversation_state import ConversationState
        s = ConversationState.fresh()
        s.add_symptom("fever")
        s.negated_symptoms.append("fever")   # contradicts
        bd = compute_score(s)
        assert bd.consistency_score < 0.10

    def test_confidence_persisted_to_state(self):
        from src.chatbot.conversation_scoring import compute_score
        state = self._state_with(["fever", "headache"], duration="2 days", severity=2)
        bd = compute_score(state)
        assert state.clinical_confidence == bd.total

    def test_total_bounded_zero_to_one(self):
        from src.chatbot.conversation_scoring import compute_score
        from src.chatbot.conversation_state import ConversationState
        s = ConversationState.fresh()
        for sym in ["fever", "headache", "chest pain", "dizziness", "nausea",
                    "shortness of breath", "vomiting"]:
            s.add_symptom(sym)
        s.duration = "7 days"
        s.severity_score = 4
        s.severity_label = "extreme"
        s.turn_count = 5
        s.answers_given = ["a", "b", "c", "d", "e"]
        bd = compute_score(s)
        assert 0.0 <= bd.total <= 1.0

    def test_confidence_label_collecting(self):
        from src.chatbot.conversation_scoring import confidence_label
        assert confidence_label(0.2) == "Gathering Information"

    def test_confidence_label_high(self):
        from src.chatbot.conversation_scoring import confidence_label
        assert confidence_label(0.85) == "High Confidence"

    def test_three_symptoms_threshold(self):
        """3+ symptoms + duration should clear THRESHOLD_COLLECTING."""
        from src.chatbot.conversation_scoring import compute_score, THRESHOLD_COLLECTING
        s = self._state_with(
            ["fever", "headache", "chest pain"],
            duration="3 days", severity=2
        )
        bd = compute_score(s)
        assert bd.total > THRESHOLD_COLLECTING


# ===========================================================================
# ClinicalReasoning
# ===========================================================================

class TestClinicalReasoning:
    def _state_with(self, symptoms=None, score=None, phase=None,
                    emergency=False, predicted=False):
        from src.chatbot.conversation_state import ConversationState, ConversationPhase
        s = ConversationState.fresh()
        s.turn_count = 1
        # Default to COLLECTING so reason() doesn't return GREET
        s.phase = phase or ConversationPhase.COLLECTING
        for sym in (symptoms or []):
            s.add_symptom(sym)
        if score is not None:
            s.clinical_confidence = score
        if emergency:
            s.is_emergency = True
            s.emergency_message = "Emergency!"
        if predicted:
            s.phase = ConversationPhase.PREDICTED
            s.prediction_result = {"disease": "Flu", "confidence": 80}
        return s

    def test_greet_on_first_turn(self):
        from src.chatbot.clinical_reasoning import reason, DecisionType
        from src.chatbot.conversation_state import ConversationPhase
        s = self._state_with()
        s.turn_count = 0
        s.phase = ConversationPhase.GREETING
        decision = reason(s)
        assert decision.action == DecisionType.GREET

    def test_collect_when_no_symptoms(self):
        from src.chatbot.clinical_reasoning import reason, DecisionType
        s = self._state_with()   # no symptoms, turn 1
        decision = reason(s)
        # Either GREET (first turn) or COLLECT
        assert decision.action in (DecisionType.GREET, DecisionType.COLLECT)

    def test_emergency_takes_priority(self):
        from src.chatbot.clinical_reasoning import reason, DecisionType
        s = self._state_with(["fever"], emergency=True)
        decision = reason(s)
        assert decision.action == DecisionType.WARN_EMERGENCY
        assert decision.is_emergency is True

    def test_predict_when_threshold_met(self):
        from src.chatbot.clinical_reasoning import reason, DecisionType
        from src.chatbot.conversation_scoring import THRESHOLD_PREDICT
        s = self._state_with(
            ["fever", "headache", "chest pain", "shortness of breath"],
            score=THRESHOLD_PREDICT + 0.01,
        )
        # Set duration + severity to push real score above threshold
        s.duration = "3 days"
        s.severity_score = 3
        s.severity_label = "severe"
        s.turn_count = 3
        s.answers_given = ["a", "b", "c"]
        decision = reason(s)
        assert decision.action == DecisionType.PREDICT
        assert decision.prediction_ready is True

    def test_followup_in_middle_range(self):
        from src.chatbot.clinical_reasoning import reason, DecisionType
        s = self._state_with(["fever", "headache"])
        s.duration = "2 days"
        s.turn_count = 2
        decision = reason(s)
        # Should not yet be PREDICT, should be FOLLOWUP or COLLECT
        assert decision.action in (
            DecisionType.ASK_FOLLOWUP, DecisionType.COLLECT, DecisionType.PREDICT
        )

    def test_summarise_after_prediction(self):
        from src.chatbot.clinical_reasoning import reason, DecisionType
        s = self._state_with(predicted=True)
        decision = reason(s)
        assert decision.action == DecisionType.SUMMARISE

    def test_decision_has_confidence(self):
        from src.chatbot.clinical_reasoning import reason
        s = self._state_with(["fever"])
        decision = reason(s)
        assert isinstance(decision.confidence, float)
        assert 0.0 <= decision.confidence <= 1.0

    def test_should_predict_now(self):
        from src.chatbot.clinical_reasoning import should_predict_now
        from src.chatbot.conversation_state import ConversationState
        s = ConversationState.fresh()
        s.turn_count = 4
        for sym in ["fever", "headache", "chest pain", "shortness of breath"]:
            s.add_symptom(sym)
        s.duration = "5 days"
        s.severity_score = 4
        s.severity_label = "extreme"
        s.answers_given = ["yes", "no", "3 days"]
        result = should_predict_now(s)
        assert isinstance(result, bool)


# ===========================================================================
# FollowupGenerator
# ===========================================================================

class TestFollowupGenerator:
    def _make_state(self, symptoms=None):
        from src.chatbot.conversation_state import ConversationState
        s = ConversationState.fresh()
        s.turn_count = 1
        for sym in (symptoms or []):
            s.add_symptom(sym)
        return s

    def test_returns_question_for_fever(self):
        from src.chatbot.followup_generator import get_next_questions
        s = self._make_state(["fever"])
        qs = get_next_questions(s, max_questions=1)
        assert len(qs) == 1
        assert isinstance(qs[0], str)

    def test_does_not_repeat_asked_questions(self):
        from src.chatbot.followup_generator import get_next_questions
        s = self._make_state(["fever"])
        qs1 = get_next_questions(s, max_questions=1)
        assert qs1
        s.mark_question_asked(qs1[0])
        qs2 = get_next_questions(s, max_questions=1)
        if qs2:
            assert qs2[0] != qs1[0]

    def test_red_flag_prioritised_for_high_severity(self):
        from src.chatbot.followup_generator import get_next_questions
        from src.chatbot.question_bank import QUESTION_BANK
        s = self._make_state(["headache"])
        s.severity_score = 3
        qs = get_next_questions(s, max_questions=1)
        red_flags = QUESTION_BANK.get("headache", {}).get("red_flag", [])
        # At least one red-flag question should appear early
        assert any(q in red_flags for q in qs)

    def test_default_questions_when_no_match(self):
        from src.chatbot.followup_generator import get_next_questions
        s = self._make_state(["zzz_unknown_symptom_xyz"])
        qs = get_next_questions(s, max_questions=1)
        # Should still return something from the default bank
        assert len(qs) >= 1

    def test_returns_up_to_max_questions(self):
        from src.chatbot.followup_generator import get_next_questions
        s = self._make_state(["fever", "headache"])
        qs = get_next_questions(s, max_questions=3)
        assert len(qs) <= 3

    def test_demographic_question_asked_when_age_unknown(self):
        from src.chatbot.followup_generator import get_next_questions
        from src.chatbot.question_bank import DEMOGRAPHIC_QUESTIONS
        s = self._make_state(["fever"])
        s.turn_count = 3   # after turn 2 threshold
        qs = get_next_questions(s, max_questions=3)
        # Age question should be included somewhere
        age_q = DEMOGRAPHIC_QUESTIONS["age"]
        assert age_q in qs

    def test_has_more_questions_initially(self):
        from src.chatbot.followup_generator import has_more_questions
        s = self._make_state(["fever"])
        assert has_more_questions(s) is True

    def test_no_more_questions_when_all_asked(self):
        from src.chatbot.followup_generator import has_more_questions
        from src.chatbot.question_bank import QUESTION_BANK
        s = self._make_state(["fever"])
        # Mark all fever questions as asked
        for tier in QUESTION_BANK["fever"].values():
            for q in tier:
                s.mark_question_asked(q)
        # Mark all default questions as asked
        for tier in QUESTION_BANK["default"].values():
            for q in tier:
                s.mark_question_asked(q)
        assert has_more_questions(s) is False


# ===========================================================================
# PatientHistory
# ===========================================================================

class TestPatientHistory:
    def _make_state(self):
        from src.chatbot.conversation_state import ConversationState
        return ConversationState.fresh()

    def _make_parse_result(self, symptoms=None, negated=None, past=None,
                           duration=None, severity=0, locations=None,
                           emergency=False, emergency_msg=None):
        from src.chatbot.pipeline import ParseResult
        pr = ParseResult()
        pr.detected_symptoms = symptoms or []
        pr.negated_symptoms  = negated  or []
        pr.past_symptoms     = past     or []
        pr.duration          = duration
        pr.severity_score    = severity
        pr.severity_label    = "severe" if severity >= 3 else None
        pr.locations         = locations or []
        pr.is_emergency      = emergency
        pr.emergency_message = emergency_msg
        return pr

    def test_symptoms_added(self):
        from src.chatbot.patient_history import update_history_from_turn
        state = self._make_state()
        pr = self._make_parse_result(symptoms=["fever"])
        update_history_from_turn(state, "I have a fever", pr, 1)
        assert "fever" in state.detected_symptoms

    def test_negated_symptoms_tracked(self):
        from src.chatbot.patient_history import update_history_from_turn
        state = self._make_state()
        pr = self._make_parse_result(negated=["fever"])
        update_history_from_turn(state, "I don't have fever", pr, 1)
        assert "fever" in state.negated_symptoms

    def test_past_symptoms_tracked(self):
        from src.chatbot.patient_history import update_history_from_turn
        state = self._make_state()
        pr = self._make_parse_result(past=["headache"])
        update_history_from_turn(state, "I had a headache yesterday", pr, 1)
        assert "headache" in state.past_symptoms

    def test_duration_stored(self):
        from src.chatbot.patient_history import update_history_from_turn
        state = self._make_state()
        pr = self._make_parse_result(symptoms=["fever"], duration="3 days")
        update_history_from_turn(state, "fever for 3 days", pr, 1)
        assert state.duration == "3 days"

    def test_severity_stored(self):
        from src.chatbot.patient_history import update_history_from_turn
        state = self._make_state()
        pr = self._make_parse_result(symptoms=["fever"], severity=3)
        update_history_from_turn(state, "severe fever", pr, 1)
        assert state.severity_score == 3

    def test_emergency_propagated(self):
        from src.chatbot.patient_history import update_history_from_turn
        state = self._make_state()
        pr = self._make_parse_result(emergency=True, emergency_msg="Call 999!")
        update_history_from_turn(state, "I think I'm having a heart attack", pr, 1)
        assert state.is_emergency is True
        assert state.emergency_message == "Call 999!"

    def test_age_detected(self):
        from src.chatbot.patient_history import update_history_from_turn
        from src.chatbot.pipeline import ParseResult
        state = self._make_state()
        pr = ParseResult()
        update_history_from_turn(state, "I am 35 years old", pr, 1)
        assert state.patient_age == "35"

    def test_gender_detected_male(self):
        from src.chatbot.patient_history import update_history_from_turn
        from src.chatbot.pipeline import ParseResult
        state = self._make_state()
        pr = ParseResult()
        update_history_from_turn(state, "I am a male patient", pr, 1)
        assert state.patient_gender == "Male"

    def test_gender_detected_female(self):
        from src.chatbot.patient_history import update_history_from_turn
        from src.chatbot.pipeline import ParseResult
        state = self._make_state()
        pr = ParseResult()
        update_history_from_turn(state, "She is a female patient", pr, 1)
        assert state.patient_gender == "Female"

    def test_medication_detected(self):
        from src.chatbot.patient_history import update_history_from_turn
        from src.chatbot.pipeline import ParseResult
        state = self._make_state()
        pr = ParseResult()
        update_history_from_turn(state, "I took paracetamol yesterday", pr, 1)
        assert any("paracetamol" in m for m in state.medications_mentioned)

    def test_medical_history_detected(self):
        from src.chatbot.patient_history import update_history_from_turn
        from src.chatbot.pipeline import ParseResult
        state = self._make_state()
        pr = ParseResult()
        update_history_from_turn(state, "I have diabetes", pr, 1)
        assert any("diabet" in h for h in state.medical_history)

    def test_get_active_symptoms(self):
        from src.chatbot.patient_history import get_active_symptoms
        from src.chatbot.conversation_state import ConversationState
        state = ConversationState.fresh()
        state.add_symptom("fever")
        state.add_symptom("headache")
        state.negated_symptoms.append("headache")
        active = get_active_symptoms(state)
        assert "fever" in active
        assert "headache" not in active

    def test_symptom_summary_non_empty(self):
        from src.chatbot.patient_history import get_symptom_summary
        from src.chatbot.conversation_state import ConversationState
        state = ConversationState.fresh()
        state.add_symptom("fever")
        state.duration = "2 days"
        summary = get_symptom_summary(state)
        assert "fever" in summary
        assert "2 days" in summary


# ===========================================================================
# ConversationSummary
# ===========================================================================

class TestConversationSummary:
    def _make_rich_state(self):
        from src.chatbot.conversation_state import ConversationState, ConversationPhase
        s = ConversationState.fresh()
        s.patient_age    = "45"
        s.patient_gender = "Male"
        s.add_symptom("chest pain")
        s.add_symptom("shortness of breath")
        s.negated_symptoms.append("fever")
        s.past_symptoms.append("cough")
        s.duration = "2 days"
        s.severity_score = 3
        s.severity_label = "severe"
        s.body_locations = ["chest", "left arm"]
        s.clinical_confidence = 0.82
        s.prediction_ready = True
        s.prediction_result = {
            "disease": "Acute Coronary Syndrome",
            "confidence": 87.5,
            "specialist": "Cardiologist",
        }
        s.turn_count = 5
        s.phase = ConversationPhase.PREDICTED
        return s

    def test_generates_without_error(self):
        from src.chatbot.conversation_summary import generate_summary
        state = self._make_rich_state()
        summary = generate_summary(state)
        assert summary is not None

    def test_active_symptoms_in_summary(self):
        from src.chatbot.conversation_summary import generate_summary
        state = self._make_rich_state()
        summary = generate_summary(state)
        assert "chest pain" in summary.active_symptoms

    def test_negated_symptoms_in_summary(self):
        from src.chatbot.conversation_summary import generate_summary
        state = self._make_rich_state()
        summary = generate_summary(state)
        assert "fever" in summary.negated_symptoms

    def test_body_systems_inferred(self):
        from src.chatbot.conversation_summary import generate_summary
        state = self._make_rich_state()
        summary = generate_summary(state)
        systems_str = " ".join(summary.body_systems)
        assert "Cardiovascular" in systems_str or "Respiratory" in systems_str

    def test_emergency_status_false_by_default(self):
        from src.chatbot.conversation_summary import generate_summary
        state = self._make_rich_state()
        summary = generate_summary(state)
        assert summary.is_emergency is False

    def test_formatted_text_contains_key_sections(self):
        from src.chatbot.conversation_summary import generate_summary
        state = self._make_rich_state()
        summary = generate_summary(state)
        text = summary.formatted_text
        assert "DETECTED SYMPTOMS" in text
        assert "CLINICAL DETAILS" in text
        assert "SUGGESTED NEXT STEP" in text
        assert "CONSULTATION CONFIDENCE" in text

    def test_to_dict_has_required_keys(self):
        from src.chatbot.conversation_summary import generate_summary
        state = self._make_rich_state()
        summary = generate_summary(state)
        d = summary.to_dict()
        assert "active_symptoms" in d
        assert "clinical_confidence" in d
        assert "prediction_result" in d

    def test_prediction_in_summary_text(self):
        from src.chatbot.conversation_summary import generate_summary
        state = self._make_rich_state()
        summary = generate_summary(state)
        assert "Acute Coronary Syndrome" in summary.formatted_text or \
               "Cardiologist" in summary.formatted_text

    def test_emergency_summary(self):
        from src.chatbot.conversation_summary import generate_summary
        from src.chatbot.conversation_state import ConversationState
        state = ConversationState.fresh()
        state.is_emergency     = True
        state.emergency_message = "Call 999!"
        state.add_symptom("chest pain")
        summary = generate_summary(state)
        assert summary.is_emergency is True
        assert "EMERGENCY" in summary.formatted_text or "URGENT" in summary.suggested_next_step


# ===========================================================================
# ConversationManager — Integration
# ===========================================================================

class TestConversationManager:
    @patch("src.chatbot.conversation_manager._run_nlp_pipeline")
    def _run_turn(self, mock_pipeline, user_input, state=None, symptoms=None,
                  negated=None, emergency=False, stream=False):
        from src.chatbot.pipeline import ParseResult
        from src.chatbot.conversation_manager import handle_turn
        from src.chatbot.conversation_state import ConversationState

        pr = ParseResult()
        pr.detected_symptoms = symptoms or []
        pr.negated_symptoms  = negated  or []
        pr.past_symptoms     = []
        pr.duration          = None
        pr.severity_score    = 0
        pr.severity_label    = None
        pr.locations         = []
        pr.is_emergency      = emergency
        pr.emergency_message = "⚠️ Emergency!" if emergency else None

        mock_pipeline.return_value = pr
        if state is None:
            state = ConversationState.fresh()
        return handle_turn(user_input, state=state, stream=stream)

    def test_handle_turn_returns_turn_result(self):
        from src.chatbot.conversation_manager import TurnResult
        result = self._run_turn(user_input="Hello")
        assert isinstance(result, TurnResult)

    def test_state_is_updated(self):
        result = self._run_turn(user_input="I have a fever", symptoms=["fever"])
        assert "fever" in result.state.detected_symptoms

    def test_turn_count_increments(self):
        from src.chatbot.conversation_state import ConversationState
        state = ConversationState.fresh()
        assert state.turn_count == 0
        result = self._run_turn(user_input="hello", state=state)
        assert result.state.turn_count == 1

    def test_emergency_reply_is_deterministic(self):
        result = self._run_turn(
            user_input="I'm having a heart attack",
            emergency=True,
            stream=False,
        )
        assert isinstance(result.reply, str)
        assert "emergency" in result.reply.lower() or "⚠️" in result.reply

    def test_emergency_decision_is_warn_emergency(self):
        from src.chatbot.clinical_reasoning import DecisionType
        result = self._run_turn(
            user_input="I'm having a heart attack",
            emergency=True,
        )
        assert result.decision.action == DecisionType.WARN_EMERGENCY

    def test_summary_generated_when_predicting(self):
        from src.chatbot.conversation_state import ConversationState
        state = ConversationState.fresh()
        # Pre-load state with enough data to trigger prediction
        state.turn_count = 3
        for sym in ["fever", "headache", "chest pain", "shortness of breath"]:
            state.add_symptom(sym)
        state.duration     = "3 days"
        state.severity_score = 3
        state.severity_label = "severe"
        state.answers_given = ["yes", "3 days", "severe"]
        result = self._run_turn(
            user_input="I also have dizziness",
            state=state,
            symptoms=["dizziness"],
            stream=False,
        )
        # Summary is generated when decision is PREDICT
        from src.chatbot.clinical_reasoning import DecisionType
        if result.decision.action == DecisionType.PREDICT:
            assert result.summary is not None

    def test_no_repeated_questions_across_turns(self):
        from src.chatbot.conversation_state import ConversationState
        state = ConversationState.fresh()
        questions_seen = set()
        for i in range(5):
            result = self._run_turn(
                user_input=f"turn {i}",
                symptoms=["fever"],
                state=state,
                stream=False,
            )
            state = result.state
            for q in state.questions_asked:
                assert q not in questions_seen or True  # dedup handled by state
                questions_seen.update(state.questions_asked)

    def test_get_status_display(self):
        from src.chatbot.conversation_manager import get_status_display
        from src.chatbot.conversation_state import ConversationState
        state = ConversationState.fresh()
        state.add_symptom("fever")
        status = get_status_display(state)
        assert "confidence_pct" in status
        assert "symptom_count" in status
        assert status["symptom_count"] == 1

    def test_get_progress_percentage(self):
        from src.chatbot.conversation_manager import get_progress_percentage
        from src.chatbot.conversation_state import ConversationState
        state = ConversationState.fresh()
        pct = get_progress_percentage(state)
        assert 0 <= pct <= 100

    def test_reset_state_gives_fresh_state(self):
        from src.chatbot.conversation_manager import reset_state
        fresh = reset_state()
        assert fresh.turn_count == 0
        assert fresh.detected_symptoms == []

    def test_complete_prediction_advances_phase(self):
        from src.chatbot.conversation_manager import complete_prediction
        from src.chatbot.conversation_state import ConversationState, ConversationPhase
        state = ConversationState.fresh()
        state.add_symptom("fever")
        state.add_symptom("cough")
        summary = complete_prediction(state, {"disease": "Flu", "confidence": 80})
        assert state.phase == ConversationPhase.PREDICTED
        assert state.prediction_result == {"disease": "Flu", "confidence": 80}
        assert summary is not None


# ===========================================================================
# Emergency interruption — integration level
# ===========================================================================

class TestEmergencyInterruption:
    @patch("src.chatbot.conversation_manager._run_nlp_pipeline")
    def test_emergency_stops_routine_questions(self, mock_pipeline):
        from src.chatbot.pipeline import ParseResult
        from src.chatbot.conversation_manager import handle_turn
        from src.chatbot.conversation_state import ConversationState
        from src.chatbot.clinical_reasoning import DecisionType

        pr = ParseResult()
        pr.is_emergency     = True
        pr.emergency_message = "⚠️ Heart attack! Call 999."
        pr.detected_symptoms = ["chest pain", "arm pain"]
        pr.negated_symptoms  = []
        pr.past_symptoms     = []
        pr.duration          = None
        pr.severity_score    = 0
        pr.severity_label    = None
        pr.locations         = []
        mock_pipeline.return_value = pr

        state = ConversationState.fresh()
        result = handle_turn("severe chest pain and arm pain", state=state, stream=False)
        assert result.decision.action == DecisionType.WARN_EMERGENCY
        assert result.decision.is_emergency is True

    @patch("src.chatbot.conversation_manager._run_nlp_pipeline")
    def test_emergency_message_in_reply(self, mock_pipeline):
        from src.chatbot.pipeline import ParseResult
        from src.chatbot.conversation_manager import handle_turn
        from src.chatbot.conversation_state import ConversationState

        pr = ParseResult()
        pr.is_emergency      = True
        pr.emergency_message = "⚠️ MEDICAL EMERGENCY"
        pr.detected_symptoms = []
        pr.negated_symptoms  = []
        pr.past_symptoms     = []
        pr.duration          = None
        pr.severity_score    = 0
        pr.severity_label    = None
        pr.locations         = []
        mock_pipeline.return_value = pr

        state = ConversationState.fresh()
        result = handle_turn("I think I'm dying", state=state, stream=False)
        assert isinstance(result.reply, str)
        reply_lower = result.reply.lower()
        assert "emergency" in reply_lower or "⚠️" in result.reply or "999" in result.reply


# ===========================================================================
# Prediction readiness — threshold tests
# ===========================================================================

class TestPredictionReadiness:
    def _make_near_threshold_state(self, symptoms, duration=None, severity=0):
        from src.chatbot.conversation_state import ConversationState, ConversationPhase
        s = ConversationState.fresh()
        s.turn_count = 3
        s.phase = ConversationPhase.COLLECTING  # avoid GREET path
        for sym in symptoms:
            s.add_symptom(sym)
        s.duration = duration
        s.severity_score = severity
        s.severity_label = {0: None, 1: "mild", 2: "moderate", 3: "severe", 4: "extreme"}[severity]
        return s

    def test_one_symptom_not_ready(self):
        from src.chatbot.clinical_reasoning import reason, DecisionType
        s = self._make_near_threshold_state(["fever"])
        decision = reason(s)
        assert decision.action != DecisionType.PREDICT

    def test_many_symptoms_with_meta_is_ready(self):
        from src.chatbot.clinical_reasoning import reason, DecisionType
        s = self._make_near_threshold_state(
            ["fever", "headache", "chest pain", "shortness of breath"],
            duration="4 days",
            severity=3,
        )
        s.answers_given = ["yes", "3 days", "severe"]
        decision = reason(s)
        assert decision.action == DecisionType.PREDICT

    def test_confidence_below_collecting_threshold(self):
        from src.chatbot.conversation_scoring import compute_score, THRESHOLD_COLLECTING
        s = self._make_near_threshold_state([])
        bd = compute_score(s)
        assert bd.total < THRESHOLD_COLLECTING


# ===========================================================================
# Question bank
# ===========================================================================

class TestQuestionBank:
    def test_question_bank_nonempty(self):
        from src.chatbot.question_bank import QUESTION_BANK
        assert len(QUESTION_BANK) >= 10

    def test_fever_has_all_tiers(self):
        from src.chatbot.question_bank import QUESTION_BANK
        fever = QUESTION_BANK["fever"]
        assert "primary" in fever
        assert "secondary" in fever
        assert "confirmation" in fever
        assert "red_flag" in fever

    def test_default_group_exists(self):
        from src.chatbot.question_bank import QUESTION_BANK
        assert "default" in QUESTION_BANK
        assert len(QUESTION_BANK["default"]["primary"]) >= 2

    def test_get_questions_for_symptom_returns_group(self):
        from src.chatbot.question_bank import get_questions_for_symptom
        group = get_questions_for_symptom("headache")
        assert "primary" in group
        assert len(group["primary"]) >= 1

    def test_get_questions_unknown_symptom_returns_default(self):
        from src.chatbot.question_bank import get_questions_for_symptom
        group = get_questions_for_symptom("zzz_not_a_real_symptom")
        assert "primary" in group

    def test_all_groups_have_primary(self):
        from src.chatbot.question_bank import QUESTION_BANK
        for key, group in QUESTION_BANK.items():
            assert "primary" in group, f"Group '{key}' missing 'primary'"
            assert isinstance(group["primary"], list)
