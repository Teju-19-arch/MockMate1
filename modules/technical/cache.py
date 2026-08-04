"""
modules/technical/cache.py
--------------------------
Thread-safe LRU cache with TTL expiration support for AI-generated MCQ questions.
Prevents duplicate expensive LLM API requests for identical test parameters.
"""

import time
import threading
import logging
from typing import Optional, List, Dict, Any
import config

logger = logging.getLogger("modules.technical.cache")


class QuestionCache:
    """
    Thread-safe in-memory LRU cache with TTL expiration.
    """

    def __init__(self, ttl_seconds: int = None, max_size: int = 100):
        self.ttl_seconds = ttl_seconds or config.CACHE_TTL_SECONDS
        self.max_size = max_size
        self._cache: Dict[str, Dict[str, Any]] = {}
        self._lock = threading.Lock()
        self.clear()

    def _build_key(self, company: Optional[str], domain: Optional[str], difficulty: str, count: int) -> str:
        """
        Constructs a unique deterministic cache key string.
        """
        c_str = (company or "none").strip().lower()
        d_str = (domain or "none").strip().lower()
        diff_str = (difficulty or "medium").strip().lower()
        return f"company:{c_str}|domain:{d_str}|diff:{diff_str}|count:{count}"

    def get(self, company: Optional[str], domain: Optional[str], difficulty: str, count: int) -> Optional[List[Dict[str, Any]]]:
        """
        Retrieves cached questions if key exists and has not expired.
        """
        if not config.ENABLE_QUESTION_CACHE:
            return None

        key = self._build_key(company, domain, difficulty, count)
        with self._lock:
            if key not in self._cache:
                return None

            entry = self._cache[key]
            current_time = time.time()

            # Check expiration
            if current_time - entry["timestamp"] > self.ttl_seconds:
                logger.info(f"Cache expired for key: {key}")
                del self._cache[key]
                return None

            logger.info(f"Cache HIT for key: {key}")
            return entry["data"]

    def set(self, company: Optional[str], domain: Optional[str], difficulty: str, count: int, data: List[Dict[str, Any]]) -> None:
        """
        Stores question list in cache with current timestamp.
        """
        if not config.ENABLE_QUESTION_CACHE or not data:
            return

        key = self._build_key(company, domain, difficulty, count)
        with self._lock:
            # Evict oldest entry if max_size reached
            if len(self._cache) >= self.max_size:
                oldest_key = min(self._cache.keys(), key=lambda k: self._cache[k]["timestamp"])
                del self._cache[oldest_key]

            self._cache[key] = {
                "data": data,
                "timestamp": time.time()
            }
            logger.info(f"Cache STORED for key: {key}")

    def clear(self) -> None:
        """Clears all cached entries."""
        with self._lock:
            self._cache.clear()
            logger.info("Question cache cleared.")


# Global cache instance
question_cache = QuestionCache()
