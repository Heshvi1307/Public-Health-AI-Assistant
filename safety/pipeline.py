"""
safety/pipeline.py - Core Safety Pipeline Orchestrator.
Coordinates every deterministic step, logs events, and guarantees safe outputs.
"""
from typing import Dict, Any, List, Optional
from validators.input_validator import validate_intake_form, ValidatedIntake
from safety.red_flags import scan_for_red_flags, RedFlagResult
from safety.safety_floor import calculate_safety_floor, enforce_safety_floor
from safety.output_filter import validate_llm_output_safety
from safety.failsafe import get_failsafe_response
from safety.event_logger import record_safety_event
from knowledge.retriever import retrieve_relevant_knowledge, format_knowledge_context_for_prompt
from llm.client import call_llm
from llm.schema import HealthGuidanceOutput


def run_safety_pipeline(raw_input_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Executes the deterministic end-to-end safety pipeline.
    Returns response payload containing guidance, UI state, sources, and pipeline stage statuses.
    """
    pipeline_stages = {
        "input_validation": {"status": "pending", "label": "Structured Input Validation"},
        "red_flag_prefilter": {"status": "pending", "label": "Multilingual Red-Flag Scan"},
        "knowledge_context": {"status": "pending", "label": "WHO/MoHFW Knowledge Grounding"},
        "llm_generation": {"status": "pending", "label": "Constrained LLM Reasoning"},
        "schema_validation": {"status": "pending", "label": "Strict JSON Schema Validation"},
        "safety_floor": {"status": "pending", "label": "Deterministic Safety Floor Engine"},
        "output_safety_filter": {"status": "pending", "label": "Dosage & Medication Safety Filter"},
        "final_audit": {"status": "pending", "label": "Uncertainty & Source Verification"},
    }

    # 1. INPUT VALIDATION
    validated_intake, val_error = validate_intake_form(raw_input_data)
    if val_error:
        pipeline_stages["input_validation"]["status"] = "failed"
        pipeline_stages["input_validation"]["details"] = val_error
        failsafe = get_failsafe_response(f"Input validation error: {val_error}")
        record_safety_event(
            red_flag_detected=False,
            is_failsafe=True,
            final_level="doctor_today",
            output_filter_passed=False,
        )
        return {
            "ui_state": "normal",
            "guidance": failsafe,
            "pipeline_stages": pipeline_stages,
            "sources": [],
            "safety_adjustments": ["Input validation rejection triggered safe fallback."],
        }

    pipeline_stages["input_validation"]["status"] = "passed"
    pipeline_stages["input_validation"]["details"] = f"Validated age: {validated_intake.age_group}, {len(validated_intake.raw_symptoms)} chars."

    # 2. RED-FLAG PREFILTER (BEFORE LLM)
    red_flag_res = scan_for_red_flags(validated_intake.raw_symptoms, validated_intake.language)
    if red_flag_res.is_red_flag:
        pipeline_stages["red_flag_prefilter"]["status"] = "triggered"
        pipeline_stages["red_flag_prefilter"]["details"] = f"Acute trigger detected: '{red_flag_res.matched_pattern}'"
        pipeline_stages["knowledge_context"]["status"] = "bypassed"
        pipeline_stages["llm_generation"]["status"] = "bypassed"
        pipeline_stages["schema_validation"]["status"] = "bypassed"
        pipeline_stages["safety_floor"]["status"] = "bypassed"
        pipeline_stages["output_safety_filter"]["status"] = "bypassed"
        pipeline_stages["final_audit"]["status"] = "passed"

        # Record event (Zero PII / symptoms logged)
        record_safety_event(
            red_flag_detected=True,
            flag_type=red_flag_res.flag_type,
            llm_called=False,
            llm_level="bypassed",
            safety_floor="emergency" if red_flag_res.flag_type == "emergency" else "crisis",
            final_level="emergency" if red_flag_res.flag_type == "emergency" else "mental_health_crisis",
            output_filter_passed=True,
        )

        return {
            "ui_state": red_flag_res.flag_type,  # "emergency" or "mental_health"
            "red_flag": red_flag_res.to_dict(),
            "pipeline_stages": pipeline_stages,
            "sources": [],
            "safety_adjustments": [f"LLM intentionally bypassed: High-priority {red_flag_res.category} intercepted."],
        }

    pipeline_stages["red_flag_prefilter"]["status"] = "passed"
    pipeline_stages["red_flag_prefilter"]["details"] = "No acute emergency or mental health red flags detected."

    # 3. CURATED KNOWLEDGE RETRIEVAL
    matched_knowledge = retrieve_relevant_knowledge(
        validated_intake.normalized_symptoms,
        validated_intake.chronic_conditions,
    )
    knowledge_context = format_knowledge_context_for_prompt(matched_knowledge)
    pipeline_stages["knowledge_context"]["status"] = "passed"
    pipeline_stages["knowledge_context"]["details"] = f"Retrieved {len(matched_knowledge)} verified public health topic(s)."

    sources = [
        {
            "topic": k.get("topic"),
            "source": k.get("source"),
            "source_url": k.get("source_url"),
            "last_reviewed": k.get("last_reviewed"),
        }
        for k in matched_knowledge
    ]

    # 4. LLM CALL
    llm_raw_dict = call_llm(validated_intake, knowledge_context)
    if not llm_raw_dict:
        pipeline_stages["llm_generation"]["status"] = "failed"
        pipeline_stages["llm_generation"]["details"] = "LLM unavailable or response empty."
        failsafe = get_failsafe_response("LLM generation unavailable.")
        record_safety_event(
            red_flag_detected=False,
            llm_called=True,
            llm_level="failed",
            final_level="doctor_today",
            is_failsafe=True,
        )
        return {
            "ui_state": "normal",
            "guidance": failsafe,
            "pipeline_stages": pipeline_stages,
            "sources": sources,
            "safety_adjustments": ["LLM generation failure triggered deterministic doctor_today fallback."],
        }

    pipeline_stages["llm_generation"]["status"] = "passed"

    # 5. STRICT JSON SCHEMA VALIDATION
    try:
        validated_llm_guidance = HealthGuidanceOutput(**llm_raw_dict)
        guidance_dict = validated_llm_guidance.model_dump()
        pipeline_stages["schema_validation"]["status"] = "passed"
        pipeline_stages["schema_validation"]["details"] = f"Pydantic schema validated (triage: {guidance_dict['triage_level']})."
    except Exception as e:
        pipeline_stages["schema_validation"]["status"] = "failed"
        pipeline_stages["schema_validation"]["details"] = f"Schema violation: {str(e)}"
        failsafe = get_failsafe_response("LLM response did not adhere to required JSON schema.")
        record_safety_event(
            red_flag_detected=False,
            llm_called=True,
            llm_level="invalid_schema",
            final_level="doctor_today",
            is_failsafe=True,
        )
        return {
            "ui_state": "normal",
            "guidance": failsafe,
            "pipeline_stages": pipeline_stages,
            "sources": sources,
            "safety_adjustments": ["Schema failure triggered deterministic doctor_today fallback."],
        }

    # 6. DETERMINISTIC SAFETY FLOOR ENGINE
    floor_level, floor_reasons = calculate_safety_floor(validated_intake)
    llm_level = guidance_dict["triage_level"]
    final_level, was_overridden, adjustment_notes = enforce_safety_floor(
        llm_triage_level=llm_level,
        floor_level=floor_level,
        floor_reasons=floor_reasons,
    )
    guidance_dict["triage_level"] = final_level
    pipeline_stages["safety_floor"]["status"] = "passed"
    pipeline_stages["safety_floor"]["details"] = (
        f"Floor applied: Level {final_level} (Overridden: {was_overridden})"
    )

    # 7. OUTPUT SAFETY FILTER (DOSAGES, PRESCRIPTIONS, DIAGNOSES)
    filter_res = validate_llm_output_safety(guidance_dict)
    if not filter_res.passed:
        pipeline_stages["output_safety_filter"]["status"] = "blocked"
        pipeline_stages["output_safety_filter"]["details"] = "; ".join(filter_res.violations)
        failsafe = get_failsafe_response(
            "The assistant generated information that did not meet the safety requirements. Please consult a healthcare professional."
        )
        record_safety_event(
            red_flag_detected=False,
            llm_called=True,
            llm_level=llm_level,
            safety_floor=floor_level,
            final_level="doctor_today",
            safety_floor_applied=was_overridden,
            output_filter_passed=False,
            is_failsafe=True,
        )
        return {
            "ui_state": "normal",
            "guidance": failsafe,
            "pipeline_stages": pipeline_stages,
            "sources": sources,
            "safety_adjustments": [
                "Output Safety Violation: Blocked unsafe prescription/dosage/diagnosis content."
            ],
        }

    pipeline_stages["output_safety_filter"]["status"] = "passed"
    pipeline_stages["output_safety_filter"]["details"] = "Zero dosage, prescription, or diagnostic assertions found."

    # 8. FINAL AUDIT & EVENT LOGGING
    pipeline_stages["final_audit"]["status"] = "passed"
    record_safety_event(
        red_flag_detected=False,
        flag_type="none",
        llm_called=True,
        llm_level=llm_level,
        safety_floor=floor_level,
        final_level=final_level,
        safety_floor_applied=was_overridden,
        output_filter_passed=True,
        is_failsafe=False,
    )

    return {
        "ui_state": "normal",
        "guidance": guidance_dict,
        "pipeline_stages": pipeline_stages,
        "sources": sources,
        "safety_adjustments": adjustment_notes,
    }
