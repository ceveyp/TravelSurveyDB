import os
from functools import lru_cache
from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

from clients.secrets_manager import SecretsManager

ENV_FILE_PATH = Path(__file__).parent.parent / ".env"


class Settings(BaseSettings):
    db_host: str
    db_port: int
    db_user: str
    db_pass: str
    db_name: str
    google_api_key: str
    alchemer_api_key: str
    alchemer_api_secret: str
    webhook_secret: str
    sqs_queue_url: str
    travel_db_survey_id: int
    log_level: str = Field(default='DEBUG')

    model_config = SettingsConfigDict(
        env_file=ENV_FILE_PATH,
        extra="allow",
        env_file_encoding="utf-8",
        case_sensitive=False
    )


@lru_cache
def get_config() -> Settings:
    secret_name = os.environ.get("SECRETS_NAME")

    if secret_name:
        secrets = SecretsManager(secret_name).get_secrets()
        for key, value in secrets.items():
            os.environ.setdefault(key, str(value))

    return Settings()
