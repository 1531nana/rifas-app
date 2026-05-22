from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    database_url: str = "sqlite:///./rifas.db"
    jwt_secret: str = "change-me-in-production"
    access_token_minutes: int = 60
    refresh_token_days: int = 14
    frontend_origin: str = "http://127.0.0.1:5173"
    app_base_url: str = "http://127.0.0.1:8000"
    wompi_public_key: str = "pub_test_local"
    wompi_events_secret: str | None = None
    meta_api_token: str | None = None
    meta_phone_number_id: str | None = None
    organizer_phone: str = "+57XXXXXXXXXX"
    upload_dir: str = "uploads"
    cloudinary_cloud_name: str | None = None
    cloudinary_upload_preset: str | None = None

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")


@lru_cache
def get_settings() -> Settings:
    return Settings()
