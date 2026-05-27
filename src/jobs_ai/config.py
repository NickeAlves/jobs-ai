from functools import lru_cache
from pathlib import Path
from typing import Optional

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_prefix="", extra="ignore")

    openai_api_key: Optional[str] = None
    openai_model: str = "gpt-5.2"
    app_database_path: Path = Path("data/jobs_ai.sqlite3")
    app_resume_path: Path = Path("data/resume.md")
    app_cv_directory: Path = Path("/documents/cv")
    app_require_manual_review: bool = True
    app_auto_submit_enabled: bool = False

    job_search_query: str = "python backend engineer remote Spain Madrid Bilbao Valladolid Burgos"
    job_search_location: str = "Spain"
    job_search_limit: int = 25


@lru_cache
def get_settings() -> Settings:
    return Settings()
