"""Configuration management for the Engineering Productivity MVP."""
import os
from pathlib import Path
from typing import Optional

try:
    from pydantic_settings import BaseSettings
except ImportError:
    # Fallback for older pydantic versions
    from pydantic import BaseSettings

from pydantic import Field


class Settings(BaseSettings):
    """Application settings with environment variable support."""
    
    # API Keys
    gemini_api_key: str = Field(..., env="GEMINI_API_KEY")
    github_token: str = Field(..., env="GITHUB_TOKEN")
    slack_bot_token: str = Field(..., env="SLACK_BOT_TOKEN")
    slack_signing_secret: str = Field(..., env="SLACK_SIGNING_SECRET")
    slack_app_token: Optional[str] = Field(default=None, env="SLACK_APP_TOKEN")  # For Socket Mode
    slack_app_token: Optional[str] = Field(default=None, env="SLACK_APP_TOKEN")  # For Socket Mode
    
    # Database
    database_path: str = Field(default="data/productivity.db", env="DATABASE_PATH")
    
    # GitHub Configuration
    github_api_base: str = Field(default="https://api.github.com", env="GITHUB_API_BASE")
    default_repo_owner: str = Field(..., env="DEFAULT_REPO_OWNER")
    default_repo_name: str = Field(..., env="DEFAULT_REPO_NAME")
    
    # LLM Configuration
    llm_model: str = Field(default="gemini-2.5-flash", env="LLM_MODEL")  # Updated to current model
    llm_temperature: float = Field(default=0.1, env="LLM_TEMPERATURE")
    max_tokens: int = Field(default=2048, env="MAX_TOKENS")
    
    # Agent Configuration
    max_retries: int = Field(default=3, env="MAX_RETRIES")
    timeout_seconds: int = Field(default=30, env="TIMEOUT_SECONDS")
    
    # Reporting Configuration
    default_lookback_days: int = Field(default=7, env="DEFAULT_LOOKBACK_DAYS")
    chart_width: int = Field(default=800, env="CHART_WIDTH")
    chart_height: int = Field(default=600, env="CHART_HEIGHT")
    
    # Development
    debug: bool = Field(default=False, env="DEBUG")
    log_level: str = Field(default="INFO", env="LOG_LEVEL")
    disable_ai: bool = Field(default=False, env="DISABLE_AI")  # For demo when quota exceeded
    
    class Config:
        env_file = ".env"
        case_sensitive = False


# Global settings instance
settings = Settings()

# Ensure data directory exists
DATA_DIR = Path(settings.database_path).parent
DATA_DIR.mkdir(exist_ok=True)

# Logging configuration
import logging

logging.basicConfig(
    level=getattr(logging, settings.log_level.upper()),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

logger = logging.getLogger(__name__)