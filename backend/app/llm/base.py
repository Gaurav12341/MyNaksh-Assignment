from dataclasses import dataclass
from typing import Protocol


@dataclass(frozen=True)
class LLMResult:
    answer: str
    confidence: str | None = None
    raw: str | None = None


class LLMProvider(Protocol):
    async def generate(self, prompt: str, *, model: str, max_tokens: int) -> LLMResult:
        ...
