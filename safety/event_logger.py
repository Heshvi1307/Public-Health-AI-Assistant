"""
safety/event_logger.py - In-memory, privacy-preserving audit log of pipeline executions.
Strictly records metadata and safety decisions; NEVER stores raw symptoms or PII.
"""
from datetime import datetime, timezone
from typing import List, Dict, Any

# Ring buffer for recent safety audit logs
MAX_LOG_EVENTS = 100
_SAFETY_EVENT_LOG: List[Dict[str, Any]] = []


def record_safety_event(
    red_flag_detected: bool,
    flag_type: str = "none",
    llm_called: bool = False,
    llm_level: str = "none",
    safety_floor: str = "self_care",
    final_level: str = "self_care",
    safety_floor_applied: bool = False,
    output_filter_passed: bool = True,
    is_failsafe: bool = False,
) -> Dict[str, Any]:
    """
    Records an anonymized safety pipeline transaction.
    No free text, symptoms, or user identifiers are ever recorded.
    """
    event = {
        "id": len(_SAFETY_EVENT_LOG) + 1,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "red_flag_detected": red_flag_detected,
        "flag_type": flag_type,
        "llm_called": llm_called,
        "llm_level": llm_level,
        "safety_floor": safety_floor,
        "safety_floor_applied": safety_floor_applied,
        "final_level": final_level,
        "output_filter": "passed" if output_filter_passed else "blocked",
        "is_failsafe": is_failsafe,
    }

    _SAFETY_EVENT_LOG.append(event)
    if len(_SAFETY_EVENT_LOG) > MAX_LOG_EVENTS:
        _SAFETY_EVENT_LOG.pop(0)

    return event


def get_safety_event_logs() -> List[Dict[str, Any]]:
    """Returns the list of recorded safety events."""
    return list(reversed(_SAFETY_EVENT_LOG))


def clear_safety_event_logs() -> None:
    """Clears the in-memory audit log."""
    _SAFETY_EVENT_LOG.clear()
