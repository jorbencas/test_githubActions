from pydantic_settings import BaseSettings
from pydantic import Field
from typing import Optional, List
import os


class Settings(BaseSettings):
    # Telegram
    telegram_bot_token: str = Field(..., alias="TELEGRAM_BOT_TOKEN")
    telegram_reports_channel_id: int = Field(..., alias="TELEGRAM_REPORTS_PROYECTOS_CHANNEL_ID")
    
    # AI Providers (al menos uno requerido)
    openai_api_key: Optional[str] = Field(None, alias="OPENAI_API_KEY")
    anthropic_api_key: Optional[str] = Field(None, alias="ANTHROPIC_API_KEY")
    gemini_api_key: Optional[str] = Field(None, alias="GEMINI_API_KEY")
    
    # Configuración generación
    ai_provider: str = Field("openai", alias="AI_PROVIDER")  # openai, anthropic, gemini
    ai_model: str = Field("gpt-4o-mini", alias="AI_MODEL")
    projects_per_run: int = Field(5, alias="PROJECTS_PER_RUN")
    
    # Persistencia
    data_dir: str = Field("./data", alias="DATA_DIR")
    history_file: str = Field("generated_projects.json", alias="HISTORY_FILE")
    
    # Scraper opcional
    scrape_tuweb_dev: bool = Field(False, alias="SCRAPE_TUWEB_DEV")
    tuweb_dev_url: str = Field("https://tuweb.dev/", alias="TUWEB_DEV_URL")
    
    # Scheduler
    cron_schedule: str = Field("0 9 * * 1", alias="CRON_SCHEDULE")  # Lunes 9am
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "ignore"


settings = Settings()