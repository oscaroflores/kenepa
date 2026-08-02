from functools import lru_cache
from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    database_url: str = Field(default="sqlite:///./kenepa.db", alias="DATABASE_URL")
    sec_user_agent: str = Field(default="your-name your-email@example.com", alias="SEC_USER_AGENT")
    data_dir: Path = Field(default=Path("data"), alias="DATA_DIR")
    reports_dir: Path = Field(default=Path("reports"), alias="REPORTS_DIR")
    companies_dir: Path = Field(default=Path("companies"), alias="COMPANIES_DIR")

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")


@lru_cache
def get_settings() -> Settings:
    settings = Settings()
    settings.data_dir.mkdir(parents=True, exist_ok=True)
    settings.reports_dir.mkdir(parents=True, exist_ok=True)
    return settings
