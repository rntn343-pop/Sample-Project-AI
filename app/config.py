from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent
ENV_FILE = BASE_DIR / ".env"
load_dotenv(ENV_FILE, override=True)


def _csv(value: str) -> list[str]:
    return [item.strip() for item in value.split(",") if item.strip()]


def _bool_env(name: str, default: bool = False) -> bool:
    value = os.getenv(name)
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "y", "on"}


def _float_env(name: str, default: float) -> float:
    try:
        return float(os.getenv(name, str(default)).strip())
    except ValueError:
        return default


def _int_env(name: str, default: int) -> int:
    try:
        return int(os.getenv(name, str(default)).strip())
    except ValueError:
        return default


@dataclass(frozen=True)
class Settings:
    app_name: str = os.getenv("APP_NAME", "PocketSmart AI")
    secret_key: str = os.getenv("SECRET_KEY", "dev-only-secret-change-me-please-32-bytes-minimum")
    database_url: str = os.getenv("DATABASE_URL", "sqlite:///./data/pocketsmart.db")
    gemini_api_key: str = os.getenv("GEMINI_API_KEY", "").strip()
    gemini_model: str = os.getenv("GEMINI_MODEL", "gemini-3.8-flash").strip()
    gemini_temperature: float = _float_env("GEMINI_TEMPERATURE", 0.4)
    gemini_max_output_tokens: int = _int_env("GEMINI_MAX_OUTPUT_TOKENS", 4500)
    gemini_debug: bool = _bool_env("GEMINI_DEBUG", False)
    gemini_fallback_on_error: bool = _bool_env("GEMINI_FALLBACK_ON_ERROR", False)
    session_max_age_seconds: int = _int_env("SESSION_MAX_AGE_SECONDS", 1800)
    max_upload_mb: int = _int_env("MAX_UPLOAD_MB", 5)
    cookie_secure: bool = _bool_env("COOKIE_SECURE", False)
    cors_origins: tuple[str, ...] = tuple(
        _csv(
            os.getenv(
                "CORS_ORIGINS",
                "http://127.0.0.1:8000,http://localhost:8000",
            )
        )
    )
    upload_dir: Path = BASE_DIR / "uploads"
    data_dir: Path = BASE_DIR / "data"


settings = Settings()
settings.upload_dir.mkdir(parents=True, exist_ok=True)
settings.data_dir.mkdir(parents=True, exist_ok=True)