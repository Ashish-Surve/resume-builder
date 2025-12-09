"""Utility functions for Streamlit UI."""

import os
import logging
from pathlib import Path

logger = logging.getLogger(__name__)


def load_env_vars():
    """Load environment variables from .env file if not already loaded."""
    from dotenv import load_dotenv

    # Look for .env file in project root
    project_root = Path(__file__).parent.parent.parent.parent
    env_file = project_root / ".env"

    if env_file.exists():
        load_dotenv(env_file)
        logger.info(f"Loaded environment variables from {env_file}")
    else:
        logger.warning(f".env file not found at {env_file}")


def get_gemini_api_key() -> str:
    """Get Gemini API key from environment variables."""
    load_env_vars()

    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key or api_key.startswith("your_"):
        return None

    return api_key


def has_gemini_api_key() -> bool:
    """Check if Gemini API key is configured."""
    return get_gemini_api_key() is not None
