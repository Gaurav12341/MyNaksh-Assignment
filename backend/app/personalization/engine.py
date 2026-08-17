from typing import Any

from app.models.context import UserContextBundle
from app.models.personalization import ContextItem, PersonalizationPlan
from app.personalization.confidence import score_confidence
from app.personalization.config_loader import load_personalization_rules
from app.personalization.intent_detector import IntentDetector


class PersonalizationEngine:
    def __init__(self, rules: dict[str, Any] | None = None) -> None:
        self.rules = rules or load_personalization_rules()
        self.intent_detector = IntentDetector(self.rules)

    def build_plan(self, question: str, bundle: UserContextBundle) -> PersonalizationPlan:
        intent_result = self.intent_detector.detect(question)
        intent_config = self.rules["intents"][intent_result.intent]
        user = bundle.user.data or {}

        selected_context = self._select_context(intent_config, bundle.as_resolver_data())
        confidence, confidence_factors = score_confidence(bundle, selected_context)

        language = self._resolve_language(user.get("language"))
        tone = self._resolve_tone(user.get("tonePreference"))
        max_words = self._resolve_max_words(user, intent_config)
        sources_used = [item.label for item in selected_context]

        return PersonalizationPlan(
            intent=intent_result.intent,
            modifiers=intent_result.modifiers,
            language=language,
            tone=tone,
            max_words=max_words,
            selected_context=selected_context,
            excluded_context=list(intent_config.get("exclude", [])),
            sources_used=sources_used,
            failed_sources=bundle.failed_sources,
            available_sources=bundle.available_sources,
            confidence=confidence,
            confidence_factors=confidence_factors | {"intentScores": intent_result.scores},
            safety_note=intent_config.get("response", {}).get("safety_note"),
        )

    def _select_context(self, intent_config: dict[str, Any], data: dict[str, Any]) -> list[ContextItem]:
        selected: list[ContextItem] = []
        for priority, key in [("primary", "primary_context"), ("secondary", "secondary_context")]:
            for entry in intent_config.get(key, []):
                source_path = entry["source"]
                value = resolve_path(data, source_path)
                if value is None or value == {} or value == "":
                    continue
                selected.append(
                    ContextItem(
                        label=entry["label"],
                        source_path=source_path,
                        value=value,
                        priority=priority,
                    )
                )
        return selected

    def _resolve_language(self, language_code: str | None) -> str:
        return self.rules.get("languages", {}).get(language_code or "en", "English")

    def _resolve_tone(self, tone_preference: str | None) -> str:
        return self.rules.get("tones", {}).get(tone_preference or "calm", "Calm")

    def _resolve_max_words(self, user: dict[str, Any], intent_config: dict[str, Any]) -> int:
        default_words = int(intent_config.get("response", {}).get("default_max_words", 200))
        subscription = user.get("subscription", "free")
        cap = int(self.rules.get("subscriptions", {}).get(subscription, {}).get("max_words_cap", 160))
        return min(default_words, cap)


def resolve_path(data: dict[str, Any], path: str) -> Any | None:
    current: Any = data
    for part in path.split("."):
        if isinstance(current, dict) and part in current:
            current = current[part]
        else:
            return None
    return current
