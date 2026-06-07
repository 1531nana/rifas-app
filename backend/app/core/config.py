from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    database_url: str = "sqlite:///./rifas.db"
    jwt_secret: str = "change-me-in-production"
    access_token_minutes: int = 60
    refresh_token_minutes: int = 10080
    frontend_origin: str = "http://localhost:5173,http://127.0.0.1:5173"
    wompi_public_key: str = "pub_test_ezjBoCzrT4tpmfiUsEiqC2FS7tovdGQL"
    wompi_integrity_key: str = "test_integrity_KeQ2kjKqYkkHTUUI8LfrWlxc7Nyu9lao"
    wompi_events_key: str = "test_events_QY1UIt4KCzXr3BJiL6h0lKt7XHQAUVBq"
    cloudinary_cloud_name: str = ""
    cloudinary_upload_preset: str = ""
    upload_dir: str = "uploads"
    app_base_url: str = "http://127.0.0.1:8000"
    meta_sandbox: bool = True
    meta_api_token: str = ""
    meta_phone_number_id: str = ""
    meta_graph_version: str = "v20.0"
    meta_language_code: str = "es_CO"
    meta_template_payment_confirmation: str = "payment_confirmation"
    meta_template_winner_notification: str = "winner_notification"
    meta_template_payment_reminder: str = "payment_reminder"

    @property
    def allowed_origins(self) -> list[str]:
        return [o.strip() for o in self.frontend_origin.split(",") if o.strip()]

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")


@lru_cache
def get_settings() -> Settings:
    return Settings()
