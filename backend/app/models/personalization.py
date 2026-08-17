from typing import Any, Literal

from pydantic import BaseModel

from app.models.responses import Confidence


class ContextItem(BaseModel):
    label: str
    source_path: str
    value: Any
    priority: Literal["primary", "secondary"]


class PersonalizationPlan(BaseModel):
    intent: str
    modifiers: list[str]
    language: str
    tone: str
    max_words: int
    selected_context: list[ContextItem]
    excluded_context: list[str]
    sources_used: list[str]
    failed_sources: list[str]
    available_sources: list[str]
    confidence: Confidence
    confidence_factors: dict[str, Any]
    safety_note: str | None = None
