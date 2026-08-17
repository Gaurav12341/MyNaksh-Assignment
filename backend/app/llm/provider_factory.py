from app.core.config import Settings, get_settings
from app.llm.base import LLMProvider
from app.llm.mock import MockLLMProvider
from app.llm.openai_compatible import OpenAICompatibleProvider
from app.llm.openrouter import OpenRouterProvider


def create_llm_provider(settings: Settings | None = None) -> LLMProvider:
    settings = settings or get_settings()
    if settings.llm_provider == "openrouter":
        return OpenRouterProvider(settings)
    if settings.llm_provider in {"lmstudio", "openai_compatible"}:
        return OpenAICompatibleProvider(settings)
    return MockLLMProvider()
