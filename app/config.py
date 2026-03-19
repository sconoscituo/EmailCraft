from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    app_name: str = "EmailCraft"
    debug: bool = False
    database_url: str = "sqlite+aiosqlite:///./emailcraft.db"
    secret_key: str = "change-me-in-production"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 60 * 24 * 7
    gemini_api_key: str = ""
    free_daily_limit: int = 5
    premium_monthly_price: int = 9900

    class Config:
        env_file = ".env"


@lru_cache
def get_settings() -> Settings:
    return Settings()
