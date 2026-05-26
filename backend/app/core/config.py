import json
import secrets
from functools import lru_cache

from pydantic import field_validator, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


DEFAULT_DATABASE_URL = (
    "postgresql+psycopg://signal_tracker:signal_tracker@localhost:5432/signal_tracker"
)
DEFAULT_ALLOWED_ORIGINS = "http://localhost:3000,http://127.0.0.1:3000,http://localhost:3001,http://127.0.0.1:3001"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    app_name: str = "Signal Tracker API"
    app_env: str = "development"
    app_version: str = "0.1.0"
    api_v1_prefix: str = "/api/v1"
    allowed_origins: str = DEFAULT_ALLOWED_ORIGINS
    log_level: str = "INFO"
    admin_api_key: str | None = None
    admin_rate_limit_per_minute: int = 30

    database_url: str = DEFAULT_DATABASE_URL
    redis_url: str = "redis://localhost:6379/0"
    celery_broker_url: str = "redis://localhost:6379/0"
    celery_result_backend: str = "redis://localhost:6379/1"

    ai_extraction_mode: str = "mock"
    ai_api_key: str | None = None
    ai_model: str = "mock"
    ai_base_url: str | None = None

    lifecycle_dormancy_days: int = 14
    source_check_interval_seconds: int = 900
    lifecycle_worker_interval_seconds: int = 3600
    notification_delivery_interval_seconds: int = 300
    github_api_token: str | None = None
    github_provider_max_repositories: int = 3
    github_provider_max_releases_per_repo: int = 2
    github_provider_max_activity_items_per_repo: int = 2
    github_provider_timeout_seconds: float = 10.0
    rss_feed_urls: str = ""
    rss_provider_max_entries_per_feed: int = 20
    rss_provider_timeout_seconds: float = 10.0
    hacker_news_provider_max_hits: int = 10
    hacker_news_provider_timeout_seconds: float = 10.0
    hacker_news_provider_tags: str = "story"

    alert_opportunity_threshold: float = 7.0
    alert_credibility_increase_min: float = 2.0
    alert_risk_threshold: float = 7.0
    alert_heat_spike_min: float = 2.0

    usage_ai_extraction_monthly_limit: int = 10000
    usage_source_check_monthly_limit: int = 100000

    @field_validator("database_url", mode="before")
    @classmethod
    def normalize_database_url(cls, value: object) -> object:
        if isinstance(value, str) and value.startswith("postgresql://"):
            return value.replace("postgresql://", "postgresql+psycopg://", 1)
        return value

    @property
    def allowed_origin_list(self) -> list[str]:
        raw_value = self.allowed_origins.strip()
        if raw_value.startswith("["):
            return json.loads(raw_value)

        return [origin.strip() for origin in raw_value.split(",") if origin.strip()]

    @property
    def rss_feed_url_list(self) -> list[str]:
        raw_value = self.rss_feed_urls.strip()
        if not raw_value:
            return []
        if raw_value.startswith("["):
            return [str(item).strip() for item in json.loads(raw_value) if str(item).strip()]
        return [item.strip() for item in raw_value.split(",") if item.strip()]

    @model_validator(mode="after")
    def validate_production_settings(self) -> "Settings":
        if self.app_env.lower() != "production":
            return self

        if self.database_url == DEFAULT_DATABASE_URL or "signal_tracker:signal_tracker" in self.database_url:
            raise ValueError("Production DATABASE_URL must not use the default local credentials.")

        if not self.allowed_origin_list or "*" in self.allowed_origin_list:
            raise ValueError("Production ALLOWED_ORIGINS must list explicit trusted origins.")

        if not self.admin_api_key:
            raise ValueError("Production ADMIN_API_KEY is required for bootstrap/admin operations.")

        return self


def verify_admin_secret(provided_secret: str | None, settings: Settings) -> bool:
    if settings.app_env.lower() != "production":
        return True
    if not settings.admin_api_key or not provided_secret:
        return False
    return secrets.compare_digest(provided_secret, settings.admin_api_key)


@lru_cache
def get_settings() -> Settings:
    return Settings()
