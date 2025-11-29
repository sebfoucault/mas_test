"""
Custom exceptions for MAS Training Audio Generator.
"""


class MASError(Exception):
    """Base exception for MAS Training Audio Generator."""
    pass


class ConfigurationError(MASError):
    """Error in configuration validation."""
    pass


class AudioGenerationError(MASError):
    """Base exception for audio generation errors."""
    pass


class CacheError(AudioGenerationError):
    """Error related to cache operations."""
    pass


class TTSError(AudioGenerationError):
    """Error related to text-to-speech generation."""
    pass


class IntervalGenerationError(MASError):
    """Error in interval generation."""
    pass
