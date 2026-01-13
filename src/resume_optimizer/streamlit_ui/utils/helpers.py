"""Utility functions for Streamlit UI."""

import os
import logging
from pathlib import Path
from typing import List, Optional

logger = logging.getLogger(__name__)


def load_env_vars():
    """Load environment variables from .env file if not already loaded."""
    from dotenv import load_dotenv

    # Look for .env file in project root
    # Path: helpers.py -> utils/ -> streamlit_ui/ -> resume_optimizer/ -> src/ -> project root
    project_root = Path(__file__).parent.parent.parent.parent.parent
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


def is_ollama_available() -> bool:
    """Check if Ollama is running and available."""
    try:
        from resume_optimizer.core.ai_integration.ollama_client import check_ollama_available
        return check_ollama_available()
    except Exception:
        return False


def get_ollama_models() -> List[str]:
    """Get list of available Ollama models."""
    try:
        from resume_optimizer.core.ai_integration.ollama_client import get_available_models
        return get_available_models()
    except Exception:
        return []


def get_default_ollama_model() -> Optional[str]:
    """Get the default/recommended Ollama model for resume parsing."""
    models = get_ollama_models()

    # Prefer llama3.1 variants
    for model in models:
        if 'llama3.1' in model.lower():
            return model

    # Fall back to any llama model
    for model in models:
        if 'llama' in model.lower():
            return model

    # Return first available model
    return models[0] if models else None
