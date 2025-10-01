
# src/resume_optimizer/config/settings.py
"""
Configuration management for the Resume Optimizer application.
Follows PEP 8 standards and modular design principles.
"""

import os
from dataclasses import dataclass
from typing import Optional
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


@dataclass
class DatabaseConfig:
    """Database configuration settings."""
    host: str = "localhost"
    port: int = 5432
    name: str = "resume_optimizer"
    user: Optional[str] = None
    password: Optional[str] = None


@dataclass
class AIConfig:
    """AI service configuration settings."""
    perplexity_api_key: Optional[str] = None
    gemini_api_key: Optional[str] = None
    max_retries: int = 3
    timeout: int = 30
    temperature: float = 0.7


@dataclass
class AppConfig:
    """Application configuration settings."""
    debug: bool = False
    data_dir: Path = Path("data")
    temp_dir: Path = Path("data/temp")
    max_file_size: int = 10 * 1024 * 1024  # 10MB
    supported_formats: tuple = (".pdf", ".docx", ".txt")


class ConfigManager:
    """
    Centralized configuration management class.
    Implements Singleton pattern for global access.
    """

    _instance: Optional['ConfigManager'] = None

    def __new__(cls) -> 'ConfigManager':
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if not hasattr(self, '_initialized'):
            self._load_config()
            self._initialized = True

    def _load_config(self) -> None:
        """Load configuration from environment variables."""
        self.ai = AIConfig(
            perplexity_api_key=os.getenv("PERPLEXITY_API_KEY"),
            gemini_api_key=os.getenv("GOOGLE_API_KEY"),
            max_retries=int(os.getenv("AI_MAX_RETRIES", "3")),
            timeout=int(os.getenv("AI_TIMEOUT", "30")),
            temperature=float(os.getenv("AI_TEMPERATURE", "0.7"))
        )

        self.app = AppConfig(
            debug=os.getenv("DEBUG", "False").lower() == "true",
            data_dir=Path(os.getenv("DATA_DIR", "data")),
            temp_dir=Path(os.getenv("TEMP_DIR", "data/temp")),
            max_file_size=int(os.getenv("MAX_FILE_SIZE", str(10 * 1024 * 1024)))
        )

        self.database = DatabaseConfig(
            host=os.getenv("DB_HOST", "localhost"),
            port=int(os.getenv("DB_PORT", "5432")),
            name=os.getenv("DB_NAME", "resume_optimizer"),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD")
        )

    def get_ai_config(self) -> AIConfig:
        """Get AI configuration."""
        return self.ai

    def get_app_config(self) -> AppConfig:
        """Get application configuration."""
        return self.app

    def validate_config(self) -> bool:
        """Validate configuration settings."""
        errors = []

        if not self.ai.perplexity_api_key:
            errors.append("PERPLEXITY_API_KEY not set")

        if not self.ai.gemini_api_key:
            errors.append("GOOGLE_API_KEY not set")

        if not self.app.data_dir.exists():
            self.app.data_dir.mkdir(parents=True, exist_ok=True)

        if not self.app.temp_dir.exists():
            self.app.temp_dir.mkdir(parents=True, exist_ok=True)

        if errors:
            raise ValueError(f"Configuration errors: {', '.join(errors)}")

        return True


# Global config instance
config = ConfigManager()
