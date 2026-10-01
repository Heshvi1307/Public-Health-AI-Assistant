"""
safety/failsafe.py - Safe default response when any part of the pipeline encounters an anomaly.
Never leaks raw LLM errors or unvalidated outputs to the user.
"""
from typing import Dict, Any, List


def get_failsafe_response(reason_message: str = "We could not safely process this information.") -> Dict[str, Any]:
    """
    Returns a guaranteed-safe clinical fallback response pinned to 'doctor_today' with high uncertainty.
    """
    return {
        "triage_level": "doctor_today",
        "summary": "We couldn't process this safely, so we recommend speaking with a healthcare professional.",
        "reasons": [
            "The assistant encountered a safety validation check or processing limit.",
            reason_message,
        ],
        "self_care_tips": [
            "Monitor your symptoms closely.",
            "Rest and avoid strenuous exertion.",
            "If symptoms worsen or any red flags appear, seek immediate medical care."
        ],
        "warning_signs": [
            "Sudden difficulty breathing or severe shortness of breath",
            "Chest pain, pressure, or dizziness",
            "High fever persisting or confusion"
        ],
        "follow_up_questions": [
            "Have your symptoms developed rapidly or gotten worse over time?",
            "Are you experiencing any other warning signs?"
        ],
        "not_assessed": [
            "A reliable automated assessment could not be safely completed from this input."
        ],
        "source_topics": ["General Public Health Safety Guidance"],
        "uncertainty": "high",
        "is_failsafe": True,
    }
