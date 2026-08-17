from functools import lru_cache
import os
from pathlib import Path
from typing import Self


def load_dotenv_file(path: Path) -> None:
    if not path.exists():
        return
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        os.environ.setdefault(key.strip(), value.strip().strip('"').strip("'"))


class Settings:
    app_env: str
    mock_service_base_url: str
    personalization_config_path: Path
    prompt_templates_path: Path
    llm_provider: str
    llm_model: str
    llm_base_url: str
    openrouter_api_key: str | None
    llm_api_key: str | None
    llm_timeout_seconds: float
    cors_origins: list[str]
    mongo_uri: str | None
    mongo_database: str
    auth_secret: str
    stripe_secret_key: str | None
    stripe_weekly_price_id: str | None
    stripe_monthly_price_id: str | None
    stripe_yearly_price_id: str | None
    frontend_base_url: str

    def __init__(self) -> None:
        backend_root = Path(__file__).resolve().parents[2]
        load_dotenv_file(backend_root / ".env")
        self.app_env = os.getenv("APP_ENV", "local")
        self.mock_service_base_url = os.getenv("MOCK_SERVICE_BASE_URL", "http://127.0.0.1:8000")
        self.personalization_config_path = Path(
            os.getenv("PERSONALIZATION_CONFIG_PATH", str(backend_root / "configs" / "personalization_rules.json"))
        )
        self.prompt_templates_path = Path(
            os.getenv("PROMPT_TEMPLATES_PATH", str(backend_root / "configs" / "prompt_templates.json"))
        )
        self.llm_provider = os.getenv("LLM_PROVIDER", "mock").lower()
        self.llm_model = os.getenv("LLM_MODEL", "mock-mynaksh")
        self.llm_base_url = os.getenv("LLM_BASE_URL", "http://localhost:1234/v1")
        self.openrouter_api_key = os.getenv("OPENROUTER_API_KEY")
        self.llm_api_key = os.getenv("LLM_API_KEY")
        self.llm_timeout_seconds = float(os.getenv("LLM_TIMEOUT_SECONDS", "30"))
        origins = os.getenv("CORS_ORIGINS", "http://localhost:5173,http://127.0.0.1:5173")
        self.cors_origins = [origin.strip() for origin in origins.split(",") if origin.strip()]
        self.mongo_uri = os.getenv("MONGO_URI")
        self.mongo_database = os.getenv("MONGO_DATABASE", "mynaksh_poc")
        self.auth_secret = os.getenv("AUTH_SECRET", "dev-only-change-me")
        self.stripe_secret_key = os.getenv("STRIPE_SECRET_KEY")
        self.stripe_weekly_price_id = os.getenv("STRIPE_WEEKLY_PRICE_ID")
        self.stripe_monthly_price_id = os.getenv("STRIPE_MONTHLY_PRICE_ID")
        self.stripe_yearly_price_id = os.getenv("STRIPE_YEARLY_PRICE_ID")
        self.frontend_base_url = os.getenv("FRONTEND_BASE_URL", "http://127.0.0.1:5173")

    def with_overrides(self, *, llm_provider: str | None = None, llm_model: str | None = None) -> Self:
        clone = Settings.__new__(Settings)
        clone.__dict__.update(self.__dict__)
        if llm_provider:
            clone.llm_provider = llm_provider.lower()
        if llm_model:
            clone.llm_model = llm_model
        return clone


@lru_cache
def get_settings() -> Settings:
    return Settings()
