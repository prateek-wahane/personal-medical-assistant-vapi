from __future__ import annotations

from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Personal Medical Assistant"
    app_env: str = "dev"
    app_host: str = "0.0.0.0"
    app_port: int = 8000
    json_logs: bool = False

    database_url: str = "sqlite:///./medical_assistant.db"
    database_pool_size: int = 5
    database_max_overflow: int = 10
    database_pool_timeout: int = 30
    database_pool_recycle_seconds: int = 1800

    upload_dir: str = "./uploads"
    timezone: str = "Asia/Kolkata"

    max_upload_size_mb: int = 10
    allowed_upload_extensions: str = ".pdf,.txt,.csv"
    cors_allowed_origins: str = "http://localhost:3000,http://localhost:8000,http://127.0.0.1:8000"

    auth_secret_key: str = "change-me-in-production"
    auth_secret_key_file: str | None = None
    auth_token_exp_minutes: int = 60 * 24

    google_client_secrets_file: str = "./credentials/google_client_secret.json"
    google_token_file: str = "./credentials/google_token.json"
    google_calendar_id: str = "primary"

    vapi_api_key: str | None = None
    vapi_public_key: str | None = None
    vapi_assistant_id: str | None = None
    vapi_webhook_secret: str | None = None
    vapi_webhook_secret_file: str | None = None
    public_base_url: str = "http://localhost:8000"

    ocr_enabled: bool = False
    ocr_command: str = "ocrmypdf"
    ocr_language: str = "eng"
    ocr_timeout_seconds: int = 120
    ocr_min_extracted_chars: int = 80
    ocr_force: bool = False

    request_id_header_name: str = "x-request-id"
    rate_limit_auth_per_minute: int = 20
    rate_limit_upload_per_minute: int = 10
    rate_limit_vapi_per_minute: int = 120

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

    @property
    def is_postgres(self) -> bool:
        return self.database_url.startswith("postgresql")

    def _read_secret_file(self, path_value: str | None) -> str | None:
        if not path_value:
            return None
        path = Path(path_value)
        if not path.exists():
            return None
        return path.read_text(encoding="utf-8").strip() or None

    @property
    def resolved_auth_secret_key(self) -> str:
        return self._read_secret_file(self.auth_secret_key_file) or self.auth_secret_key

    @property
    def resolved_vapi_webhook_secret(self) -> str | None:
        return self._read_secret_file(self.vapi_webhook_secret_file) or self.vapi_webhook_secret


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()
