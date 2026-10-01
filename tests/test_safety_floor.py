"""
tests/test_safety_floor.py - Tests for post-LLM deterministic safety floor.
"""
from validators.input_validator import validate_intake_form
from safety.safety_floor import calculate_safety_floor, enforce_safety_floor


def test_pediatric_fever_floor():
    intake, err = validate_intake_form({
        "age_group": "1-5",
        "sex": "Female",
        "duration": "4-7 days",
        "severity": "Moderate",
        "chronic_conditions": ["None"],
        "symptoms_text": "Child has fever for 4 days",
    })
    assert err is None
    floor_level, reasons = calculate_safety_floor(intake)
    assert floor_level in ["doctor_today", "emergency"]
    
    # Verify LLM de-escalation prevention
    final_level, overridden, notes = enforce_safety_floor("self_care", floor_level, reasons)
    assert final_level == "doctor_today"
    assert overridden is True


def test_severe_symptoms_floor():
    intake, err = validate_intake_form({
        "age_group": "18-59",
        "sex": "Male",
        "duration": "1-3 days",
        "severity": "Severe",
        "chronic_conditions": ["None"],
        "symptoms_text": "Very severe body aches",
    })
    floor_level, reasons = calculate_safety_floor(intake)
    assert floor_level == "doctor_today"


def test_critical_combination_fever_stiff_neck():
    intake, err = validate_intake_form({
        "age_group": "18-59",
        "sex": "Male",
        "duration": "1-3 days",
        "severity": "Moderate",
        "chronic_conditions": ["None"],
        "symptoms_text": "fever and stiff neck cannot move head",
    })
    floor_level, reasons = calculate_safety_floor(intake)
    assert floor_level == "emergency"


def test_llm_escalation_allowed_but_not_deescalation():
    # LLM says emergency, floor says self_care -> final is emergency
    final, overridden, _ = enforce_safety_floor("emergency", "self_care", [])
    assert final == "emergency"
    assert overridden is False

    # LLM says self_care, floor says doctor_today -> final is doctor_today
    final, overridden, _ = enforce_safety_floor("self_care", "doctor_today", ["Rule"])
    assert final == "doctor_today"
    assert overridden is True
