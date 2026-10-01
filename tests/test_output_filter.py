"""
tests/test_output_filter.py - Tests for output safety violations (dosages, drugs, diagnosis claims).
"""
from safety.output_filter import scan_text_for_violations, validate_llm_output_safety


def test_dosage_detection():
    v1 = scan_text_for_violations("Take 500 mg paracetamol twice a day")
    assert any("dosage" in v.lower() for v in v1)

    v2 = scan_text_for_violations("Administer 5 ml of syrup")
    assert any("dosage" in v.lower() for v in v2)

    v3 = scan_text_for_violations("Take 2 tablets before sleep")
    assert any("dosage" in v.lower() for v in v3)


def test_prohibited_medications():
    v = scan_text_for_violations("You should start amoxicillin or another antibiotic")
    assert any("medication" in v.lower() for v in v)


def test_diagnostic_claims_blocked():
    v1 = scan_text_for_violations("Based on your symptoms, you have dengue fever.")
    assert any("diagnostic" in v.lower() for v in v1)

    v2 = scan_text_for_violations("You are suffering from malaria.")
    assert any("diagnostic" in v.lower() for v in v2)


def test_clean_output_passes():
    clean_dict = {
        "summary": "These symptoms can have several possible causes.",
        "reasons": ["Common cold symptoms peak in 2 to 3 days"],
        "self_care_tips": ["Drink plenty of warm water", "Ensure adequate rest"],
        "warning_signs": ["Difficulty breathing", "Fever exceeding 3 days"],
        "not_assessed": ["Definitive diagnosis requires in-person medical evaluation"],
    }
    res = validate_llm_output_safety(clean_dict)
    assert res.passed is True
    assert len(res.violations) == 0
