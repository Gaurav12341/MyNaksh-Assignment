import json

import httpx

from app.core.config import Settings
from app.llm.base import LLMResult


class OpenAICompatibleProvider:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings

    async def generate(self, prompt: str, *, model: str, max_tokens: int) -> LLMResult:
        headers = {"Content-Type": "application/json"}
        if self.settings.llm_api_key:
            headers["Authorization"] = f"Bearer {self.settings.llm_api_key}"

        payload = {
            "model": model,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.4,
            "max_tokens": max_tokens,
        }

        async with httpx.AsyncClient(timeout=self.settings.llm_timeout_seconds) as client:
            response = await client.post(
                f"{self.settings.llm_base_url.rstrip('/')}/chat/completions",
                headers=headers,
                json=payload,
            )
            response.raise_for_status()
            data = response.json()

        content = data["choices"][0]["message"]["content"]
        return parse_llm_content(content)


def parse_llm_content(content: str) -> LLMResult:
    raw = content
    cleaned = content.strip()
    if cleaned.startswith("```"):
        cleaned = cleaned.strip("`")
        if cleaned.lower().startswith("json"):
            cleaned = cleaned[4:].strip()
    try:
        parsed = json.loads(cleaned)
        answer = str(parsed.get("answer", "")).strip()
        confidence = str(parsed.get("confidence", "")).upper().strip() or None
        if answer:
            return LLMResult(answer=answer, confidence=confidence, raw=raw)
    except json.JSONDecodeError:
        pass
    return LLMResult(answer=content.strip(), confidence=None, raw=raw)
