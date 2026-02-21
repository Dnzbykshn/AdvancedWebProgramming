"""Application configuration using Pydantic Settings."""

from pydantic_settings import BaseSettings
from pathlib import Path


class Settings(BaseSettings):
    """Application settings loaded from .env file."""

    GEMINI_API_KEY: str
    RESEND_API_KEY: str
    NTFY_TOPIC: str = "deniz-career-agent"
    FROM_EMAIL: str = "onboarding@resend.dev"
    NOTIFY_EMAIL: str = "buyuksahin.dnz@gmail.com"
    EVALUATOR_THRESHOLD: int = 7
    MAX_REVISION_ATTEMPTS: int = 3

    model_config = {
        "env_file": str(Path(__file__).resolve().parent.parent / ".env"),
        "env_file_encoding": "utf-8",
    }


settings = Settings()
