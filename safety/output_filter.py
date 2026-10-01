"""
safety/output_filter.py - Scans LLM output for forbidden dosage, medication, and diagnosis claims.
Enforces the zero-tolerance output safety boundary.
"""
import re
from typing import Dict, Any, List, Tuple

# Dosage patterns: numbers followed by units or direct dosage phrases
DOSAGE_PATTERNS = [
    r"\b\d+(\.\d+)?\s*(mg|ml|mcg|milligram|milliliter|tab|tablet|tablets|cap|capsule|capsules|drops)\b",
    r"\btake\s+\d+\s+(tablet|tablets|capsule|capsules|pill|pills)\b",
    r"\bdose\s+of\s+\d+",
    r"\b\d+\s*times\s+a\s+day\b",
]

# Prohibited medications (except approved non-pharmacological hydration ORS)
PROHIBITED_MEDICATIONS = [
    r"\bparacetamol\b",
    r"\bibuprofen\b",
    r"\bazithromycin\b",
    r"\bamoxicillin\b",
    r"\bantibiotic\b",
    r"\bantibiotics\b",
    r"\bcrocin\b",
    r"\bdolo\b",
    r"\baspirin\b",
    r"\bciprofloxacin\b",
    r"\bmetformin\b",
    r"\batorvastatin\b",
    r"\bprednisone\b",
    r"\bdoxycycline\b",
    r"\bcombiflam\b",
    r"\bcalpol\b",
]

# Prohibited definitive diagnostic assertions
DIAGNOSIS_PATTERNS = [
    r"\byou\s+have\s+(dengue|malaria|typhoid|covid|pneumonia|bronchitis|tuberculosis|influenza|flu)\b",
    r"\byou\s+are\s+suffering\s+from\b",
    r"\bthis\s+is\s+(dengue|malaria|typhoid|covid|pneumonia)\b",
    r"\byou\s+are\s+diagnosed\s+with\b",
    r"\bdiagnosis:\s*[a-zA-Z]+\b",
    r"\byou\s+definitely\s+have\b",
]


class OutputFilterResult:
    def __init__(self, passed: bool, violations: List[str]):
        self.passed = passed
        self.violations = violations

    def to_dict(self) -> Dict[str, Any]:
        return {
            "passed": self.passed,
            "violations": self.violations,
        }


def scan_text_for_violations(text: str) -> List[str]:
    """
    Checks an individual text string for dosage, medication, or diagnosis violations.
    """
    violations = []
    if not text:
        return violations

    lower_text = text.lower()

    # 1. Dosage scan
    for pat in DOSAGE_PATTERNS:
        matches = re.findall(pat, lower_text)
        if matches:
            violations.append(f"Forbidden dosage pattern detected: '{matches[0]}'")

    # 2. Medication scan
    for pat in PROHIBITED_MEDICATIONS:
        match = re.search(pat, lower_text)
        if match:
            violations.append(f"Forbidden medication reference detected: '{match.group(0)}'")

    # 3. Diagnostic assertion scan
    for pat in DIAGNOSIS_PATTERNS:
        match = re.search(pat, lower_text)
        if match:
            violations.append(f"Forbidden diagnostic assertion detected: '{match.group(0)}'")

    return violations


def validate_llm_output_safety(output_dict: Dict[str, Any]) -> OutputFilterResult:
    """
    Recursively scans the full JSON output of the LLM for any safety violations.
    """
    violations = []

    def inspect_value(val: Any):
        if isinstance(val, str):
            v_list = scan_text_for_violations(val)
            violations.extend(v_list)
        elif isinstance(val, list):
            for item in val:
                inspect_value(item)
        elif isinstance(val, dict):
            for k, item in val.items():
                inspect_value(item)

    inspect_value(output_dict)

    return OutputFilterResult(
        passed=len(violations) == 0,
        violations=violations
    )
