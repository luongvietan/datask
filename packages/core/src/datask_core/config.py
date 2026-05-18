from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # App
    app_env: str = Field(default="development", alias="APP_ENV")
    app_secret_key: str = Field(default="change-me-in-production", alias="APP_SECRET_KEY")
    base_url: str = Field(default="https://datask.run", alias="BASE_URL")

    # Database
    database_url: str = Field(default="postgresql+asyncpg://datask:datask@localhost:5432/datask", alias="DATABASE_URL")

    # Redis
    redis_url: str = Field(default="redis://localhost:6379/0", alias="REDIS_URL")

    # Stripe
    stripe_secret_key: str = Field(default="", alias="STRIPE_SECRET_KEY")
    stripe_webhook_secret: str = Field(default="", alias="STRIPE_WEBHOOK_SECRET")
    stripe_price_payg_id: str = Field(default="", alias="STRIPE_PRICE_PAYG_ID")

    # OpenAI (Layer 3)
    openai_api_key: str = Field(default="", alias="OPENAI_API_KEY")
    openai_model: str = Field(default="gpt-4o-mini", alias="OPENAI_MODEL")

    # Proxy
    brightdata_proxy_url: str = Field(default="", alias="BRIGHTDATA_PROXY_URL")

    # Rate limits
    free_tier_monthly_quota: int = Field(default=500, alias="FREE_TIER_MONTHLY_QUOTA")
    free_tier_concurrent: int = Field(default=2, alias="FREE_TIER_CONCURRENT")
    free_tier_burst_per_minute: int = Field(default=10, alias="FREE_TIER_BURST_PER_MINUTE")

    # Worker
    worker_concurrency: int = Field(default=4, alias="WORKER_CONCURRENCY")
    job_timeout_seconds: int = Field(default=60, alias="JOB_TIMEOUT_SECONDS")

    @property
    def is_production(self) -> bool:
        return self.app_env == "production"


@lru_cache
def get_settings() -> Settings:
    return Settings()
