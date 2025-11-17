from __future__ import annotations

from functools import lru_cache
from typing import Literal

from pydantic import BaseModel
from pydantic_settings import BaseSettings, SettingsConfigDict


class TokenSettings(BaseModel):
    secret_key: str
    algorithm: str
    access_token_expire_minutes: int
    refresh_token_expire_minutes: int


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    app_name: str = "MiniCRM"
    api_v1_prefix: str = "/api/v1"
    environment: Literal["local", "test", "staging", "prod", "docker"] = "local"
    log_level: str = "INFO"

    database_url: str = "sqlite+aiosqlite:///./mini_crm.db"

    secret_key: str = "changeme"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    refresh_token_expire_minutes: int = 60 * 24

    cache_ttl_seconds: int = 60

    @property
    def token_settings(self) -> TokenSettings:
        return TokenSettings(
            secret_key=self.secret_key,
            algorithm=self.algorithm,
            access_token_expire_minutes=self.access_token_expire_minutes,
            refresh_token_expire_minutes=self.refresh_token_expire_minutes,
        )


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()


