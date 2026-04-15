from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Personal Medical Assistant"
    app_env: str = "dev"
    app_host: str = "0.0.0.0"
    app_port: int = 8000
    database_url: str = "sqlite:///./medical_assistant.db"
    upload_dir: str = "./uploads"
    timezone: str = "Asia/Kolkata"
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
    )


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()
