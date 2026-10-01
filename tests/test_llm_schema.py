"""
tests/test_llm_schema.py - Tests for Pydantic schema validation and fail-safe behavior.
"""
import pytest
from pydantic import ValidationError
from llm.schema import HealthGuidanceOutput
from safety.failsafe import get_failsafe_response


def test_valid_schema():
    valid_data = {
        "triage_level": "self_care",
        "summary": "Mild cold symptoms consistent with viral irritation.",
        "reasons": ["Short duration", "Mild intensity"],
        "self_care_tips": ["Rest", "Warm liquids"],
        "warning_signs": ["Difficulty breathing"],
        "follow_up_questions": ["Any sore throat?"],
        "not_assessed": ["Definitive diagnosis requires clinical exam"],
        "source_topics": ["Common Cold"],
        "uncertainty": "low",
    }
    obj = HealthGuidanceOutput(**valid_data)
    assert obj.triage_level == "self_care"
    assert obj.uncertainty == "low"


def test_schema_rejects_invalid_triage_level():
    bad_data = {
        "triage_level": "totally_fine_go_party",  # Invalid
        "summary": "Summary",
        "uncertainty": "low",
    }
    with pytest.raises(ValidationError):
        HealthGuidanceOutput(**bad_data)


def test_failsafe_response_guarantees_doctor_today():
    fs = get_failsafe_response("Schema validation failure")
    assert fs["triage_level"] == "doctor_today"
    assert fs["uncertainty"] == "high"
    assert fs["is_failsafe"] is True
