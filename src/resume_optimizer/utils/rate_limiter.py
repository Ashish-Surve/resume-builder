"""
Rate limiting and caching utilities for API calls.
"""

import time
import hashlib
import json
import logging
from typing import Any, Callable, Optional
from functools import wraps
from pathlib import Path
import pickle
from datetime import datetime, timedelta


logger = logging.getLogger(__name__)


class RateLimiter:
    """Token bucket rate limiter for API calls."""

    def __init__(self, calls_per_minute: int = 5, calls_per_day: int = 1500):
        """
        Initialize rate limiter.

        Args:
            calls_per_minute: Maximum calls per minute (default: 5 for free tier)
            calls_per_day: Maximum calls per day (default: 1500 for free tier)
        """
        self.calls_per_minute = calls_per_minute
        self.calls_per_day = calls_per_day
        self.minute_tokens = calls_per_minute
        self.day_tokens = calls_per_day
        self.last_minute_refill = time.time()
        self.last_day_refill = time.time()
        self.min_interval = 60.0 / calls_per_minute  # Minimum seconds between calls

    def acquire(self) -> float:
        """
        Acquire a token for making an API call.

        Returns:
            float: Time to wait before making the call (0 if can proceed immediately)
        """
        now = time.time()

        # Refill minute tokens
        time_since_minute = now - self.last_minute_refill
        if time_since_minute >= 60.0:
            self.minute_tokens = self.calls_per_minute
            self.last_minute_refill = now
        elif time_since_minute >= self.min_interval:
            # Gradual refill
            tokens_to_add = int(time_since_minute / self.min_interval)
            self.minute_tokens = min(
                self.calls_per_minute,
                self.minute_tokens + tokens_to_add
            )

        # Refill day tokens
        time_since_day = now - self.last_day_refill
        if time_since_day >= 86400.0:  # 24 hours
            self.day_tokens = self.calls_per_day
            self.last_day_refill = now

        # Check if we have tokens
        if self.minute_tokens <= 0:
            wait_time = self.min_interval - (now - self.last_minute_refill) % self.min_interval
            logger.warning(f"Rate limit: waiting {wait_time:.2f}s for minute quota")
            return wait_time

        if self.day_tokens <= 0:
            wait_time = 86400.0 - time_since_day
            logger.warning(f"Rate limit: waiting {wait_time:.2f}s for daily quota")
            return wait_time

        # Consume tokens
        self.minute_tokens -= 1
        self.day_tokens -= 1
        return 0.0

    def wait_if_needed(self):
        """Wait if rate limit is exceeded."""
        wait_time = self.acquire()
        if wait_time > 0:
            logger.info(f"Rate limiting: sleeping for {wait_time:.2f}s")
            time.sleep(wait_time)


class CacheManager:
    """Disk-based cache manager for API responses."""

    def __init__(self, cache_dir: Optional[Path] = None, ttl_hours: int = 24):
        """
        Initialize cache manager.

        Args:
            cache_dir: Directory for cache files (default: .cache in project root)
            ttl_hours: Time-to-live for cached items in hours
        """
        if cache_dir is None:
            cache_dir = Path.cwd() / ".cache" / "gemini"
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.ttl = timedelta(hours=ttl_hours)
        self.logger = logging.getLogger(__name__)

    def _get_cache_key(self, *args, **kwargs) -> str:
        """Generate a cache key from function arguments."""
        # Create a deterministic string from args and kwargs
        key_data = {
            'args': args,
            'kwargs': {k: v for k, v in sorted(kwargs.items())}
        }
        key_str = json.dumps(key_data, sort_keys=True, default=str)
        return hashlib.sha256(key_str.encode()).hexdigest()

    def _get_cache_path(self, cache_key: str) -> Path:
        """Get the file path for a cache key."""
        return self.cache_dir / f"{cache_key}.pkl"

    def get(self, cache_key: str) -> Optional[Any]:
        """
        Get cached value if it exists and is not expired.

        Args:
            cache_key: Cache key

        Returns:
            Cached value or None if not found/expired
        """
        cache_path = self._get_cache_path(cache_key)

        if not cache_path.exists():
            return None

        try:
            with open(cache_path, 'rb') as f:
                cached_data = pickle.load(f)

            # Check if expired
            if datetime.now() - cached_data['timestamp'] > self.ttl:
                self.logger.debug(f"Cache expired for key {cache_key[:8]}...")
                cache_path.unlink()
                return None

            self.logger.info(f"Cache hit for key {cache_key[:8]}...")
            return cached_data['value']

        except Exception as e:
            self.logger.warning(f"Cache read error: {e}")
            return None

    def set(self, cache_key: str, value: Any):
        """
        Store value in cache.

        Args:
            cache_key: Cache key
            value: Value to cache
        """
        cache_path = self._get_cache_path(cache_key)

        try:
            cached_data = {
                'timestamp': datetime.now(),
                'value': value
            }
            with open(cache_path, 'wb') as f:
                pickle.dump(cached_data, f)

            self.logger.debug(f"Cached value for key {cache_key[:8]}...")

        except Exception as e:
            self.logger.warning(f"Cache write error: {e}")

    def clear(self):
        """Clear all cached items."""
        for cache_file in self.cache_dir.glob("*.pkl"):
            cache_file.unlink()
        self.logger.info("Cache cleared")

    def get_stats(self) -> dict:
        """Get cache statistics."""
        cache_files = list(self.cache_dir.glob("*.pkl"))
        total_size = sum(f.stat().st_size for f in cache_files)

        return {
            'cache_dir': str(self.cache_dir),
            'total_items': len(cache_files),
            'total_size_mb': total_size / (1024 * 1024),
            'ttl_hours': self.ttl.total_seconds() / 3600
        }


def rate_limited(rate_limiter: RateLimiter):
    """
    Decorator to apply rate limiting to a function.

    Args:
        rate_limiter: RateLimiter instance to use

    Example:
        rate_limiter = RateLimiter(calls_per_minute=5)

        @rate_limited(rate_limiter)
        def call_api():
            # API call here
            pass
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            rate_limiter.wait_if_needed()
            return func(*args, **kwargs)
        return wrapper
    return decorator


def cached(cache_manager: CacheManager, cache_key_func: Optional[Callable] = None):
    """
    Decorator to cache function results.

    Args:
        cache_manager: CacheManager instance to use
        cache_key_func: Optional function to generate cache key from args/kwargs

    Example:
        cache = CacheManager()

        @cached(cache)
        def expensive_operation(param):
            # Expensive operation here
            return result
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Generate cache key
            if cache_key_func:
                cache_key = cache_key_func(*args, **kwargs)
            else:
                cache_key = cache_manager._get_cache_key(*args, **kwargs)

            # Try to get from cache
            cached_value = cache_manager.get(cache_key)
            if cached_value is not None:
                return cached_value

            # Call function and cache result
            result = func(*args, **kwargs)
            cache_manager.set(cache_key, result)
            return result

        # Add cache management methods
        wrapper.clear_cache = cache_manager.clear
        wrapper.get_cache_stats = cache_manager.get_stats

        return wrapper
    return decorator
