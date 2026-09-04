import os
import json
from typing import List
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), ".env"))

# Backend papkasining absolute pathi (config.py joylashgan: backend/app/config.py)
BACKEND_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DEFAULT_SQLITE_PATH = os.path.join(BACKEND_DIR, "school_assistant.db")


def _parse_cors_list():
    raw = os.getenv("CORS_ORIGINS", "")
    if not raw:
        return ["http://localhost:5173", "http://localhost:3000"]
    try:
        parsed = json.loads(raw)
        if isinstance(parsed, list):
            return parsed
    except json.JSONDecodeError:
        pass
    return [s.strip() for s in raw.split(",")]


class Settings(BaseSettings):
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL",
        f"sqlite+aiosqlite:///{DEFAULT_SQLITE_PATH}",
    )
    JWT_SECRET: str = os.getenv("JWT_SECRET", "change-me-in-production")
    JWT_ALGORITHM: str = os.getenv("JWT_ALGORITHM", "HS256")
    JWT_EXPIRE_MINUTES: int = int(os.getenv("JWT_EXPIRE_MINUTES", "1440"))
    BOT_TOKEN: str = os.getenv("BOT_TOKEN", "")
    TELEGRAM_BOT_TOKEN: str = os.getenv("TELEGRAM_BOT_TOKEN", "")
    GOOGLE_MAPS_API_KEY: str = os.getenv("GOOGLE_MAPS_API_KEY", "")
    FIREBASE_CREDENTIALS: str = os.getenv("FIREBASE_CREDENTIALS", "")
    SMS_API_KEY: str = os.getenv("SMS_API_KEY", "")
    SMS_API_URL: str = os.getenv("SMS_API_URL", "")
    CORS_ORIGINS: List[str] = _parse_cors_list()
    DEFAULT_SCHOOL_START_TIME: str = os.getenv(
        "DEFAULT_SCHOOL_START_TIME", "08:00"
    )
    SUPER_ADMIN_PHONE: str = os.getenv("SUPER_ADMIN_PHONE", "+998901234567")
    SUPER_ADMIN_TELEGRAM_ID: str = os.getenv(
        "SUPER_ADMIN_TELEGRAM_ID", ""
    )
    WEBAPP_URL: str = os.getenv(
        "WEBAPP_URL", "http://localhost:5173"
    )
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
