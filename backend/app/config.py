from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    database_url: str = "postgresql://devlog:devlog@localhost:5432/devlog"

    secret_key: str = "dev-only-insecure-secret-change-me"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30

    cors_origins: list[str] = ["http://localhost:5173"]

    # AI / LangChain
    llm_provider: str = "groq"  # groq | openai | anthropic
    llm_model: str = "llama-3.3-70b-versatile"
    groq_api_key: str = ""


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
