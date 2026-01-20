from functools import lru_cache
from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

ENV_FILE_PATH = Path(__file__).parent.parent / ".env"


class Settings(BaseSettings):
    db_host: str
    db_port: int
    db_user: str
    db_pass: str
    db_name: str
    google_api_key: str
    log_level: str = Field(default='DEBUG')


    model_config = SettingsConfigDict(
        env_file=ENV_FILE_PATH,
        extra="allow",
        env_file_encoding="utf-8",
        case_sensitive=False
    )


@lru_cache
def get_config() -> Settings:
    return Settings()
