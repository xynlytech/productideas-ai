from functools import lru_cache

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_url: str = "postgresql+asyncpg://productideas:productideas_dev@localhost:5432/productideas"
    database_url_sync: str = "postgresql://productideas:productideas_dev@localhost:5432/productideas"
    redis_url: str = "redis://localhost:6379/0"
    secret_key: str = "dev-secret-key-change-in-production"
    cors_origins: str = "http://localhost:3000"
    access_token_expire_minutes: int = 30
    refresh_token_expire_days: int = 7

    s3_bucket: str = "productideas-exports"
    s3_endpoint: str | None = None
    s3_access_key: str = ""
    s3_secret_key: str = ""

    google_trends_api_key: str = ""

    sentry_dsn: str = ""
    posthog_api_key: str = ""
    environment: str = "development"

    model_config = {"env_file": ".env", "extra": "ignore"}


@lru_cache
def get_settings() -> Settings:
    return Settings()
