"""
validators/input_validator.py - Validates structured intake and sanitizes symptom text.
"""
import re
import unicodedata
from typing import List, Optional, Tuple
from pydantic import BaseModel, Field

VALID_AGE_GROUPS = ["<1 yr", "1-5", "6-17", "18-59", "60+"]
VALID_SEX_OPTIONS = ["Male", "Female", "Prefer not to say"]
VALID_PREGNANCY_OPTIONS = ["Yes", "No", "Not applicable"]
VALID_DURATIONS = ["<24h", "1-3 days", "4-7 days", ">1 week", "Don't know"]
VALID_SEVERITIES = ["Mild", "Moderate", "Severe", "Don't know"]
VALID_CHRONIC_CONDITIONS = ["Diabetes", "Heart disease", "Asthma/COPD", "Kidney disease", "None"]

MAX_SYMPTOMS_LENGTH = 500


class StructuredIntakeInput(BaseModel):
    age_group: str
    sex: str
    pregnant: Optional[str] = "Not applicable"
    duration: str
    severity: str
    chronic_conditions: List[str] = Field(default_factory=list)
    symptoms_text: str = ""
    language: Optional[str] = "en"  # "en", "hi", "gu"


class ValidatedIntake(BaseModel):
    age_group: str
    sex: str
    pregnant: str
    duration: str
    severity: str
    chronic_conditions: List[str]
    raw_symptoms: str
    normalized_symptoms: str
    safe_data_wrapped: str
    language: str


def sanitize_and_normalize_text(text: str) -> Tuple[str, str]:
    """
    Sanitize and normalize user free-text.
    Returns (cleaned_original, normalized_lower).
    Limits to MAX_SYMPTOMS_LENGTH characters.
    """
    if not text:
        return "", ""

    # Truncate to maximum allowed length
    truncated = text[:MAX_SYMPTOMS_LENGTH].strip()

    # Unicode normalization
    normalized = unicodedata.normalize("NFKC", truncated)

    # Trim excessive whitespaces
    cleaned_original = re.sub(r"\s+", " ", normalized).strip()
    normalized_lower = cleaned_original.lower()

    return cleaned_original, normalized_lower


def wrap_user_input_as_data(text: str) -> str:
    """
    Wraps free-text to explicitly treat it as untrusted DATA, never instructions.
    """
    return f"<user_input>\n{text}\n</user_input>"


def validate_intake_form(data: dict) -> Tuple[Optional[ValidatedIntake], Optional[str]]:
    """
    Validates every structured intake field and free-text symptoms.
    Returns (ValidatedIntake, None) or (None, error_message).
    """
    age_group = data.get("age_group", "")
    if age_group not in VALID_AGE_GROUPS:
        return None, f"Invalid age_group: '{age_group}'. Must be one of {VALID_AGE_GROUPS}"

    sex = data.get("sex", "")
    if sex not in VALID_SEX_OPTIONS:
        return None, f"Invalid sex: '{sex}'. Must be one of {VALID_SEX_OPTIONS}"

    pregnant = data.get("pregnant", "Not applicable")
    if sex != "Female":
        pregnant = "Not applicable"
    elif pregnant not in VALID_PREGNANCY_OPTIONS:
        return None, f"Invalid pregnancy selection: '{pregnant}'"

    duration = data.get("duration", "")
    if duration not in VALID_DURATIONS:
        return None, f"Invalid duration: '{duration}'. Must be one of {VALID_DURATIONS}"

    severity = data.get("severity", "")
    if severity not in VALID_SEVERITIES:
        return None, f"Invalid severity: '{severity}'. Must be one of {VALID_SEVERITIES}"

    chronic_input = data.get("chronic_conditions", [])
    if not isinstance(chronic_input, list):
        return None, "chronic_conditions must be a list."
    
    # Filter or validate chronic conditions
    chronic_conditions = []
    for cond in chronic_input:
        if cond in VALID_CHRONIC_CONDITIONS and cond != "None":
            chronic_conditions.append(cond)
    if not chronic_conditions:
        chronic_conditions = ["None"]

    raw_symptoms = str(data.get("symptoms_text", ""))
    cleaned_orig, norm_lower = sanitize_and_normalize_text(raw_symptoms)
    wrapped = wrap_user_input_as_data(cleaned_orig)

    lang = str(data.get("language", "en")).lower()
    if lang not in ["en", "hi", "gu"]:
        lang = "en"

    validated = ValidatedIntake(
        age_group=age_group,
        sex=sex,
        pregnant=pregnant,
        duration=duration,
        severity=severity,
        chronic_conditions=chronic_conditions,
        raw_symptoms=cleaned_orig,
        normalized_symptoms=norm_lower,
        safe_data_wrapped=wrapped,
        language=lang,
    )
    return validated, None
