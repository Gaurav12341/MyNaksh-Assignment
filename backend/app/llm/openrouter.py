import httpx

from app.core.config import Settings
from app.llm.base import LLMResult
from app.llm.openai_compatible import parse_llm_content


class OpenRouterProvider:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings

    async def generate(self, prompt: str, *, model: str, max_tokens: int) -> LLMResult:
        if not self.settings.openrouter_api_key:
            raise RuntimeError("OPENROUTER_API_KEY is not configured")

        payload = {
            "model": model,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.4,
            "max_tokens": max_tokens,
        }
        headers = {
            "Authorization": f"Bearer {self.settings.openrouter_api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "http://localhost:5173",
            "X-Title": "MyNaksh Assessment POC",
        }

        async with httpx.AsyncClient(timeout=self.settings.llm_timeout_seconds) as client:
            response = await client.post("https://openrouter.ai/api/v1/chat/completions", headers=headers, json=payload)
            response.raise_for_status()
            data = response.json()

        content = data["choices"][0]["message"]["content"]
        return parse_llm_content(content)
