"""
llm/schema.py - Strict Pydantic and JSON schema for LLM health guidance output.
"""
from typing import List, Literal
from pydantic import BaseModel, Field, field_validator

TriageLevelType = Literal["self_care", "doctor_2_3_days", "doctor_today", "emergency"]
UncertaintyType = Literal["low", "moderate", "high"]


class HealthGuidanceOutput(BaseModel):
    triage_level: TriageLevelType = Field(
        ...,
        description="The recommended informational triage urgency level."
    )
    summary: str = Field(
        ...,
        max_length=350,
        description="Short informational summary of the symptoms and situation."
    )
    reasons: List[str] = Field(
        default_factory=list,
        max_length=4,
        description="Concise reasons explaining the informational assessment (maximum 4)."
    )
    self_care_tips: List[str] = Field(
        default_factory=list,
        max_length=5,
        description="Non-pharmacological self-care and comfort measures (maximum 5)."
    )
    warning_signs: List[str] = Field(
        default_factory=list,
        max_length=5,
        description="Specific warning signs that warrant immediate clinical escalation (maximum 5)."
    )
    follow_up_questions: List[str] = Field(
        default_factory=list,
        max_length=3,
        description="Relevant follow-up questions to clarify missing health information (maximum 3)."
    )
    not_assessed: List[str] = Field(
        default_factory=list,
        description="Explicit statements of what cannot be determined from the available input."
    )
    source_topics: List[str] = Field(
        default_factory=list,
        description="Names of public health topics and sources referenced."
    )
    uncertainty: UncertaintyType = Field(
        ...,
        description="Level of clinical and informational uncertainty ('low', 'moderate', or 'high')."
    )

    @field_validator("reasons")
    @classmethod
    def limit_reasons(cls, v: List[str]) -> List[str]:
        return v[:4]

    @field_validator("self_care_tips")
    @classmethod
    def limit_tips(cls, v: List[str]) -> List[str]:
        return v[:5]

    @field_validator("warning_signs")
    @classmethod
    def limit_warning_signs(cls, v: List[str]) -> List[str]:
        return v[:5]

    @field_validator("follow_up_questions")
    @classmethod
    def limit_questions(cls, v: List[str]) -> List[str]:
        return v[:3]
