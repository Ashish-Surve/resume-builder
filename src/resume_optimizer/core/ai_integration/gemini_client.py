from typing import List, Optional
import os
import logging
import hashlib
from pydantic import SecretStr
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import SystemMessage, HumanMessage

from ...utils.rate_limiter import RateLimiter, CacheManager


class GeminiClient:
    """
    Gemini AI client with rate limiting and caching.

    Features:
    - Automatic rate limiting (model-specific limits)
    - Response caching to avoid redundant API calls
    - Exponential backoff on rate limit errors

    Model Options (FREE tier):
    - gemini-2.5-flash-lite: RECOMMENDED - fastest, most cost-effective, best for most tasks
    """

    # Model-specific rate limits (requests per minute)
    MODEL_RATE_LIMITS = {
        "gemini-2.5-flash-lite": 4,  # Fast and efficient for resume/job analysis
        "gemini-2.5-pro": 2,         # More capable but slower
    }

    def __init__(
        self,
        api_key=None,
        model="gemini-2.5-flash-lite",  # Default: best balance of speed/quality/limits
        temperature=0.2,
        enable_cache=True,
        cache_ttl_hours=24,
        calls_per_minute=None  # Auto-detect based on model if None
    ):
        """
        Initialize Gemini client with rate limiting and caching.

        Args:
            api_key: Google API key (defaults to GOOGLE_API_KEY env var)
            model: Model name (default: gemini-2.5-flash-lite)
                   ONLY use: gemini-2.5-flash-lite (other models are deprecated)
            temperature: Temperature for generation (0.0-1.0)
            enable_cache: Enable response caching (default: True)
            cache_ttl_hours: Cache time-to-live in hours (default: 24)
            calls_per_minute: Max API calls per minute
                             If None, auto-detects based on model limits
        """
        key = api_key or os.getenv("GOOGLE_API_KEY")
        secret = SecretStr(key) if key is not None else None
        self.model_name = model

        self.chat = ChatGoogleGenerativeAI(
            model=model,
            temperature=temperature,
            api_key=secret,
            max_retries=3  # Enable automatic retries
        )

        # Auto-detect rate limit based on model if not specified
        if calls_per_minute is None:
            calls_per_minute = self.MODEL_RATE_LIMITS.get(model, 4)

        # Initialize rate limiter
        self.rate_limiter = RateLimiter(calls_per_minute=calls_per_minute)

        # Initialize cache manager
        self.enable_cache = enable_cache
        if enable_cache:
            self.cache_manager = CacheManager(ttl_hours=cache_ttl_hours)
        else:
            self.cache_manager = None

        self.logger = logging.getLogger(__name__)
        self.logger.info(
            f"GeminiClient initialized: model={model}, "
            f"cache={'enabled' if enable_cache else 'disabled'}, "
            f"rate_limit={calls_per_minute}/min"
        )

    def _get_cache_key(self, system: str, user: str) -> str:
        """Generate cache key from system and user prompts."""
        combined = f"{system}|||{user}"
        return hashlib.sha256(combined.encode()).hexdigest()

    def invoke(self, system: str, user: str, bypass_cache: bool = False) -> str:
        """
        Invoke Gemini API with rate limiting and caching.

        Args:
            system: System prompt
            user: User prompt
            bypass_cache: Skip cache lookup and force API call

        Returns:
            str: Model response
        """
        # Check cache first
        cache_key = None
        if self.enable_cache and not bypass_cache:
            cache_key = self._get_cache_key(system, user)
            cached_response = self.cache_manager.get(cache_key)
            if cached_response is not None:
                self.logger.info("Using cached response")
                return cached_response

        # Apply rate limiting before API call
        self.rate_limiter.wait_if_needed()

        # Make API call
        try:
            msgs = [SystemMessage(content=system), HumanMessage(content=user)]
            generation_config = {
                "response_mime_type": "application/json",
            }

            self.logger.debug(f"Calling Gemini API (cache_key={cache_key[:8] if cache_key else 'none'}...)")
            resp = self.chat.invoke(msgs, generation_config=generation_config)
            response_content = getattr(resp, "content", str(resp))

            # Cache the response
            if self.enable_cache and cache_key:
                self.cache_manager.set(cache_key, response_content)

            return response_content

        except Exception as e:
            self.logger.error(f"Gemini API call failed: {e}")
            raise

    def clear_cache(self):
        """Clear all cached responses."""
        if self.cache_manager:
            self.cache_manager.clear()
            self.logger.info("Cache cleared")

    def get_cache_stats(self) -> dict:
        """Get cache statistics."""
        if self.cache_manager:
            return self.cache_manager.get_stats()
        return {"cache_enabled": False}
