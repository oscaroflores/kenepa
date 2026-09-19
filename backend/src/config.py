from functools import lru_cache
import os
from pathlib import Path

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    database_url: str = Field(default="sqlite:///./kenepa.db", alias="DATABASE_URL")
    sec_user_agent: str = Field(default="your-name your-email@example.com", alias="SEC_USER_AGENT")
    data_dir: Path = Field(default=Path("data"), alias="DATA_DIR")
    reports_dir: Path = Field(default=Path("reports"), alias="REPORTS_DIR")
    companies_dir: Path = Field(default=Path("companies"), alias="COMPANIES_DIR")

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    @field_validator("database_url")
    @classmethod
    def use_declared_postgres_driver(cls, value: str) -> str:
        if value.startswith("postgresql://"):
            return value.replace("postgresql://", "postgresql+psycopg://", 1)
        return value

    @field_validator("data_dir", "reports_dir")
    @classmethod
    def use_writable_vercel_path(cls, value: Path) -> Path:
        if os.getenv("VERCEL") and value.is_absolute() and not str(value).startswith("/tmp"):
            return Path("/tmp") / value.name
        return value


@lru_cache
def get_settings() -> Settings:
    return Settings()
