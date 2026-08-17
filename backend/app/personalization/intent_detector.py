import re
from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class IntentResult:
    intent: str
    modifiers: list[str]
    scores: dict[str, int]


class IntentDetector:
    def __init__(self, rules: dict[str, Any]) -> None:
        self.rules = rules

    def detect(self, question: str) -> IntentResult:
        normalized = self._normalize(question)
        scores: dict[str, int] = {}

        for intent, config in self.rules["intents"].items():
            score = 0
            for keyword in config.get("keywords", []):
                if self._keyword_matches(normalized, keyword):
                    score += 1
            scores[intent] = score

        best_intent = max(scores, key=scores.get)
        if scores[best_intent] == 0:
            best_intent = "general"

        modifiers = self._detect_modifiers(normalized)
        return IntentResult(intent=best_intent, modifiers=modifiers, scores=scores)

    def _detect_modifiers(self, normalized_question: str) -> list[str]:
        modifiers = []
        for modifier, config in self.rules.get("intent_modifiers", {}).items():
            if any(self._keyword_matches(normalized_question, keyword) for keyword in config.get("keywords", [])):
                modifiers.append(modifier)
        return modifiers

    @staticmethod
    def _normalize(text: str) -> str:
        return re.sub(r"\s+", " ", text.lower()).strip()

    @staticmethod
    def _keyword_matches(text: str, keyword: str) -> bool:
        keyword = keyword.lower().strip()
        if " " in keyword:
            return keyword in text
        return re.search(rf"\b{re.escape(keyword)}\b", text) is not None
