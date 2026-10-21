from functools import lru_cache

from pydantic import model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=(".env", "../.env"), extra="ignore")

    app_env: str = "dev"
    log_level: str = "INFO"
    cors_origins: str = "http://localhost:3000"

    ocr_provider: str = "mock"  # gemma | gemini | mock | rapidocr | handwriting
    gemma_base_url: str = "http://localhost:11434/v1"
    gemma_model: str = "gemma4:e4b"  # Ollama tag for Gemma 4 E4B (vision). Override if your runtime differs.
    gemma_api_key: str = ""

    gemini_api_key: str = ""
    gemini_model: str = "gemini-3.5-flash-lite"
    gemini_base_url: str = "https://generativelanguage.googleapis.com/v1beta"

    ocr_max_bytes: int = 5 * 1024 * 1024
    ocr_max_pixels: int = 25_000_000
    ocr_timeout_seconds: float = 20.0
    ocr_rate_limit_per_minute: int = 10
    trust_proxy: bool = False

    data_dir: str = "data"

    @property
    def cors_origin_list(self) -> list[str]:
        return [o.strip() for o in self.cors_origins.split(",") if o.strip()]

    @property
    def is_prod(self) -> bool:
        return self.app_env.lower() == "prod"

    @model_validator(mode="after")
    def _no_wildcard_cors_in_prod(self) -> "Settings":
        if self.is_prod and "*" in self.cors_origin_list:
            raise ValueError("CORS_ORIGINS must not contain '*' in prod")
        return self


@lru_cache
def get_settings() -> Settings:
    return Settings()
