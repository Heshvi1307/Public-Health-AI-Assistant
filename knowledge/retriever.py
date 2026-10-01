"""
knowledge/retriever.py - Retrieves curated, source-attributed health context.
Grounds the LLM against verified public health information (WHO, MoHFW).
"""
import json
from pathlib import Path
from typing import List, Dict, Any

KNOWLEDGE_FILE = Path(__file__).parent / "base.json"


def load_knowledge_base() -> List[Dict[str, Any]]:
    if not KNOWLEDGE_FILE.exists():
        return []
    with open(KNOWLEDGE_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)
        return data.get("entries", [])


def retrieve_relevant_knowledge(symptoms_text: str, chronic_conditions: List[str] = None) -> List[Dict[str, Any]]:
    """
    Matches user normalized symptom text and chronic conditions against curated knowledge entries.
    Returns matched entries, or fallback to general_self_care if none specifically match.
    """
    entries = load_knowledge_base()
    text = (symptoms_text or "").lower()
    matched = []

    for entry in entries:
        # Check topic or aliases
        aliases = [a.lower() for a in entry.get("aliases", [])]
        topic_words = entry.get("topic", "").lower()

        if any(alias in text for alias in aliases) or any(w in text for w in topic_words.split()):
            if entry not in matched:
                matched.append(entry)

    # If no specific topic matched, attach the general self-care entry
    if not matched:
        general_entry = next((e for e in entries if e.get("id") == "general_self_care"), None)
        if general_entry:
            matched.append(general_entry)

    return matched


def format_knowledge_context_for_prompt(entries: List[Dict[str, Any]]) -> str:
    """
    Formats retrieved knowledge into a strict, bounded context block for the LLM prompt.
    """
    if not entries:
        return "No specific curated reference entry found. Rely strictly on universal general public health precautions."

    formatted = []
    for e in entries:
        topic = e.get("topic", "General")
        info = " ".join(e.get("general_information", []))
        self_care = "; ".join(e.get("self_care", []))
        warning_signs = "; ".join(e.get("warning_signs", []))
        when_care = "; ".join(e.get("when_to_seek_care", []))
        src = e.get("source", "Authoritative Public Health Source")
        
        block = (
            f"--- TOPIC: {topic} (Source: {src}) ---\n"
            f"Facts: {info}\n"
            f"Verified Self-Care: {self_care}\n"
            f"Warning Signs: {warning_signs}\n"
            f"When to Seek Care: {when_care}\n"
        )
        formatted.append(block)

    return "\n".join(formatted)
