"""
safety/safety_floor.py - Deterministic rule engine applied after LLM.
Enforces the safety floor: The LLM can escalate urgency, but can NEVER de-escalate.
"""
import re
from typing import Dict, Any, List, Tuple
from validators.input_validator import ValidatedIntake

# Ordinal rank of triage urgency
LEVEL_RANKS = {
    "self_care": 0,
    "doctor_2_3_days": 1,
    "doctor_today": 2,
    "emergency": 3,
}

RANK_TO_LEVEL = {
    0: "self_care",
    1: "doctor_2_3_days",
    2: "doctor_today",
    3: "emergency",
}


def calculate_safety_floor(intake: ValidatedIntake) -> Tuple[str, List[str]]:
    """
    Computes the deterministic minimum triage urgency level and the reasons triggering it.
    Returns (floor_level, list_of_rule_reasons).
    """
    highest_rank = 0
    reasons = []

    text = intake.normalized_symptoms
    age = intake.age_group
    severity = intake.severity
    duration = intake.duration
    chronic = [c for c in intake.chronic_conditions if c != "None"]
    pregnant = intake.pregnant == "Yes"

    # Multilingual/phonetic checks for fever, rash, stiff neck, headache, vomiting
    has_fever = bool(re.search(r"\b(fever|temp|high\s+temp|temperature|bukhar|बुखार|ताप|તાવ)\b", text))
    has_cough = bool(re.search(r"\b(cough|khansi|खांसी|ઉધરસ|કફ)\b", text))
    has_stiff_neck = bool(re.search(r"\b(stiff\s*neck|neck\s*stiffness|गर्दन\s*अकड़|ગરદન\s*કડક)\b", text))
    has_rash = bool(re.search(r"\b(rash|spots|petechiae|चकत्ते|દાણા|રેશ)\b", text))
    has_headache = bool(re.search(r"\b(headache|head\s*pain|sir\s*dard|sar\s*dard|सिर\s*दर्द|માથાનો\s*દુખાવો)\b", text))
    has_vomiting = bool(re.search(r"\b(vomit|vomiting|ulti|उल्टी|ઉલટી)\b", text))
    has_confusion = bool(re.search(r"\b(confusion|confused|drowsy|drowsiness|lethargic|बेसुध|ચક્કર)\b", text))
    has_no_urine = bool(re.search(r"\b(no\s*urine|not\s*urinating|no\s*pee|पेशाब\s*नहीं|પેશાબ\s*નથી)\b", text))

    # --- RULE GROUP 1: CRITICAL COMBINATION OVERRIDES (EMERGENCY = Rank 3) ---
    if has_fever and has_stiff_neck:
        highest_rank = max(highest_rank, 3)
        reasons.append("Safety rule: Fever accompanied by neck stiffness indicates potential acute neurological risk (Emergency).")

    if has_headache and has_vomiting and has_confusion:
        highest_rank = max(highest_rank, 3)
        reasons.append("Safety rule: Severe headache combined with vomiting and altered mental state requires urgent emergency evaluation.")

    if has_vomiting and has_no_urine:
        highest_rank = max(highest_rank, 3)
        reasons.append("Safety rule: Fluid loss with cessation of urine output indicates severe acute dehydration.")

    if has_fever and has_rash and age in ["<1 yr", "1-5"]:
        highest_rank = max(highest_rank, 3)
        reasons.append("Safety rule: Fever with acute rash in young children warrants immediate emergency pediatric assessment.")

    # --- RULE GROUP 2: HIGH CLINICAL RISK (DOCTOR TODAY = Rank 2) ---
    if severity == "Severe":
        highest_rank = max(highest_rank, 2)
        reasons.append("Safety rule: Reported severity is Severe; requires professional evaluation today.")

    if age == "<1 yr":
        highest_rank = max(highest_rank, 2)
        reasons.append("Safety rule: High-risk vulnerable infant age group (<1 year); minimum care level is Doctor Today.")

    if age == "1-5" and (duration in ["4-7 days", ">1 week"] or has_fever):
        highest_rank = max(highest_rank, 2)
        reasons.append(f"Safety rule: Child age 1-5 with concerning illness/duration ({duration}); requires Doctor Today.")

    if pregnant and (has_fever or severity in ["Moderate", "Severe"]):
        highest_rank = max(highest_rank, 2)
        reasons.append("Safety rule: Pregnancy with symptomatic illness requires direct same-day obstetric/medical evaluation.")

    if chronic and (has_fever or severity in ["Moderate", "Severe"] or duration in ["4-7 days", ">1 week"]):
        highest_rank = max(highest_rank, 2)
        reasons.append(f"Safety rule: Underlying chronic condition ({', '.join(chronic)}) with ongoing symptoms requires direct medical assessment.")

    if has_fever and duration in ["4-7 days", ">1 week"]:
        highest_rank = max(highest_rank, 2)
        reasons.append(f"Safety rule: Prolonged fever ({duration}) warrants prompt laboratory/clinical investigation today.")

    # --- RULE GROUP 3: MODERATE CAUTION (DOCTOR IN 2-3 DAYS = Rank 1) ---
    if duration == ">1 week" and highest_rank < 1:
        highest_rank = max(highest_rank, 1)
        reasons.append("Safety rule: Illness persisting beyond one week warrants planned professional medical follow-up.")

    if has_cough and duration in ["4-7 days", ">1 week"] and highest_rank < 1:
        highest_rank = max(highest_rank, 1)
        reasons.append("Safety rule: Persistent cough requires clinical chest examination.")

    if age == "60+" and highest_rank < 1:
        highest_rank = max(highest_rank, 1)
        reasons.append("Safety rule: Older adult age group (60+) warrants elevated clinical vigilance.")

    if (duration == "Don't know" or severity == "Don't know") and highest_rank < 1:
        highest_rank = max(highest_rank, 1)
        reasons.append("Safety rule: Incomplete information regarding symptom duration or severity mandates cautious in-person review.")

    floor_level = RANK_TO_LEVEL[highest_rank]
    return floor_level, reasons


def enforce_safety_floor(
    llm_triage_level: str,
    floor_level: str,
    floor_reasons: List[str],
) -> Tuple[str, bool, List[str]]:
    """
    Enforces the safety floor.
    The final triage level is max(rank(llm_level), rank(floor_level)).
    Returns (final_level, was_overridden, adjustment_notes).
    """
    llm_clean = llm_triage_level.strip().lower() if llm_triage_level else "self_care"
    llm_rank = LEVEL_RANKS.get(llm_clean, 0)
    floor_rank = LEVEL_RANKS.get(floor_level, 0)

    notes = []
    if floor_rank > llm_rank:
        final_level = RANK_TO_LEVEL[floor_rank]
        was_overridden = True
        notes.append(
            f"Safety Floor Triggered: Triage urgency escalated from '{llm_clean}' to '{final_level}' by deterministic rule."
        )
        for r in floor_reasons:
            notes.append(r)
    else:
        final_level = RANK_TO_LEVEL[llm_rank]
        was_overridden = False

    return final_level, was_overridden, notes
