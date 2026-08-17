import json

from app.models.personalization import PersonalizationPlan
from app.personalization.config_loader import load_prompt_templates


class PromptBuilder:
    def __init__(self) -> None:
        self.templates = load_prompt_templates()

    def build(self, question: str, plan: PersonalizationPlan) -> str:
        context_lines = []
        remaining_context_chars = int(self.templates.get("max_context_chars", 1200))
        for item in plan.selected_context:
            value_text = format_context_value(item.value)
            if len(value_text) > remaining_context_chars:
                value_text = value_text[: max(0, remaining_context_chars - 3)].rstrip() + "..."
            context_lines.append(f"- {item.label}: {value_text}")
            remaining_context_chars -= len(value_text)
            if remaining_context_chars <= 0:
                break

        safety = f"\nSafety note: {plan.safety_note}\n" if plan.safety_note else ""
        excluded = ", ".join(plan.excluded_context) if plan.excluded_context else "None"

        return (
            f"{self.templates['system'].strip()}\n"
            f"{safety}\n"
            "Response preferences:\n"
            f"- Language: {plan.language}\n"
            f"- Tone: {plan.tone}\n"
            f"- Max words: {plan.max_words}\n"
            f"- Detected intent: {plan.intent}\n\n"
            f"User question:\n{question}\n\n"
            "Selected context:\n"
            f"{chr(10).join(context_lines) if context_lines else '- No selected context available.'}\n\n"
            f"Excluded context labels: {excluded}\n\n"
            "Grounding rules:\n"
            "- Use only selected context.\n"
            "- Do not invent astrology details not present in selected context.\n"
            "- Mention uncertainty when selected context is incomplete.\n\n"
            f"{self.templates['json_instruction'].strip()}\n"
        )


def format_context_value(value) -> str:
    if isinstance(value, dict):
        return json.dumps(value, ensure_ascii=False, separators=(",", ":"))
    return str(value)
