"""
Configuration and data classes for MAS Training Audio Generator.
"""

import os
import logging
from dataclasses import dataclass
from pathlib import Path
from typing import Optional
from constants import CacheConstants
from exceptions import ConfigurationError

logger = logging.getLogger(__name__)


# Audio cache configuration (backward compatibility)
DEFAULT_CACHE_DIR = CacheConstants.DEFAULT_CACHE_DIR


def is_cache_enabled():
    """Check if audio caching is enabled (backward compatibility)."""
    return os.environ.get('MAS_ENABLE_CACHE', '1') == '1'


def get_cache_directory():
    """
    Get the cache directory path, creating it if needed.
    (backward compatibility function)
    """
    cache_dir = os.environ.get('MAS_CACHE_DIR', DEFAULT_CACHE_DIR)
    cache_path = Path(cache_dir)
    cache_path.mkdir(parents=True, exist_ok=True)
    return str(cache_path)


@dataclass
class TestConfig:
    """
    Configuration parameters for training test generation.

    This class combines training, audio, and cache configuration.
    Consider using separate config classes for better separation of concerns.
    """

    init_speed_in_km_per_hour: float
    init_speed_in_meters_per_sec: float
    interval_distance_in_meters: int
    stage_duration_in_sec: int
    stage_duration_threshold_in_sec: int
    stage_speed_increment: float
    max_speed: float
    enable_cache: bool
    cache_dir: str

    def __init__(
        self,
        init_speed_in_km_per_hour: float,
        interval_distance_in_meters: int,
        stage_duration_in_sec: int,
        stage_duration_threshold_in_sec: int,
        stage_speed_increment: float,
        max_speed: float,
        enable_cache: bool = True,
        cache_dir: Optional[str] = None
    ):
        """
        Initialize training configuration with validation.

        Args:
            init_speed_in_km_per_hour: Initial training speed in km/h.
            interval_distance_in_meters: Distance for each interval in meters.
            stage_duration_in_sec: Target duration for each stage in seconds.
            stage_duration_threshold_in_sec: Threshold for stage completion.
            stage_speed_increment: Speed increase per stage in km/h.
            max_speed: Maximum training speed in km/h.
            enable_cache: Whether to enable audio caching.
            cache_dir: Directory for cache storage (defaults to .cache).

        Raises:
            ConfigurationError: If configuration values are invalid.
        """
        # Validate inputs
        self._validate_positive("init_speed_in_km_per_hour",
                                init_speed_in_km_per_hour)
        self._validate_positive("interval_distance_in_meters",
                                interval_distance_in_meters)
        self._validate_positive("stage_duration_in_sec", stage_duration_in_sec)
        self._validate_positive("stage_duration_threshold_in_sec",
                                stage_duration_threshold_in_sec)
        self._validate_positive("stage_speed_increment", stage_speed_increment)
        self._validate_positive("max_speed", max_speed)

        if max_speed < init_speed_in_km_per_hour:
            raise ConfigurationError(
                f"max_speed ({max_speed}) must be >= "
                f"init_speed ({init_speed_in_km_per_hour})"
            )

        # Set values
        self.init_speed_in_km_per_hour = init_speed_in_km_per_hour
        self.interval_distance_in_meters = interval_distance_in_meters
        self.stage_duration_in_sec = stage_duration_in_sec
        self.stage_duration_threshold_in_sec = stage_duration_threshold_in_sec
        self.stage_speed_increment = stage_speed_increment
        self.max_speed = max_speed
        self.enable_cache = enable_cache
        self.cache_dir = cache_dir if cache_dir else DEFAULT_CACHE_DIR

        # Derived values
        self.init_speed_in_meters_per_sec = init_speed_in_km_per_hour / 3.6

        logger.debug(f"Configuration created: {self}")

    @staticmethod
    def _validate_positive(name: str, value: float) -> None:
        """Validate that a value is positive."""
        if value <= 0:
            raise ConfigurationError(f"{name} must be positive, got {value}")
