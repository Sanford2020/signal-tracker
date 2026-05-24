import pytest
from pydantic import ValidationError

from app.core.config import Settings


def test_allowed_origins_accepts_comma_separated_env_value() -> None:
    settings = Settings(allowed_origins="https://app.example.com, http://localhost:3000")

    assert settings.allowed_origin_list == ["https://app.example.com", "http://localhost:3000"]


def test_allowed_origins_accepts_json_env_value() -> None:
    settings = Settings(allowed_origins='["https://app.example.com","https://admin.example.com"]')

    assert settings.allowed_origin_list == ["https://app.example.com", "https://admin.example.com"]


def test_database_url_normalizes_render_postgres_scheme() -> None:
    settings = Settings(database_url="postgresql://user:pass@host:5432/db")

    assert settings.database_url == "postgresql+psycopg://user:pass@host:5432/db"


def test_production_rejects_default_database_credentials() -> None:
    with pytest.raises(ValidationError, match="Production DATABASE_URL"):
        Settings(
            app_env="production",
            allowed_origins="https://app.example.com",
            admin_api_key="secret",
        )


def test_production_rejects_wildcard_origins() -> None:
    with pytest.raises(ValidationError, match="Production ALLOWED_ORIGINS"):
        Settings(
            app_env="production",
            database_url="postgresql+psycopg://prod_user:prod_pass@db.example.com:5432/signal_tracker",
            allowed_origins="*",
            admin_api_key="secret",
        )


def test_production_requires_admin_api_key() -> None:
    with pytest.raises(ValidationError, match="Production ADMIN_API_KEY"):
        Settings(
            app_env="production",
            database_url="postgresql+psycopg://prod_user:prod_pass@db.example.com:5432/signal_tracker",
            allowed_origins="https://app.example.com",
        )


def test_production_accepts_explicit_origins_and_non_default_database() -> None:
    settings = Settings(
        app_env="production",
        database_url="postgresql+psycopg://prod_user:prod_pass@db.example.com:5432/signal_tracker",
        allowed_origins="https://app.example.com",
        admin_api_key="secret",
    )

    assert settings.app_env == "production"
    assert settings.allowed_origin_list == ["https://app.example.com"]
