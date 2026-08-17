from functools import lru_cache
import json
from typing import Any

from app.core.config import get_settings


@lru_cache
def load_personalization_rules() -> dict[str, Any]:
    settings = get_settings()
    with settings.personalization_config_path.open("r", encoding="utf-8") as file:
        return json.load(file)


@lru_cache
def load_prompt_templates() -> dict[str, str]:
    settings = get_settings()
    with settings.prompt_templates_path.open("r", encoding="utf-8") as file:
        return json.load(file)
