from typing import Any, Literal

from pydantic import BaseModel


Confidence = Literal["HIGH", "MEDIUM", "LOW"]


class PersonalizeResponse(BaseModel):
    answer: str
    confidence: Confidence
    sourcesUsed: list[str]


class DebugPersonalizationResponse(BaseModel):
    intent: str
    selectedContext: list[str]
    excludedContext: list[str]
    language: str
    tone: str
    maxWords: int
    availableSources: list[str]
    failedSources: list[str]
    modifiers: list[str] = []
    confidence: Confidence
    confidenceFactors: dict[str, Any] = {}
