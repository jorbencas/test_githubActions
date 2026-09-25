from pydantic_settings import BaseSettings
from pydantic import Field
from typing import Optional, List
import os


class Settings(BaseSettings):
    # Telegram
    telegram_bot_token: str = Field(..., alias="TELEGRAM_BOT_TOKEN")
    telegram_reports_channel_id: int = Field(..., alias="TELEGRAM_REPORTS_PROYECTOS_CHANNEL_ID")
    
    # AI (solo Gemini)
    gemini_api_key: str = Field(..., alias="GEMINI_API_KEY")
    ai_model: str = Field("gemini-1.5-flash", alias="AI_MODEL")
    
    # Configuración generación
    projects_per_run: int = Field(3, alias="PROJECTS_PER_RUN")
    scrape_tuweb_dev: bool = Field(True, alias="SCRAPE_TUWEB_DEV")
    
    # Persistencia
    data_dir: str = Field("./data", alias="DATA_DIR")
    history_file: str = Field("generated_projects.json", alias="HISTORY_FILE")
    
    # Scraper opcional
    scrape_tuweb_dev: bool = Field(True, alias="SCRAPE_TUWEB_DEV")
    tuweb_dev_url: str = Field("https://tuweb.dev/", alias="TUWEB_DEV_URL")
    
    # Scheduler
    cron_schedule: str = Field("0 */4 * * *", alias="CRON_SCHEDULE")
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "ignore"


settings = Settings()