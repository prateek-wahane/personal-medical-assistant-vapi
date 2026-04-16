from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Personal Medical Assistant"
    app_env: str = "dev"
    app_host: str = "0.0.0.0"
    app_port: int = 8000

    database_url: str = "sqlite:///./medical_assistant.db"
    upload_dir: str = "./uploads"
    timezone: str = "Asia/Kolkata"

    max_upload_size_mb: int = 10
    allowed_upload_extensions: str = ".pdf,.txt,.csv"
    cors_allowed_origins: str = "http://localhost:3000,http://localhost:8000,http://127.0.0.1:8000"

    auth_secret_key: str = "change-me-in-production"
    auth_token_exp_minutes: int = 60 * 24

    google_client_secrets_file: str = "./credentials/google_client_secret.json"
    google_token_file: str = "./credentials/google_token.json"
    google_calendar_id: str = "primary"

    vapi_api_key: str | None = None
    vapi_public_key: str | None = None
    vapi_assistant_id: str | None = None
    vapi_webhook_secret: str | None = None
    public_base_url: str = "http://localhost:8000"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    @property
    def cors_origins(self) -> list[str]:
        return [origin.strip() for origin in self.cors_allowed_origins.split(",") if origin.strip()]

    @property
    def allowed_extensions(self) -> set[str]:
        return {ext.strip().lower() for ext in self.allowed_upload_extensions.split(",") if ext.strip()}


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()
