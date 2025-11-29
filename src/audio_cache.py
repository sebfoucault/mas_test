"""
Audio caching module for MAS Training Audio Generator.
Provides efficient caching of generated audio samples.
"""

import os
import pickle
import hashlib
import logging
from typing import Dict, List, Optional
from pathlib import Path

logger = logging.getLogger(__name__)


class AudioCache:
    """Manages caching of generated audio samples."""

    def __init__(self, cache_dir: str, enabled: bool = True):
        """
        Initialize audio cache.

        Args:
            cache_dir: Directory path for cache storage.
            enabled: Whether caching is enabled.
        """
        self.cache_dir = cache_dir
        self.enabled = enabled
        self._cache: Dict[str, List[int]] = {}
        self._loaded = False

    def _get_cache_file_path(self) -> str:
        """Get the path to the cache file."""
        return os.path.join(self.cache_dir, "audio_cache.pkl")

    def _ensure_cache_dir(self) -> None:
        """Ensure cache directory exists."""
        if self.enabled:
            Path(self.cache_dir).mkdir(parents=True, exist_ok=True)

    def _load(self) -> None:
        """Load cached audio samples from disk."""
        if self._loaded or not self.enabled:
            return

        self._ensure_cache_dir()
        cache_file = self._get_cache_file_path()

        if os.path.exists(cache_file):
            try:
                with open(cache_file, 'rb') as f:
                    self._cache = pickle.load(f)
                logger.info(f"Loaded {len(self._cache)} cached audio samples")
            except Exception as e:
                logger.warning(f"Could not load audio cache: {e}")
                self._cache = {}

        self._loaded = True

    def _save(self) -> None:
        """Save cached audio samples to disk."""
        if not self.enabled:
            return

        self._ensure_cache_dir()
        cache_file = self._get_cache_file_path()

        try:
            with open(cache_file, 'wb') as f:
                pickle.dump(self._cache, f)
        except Exception as e:
            logger.warning(f"Could not save audio cache: {e}")

    @staticmethod
    def generate_key(prefix: str, *args) -> str:
        """
        Generate a cache key from prefix and arguments.

        Args:
            prefix: Key prefix (e.g., 'beep', 'voice').
            *args: Additional arguments to include in key.

        Returns:
            MD5 hash of the key components.
        """
        key_str = f"{prefix}:" + ":".join(str(arg) for arg in args)
        return hashlib.md5(key_str.encode()).hexdigest()

    def get(self, key: str) -> Optional[List[int]]:
        """
        Retrieve cached audio samples.

        Args:
            key: Cache key.

        Returns:
            Copy of cached samples or None if not found.
        """
        if not self.enabled:
            return None

        self._load()
        if key in self._cache:
            return self._cache[key].copy()
        return None

    def set(self, key: str, samples: List[int]) -> None:
        """
        Cache audio samples.

        Args:
            key: Cache key.
            samples: Audio samples to cache.
        """
        if not self.enabled:
            return

        self._load()
        self._cache[key] = samples.copy()
        self._save()

    def clear(self) -> None:
        """Clear all cached samples."""
        self._cache = {}
        cache_file = self._get_cache_file_path()
        if os.path.exists(cache_file):
            try:
                os.remove(cache_file)
                logger.info("Cache cleared")
            except Exception as e:
                logger.warning(f"Could not clear cache: {e}")

    def size(self) -> int:
        """Get number of cached items."""
        self._load()
        return len(self._cache)
