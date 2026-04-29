"""
config/settings.py
──────────────────
Centralized configuration using pydantic-settings.
All secrets loaded from environment variables / .env file.
Never hardcode secrets — always use this module.
"""

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # ── Telegram ────────────────────────────────────────────────────────────
    TELEGRAM_BOT_TOKEN: str

    # ── Google OAuth 2.0 ────────────────────────────────────────────────────
    GOOGLE_CLIENT_ID: str
    GOOGLE_CLIENT_SECRET: str
    OAUTH_REDIRECT_URI: str = "https://your-domain.com/oauth/callback"

    # ── App ─────────────────────────────────────────────────────────────────
    LOG_LEVEL: str = "INFO"
    TIMEZONE: str = "Asia/Riyadh"   # Default timezone for Saudi users
    ENV: str = "development"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
