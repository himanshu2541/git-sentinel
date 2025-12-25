from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    APP_NAME: str = "Git Sentinel"
    ENV: str = "development"  # or "production"
    DEBUG: bool = ENV == "development"
    LOG_LEVEL: str = "DEBUG" if DEBUG else "INFO"
    
    REDIS_URL: str = "redis://localhost:6379/0"

    # GitHub Tokens
    GITHUB_API_TOKEN: str = ""
    WEBHOOK_SECRET: str = ""



settings = Settings()