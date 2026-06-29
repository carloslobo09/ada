from functools import lru_cache
from pathlib import Path
from typing import Literal

from pydantic_settings import BaseSettings, SettingsConfigDict

ExtractorMode = Literal["mock", "gemini"]


class Settings(BaseSettings):
    """Configuracion de la aplicacion, hidratada desde variables de entorno."""

    extractor_mode: ExtractorMode = "mock"
    gemini_api_key: str | None = None
    gemini_model: str = "gemini-2.0-flash"

    db_url: str = "sqlite:///./ada.db"
    upload_dir: Path = Path("./data/uploads")

    log_level: str = "INFO"

    jwt_secret: str = "ada-mvp-dev-secret-cambiar-en-produccion"
    jwt_algorithm: str = "HS256"
    jwt_expire_minutes: int = 480

    seed_password: str = "ada2026"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()
