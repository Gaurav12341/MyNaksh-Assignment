from app.llm.base import LLMResult


class MockLLMProvider:
    async def generate(self, prompt: str, *, model: str, max_tokens: int) -> LLMResult:
        answer = (
            "Based on the selected MyNaksh context, this looks like a period for thoughtful action rather than a rushed "
            "decision. The available indicators suggest that opportunities can improve through networking and practical "
            "conversations, while timing factors should be treated as guidance rather than certainty. Use the next few "
            "months to compare options, strengthen your profile, and move when the role clearly improves your growth."
        )
        return LLMResult(answer=answer, confidence="MEDIUM", raw='{"answer": "...", "confidence": "MEDIUM"}')
