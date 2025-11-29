"""
Constants for MAS Training Audio Generator.
"""


class AudioConstants:
    """Audio-related constants."""
    SAMPLE_RATE = 44100
    BIT_DEPTH = 16
    CHANNELS = 1
    BEEP_FREQUENCY = 220  # A3 note for warm, deep sound
    BEEP_DURATION = 0.5
    BEEP_AMPLITUDE = 10000  # Reduced for harmonics headroom
    TRIPLE_BEEP_DURATION = 0.2
    TRIPLE_BEEP_PAUSE = 0.1
    COUNTDOWN_NUMBER_PAUSE = 1.0  # Pause between countdown numbers
    VOICE_ANNOUNCEMENT_LEAD_TIME = 10.0
    SILENCE_FALLBACK = 2.0
    TTS_RATE = 150  # Speech rate
    TTS_VOLUME = 0.9  # Volume level (0.0 to 1.0)


class SampleLimits:
    """Sample value limits for 16-bit audio."""
    MAX_SAMPLE = 32767
    MIN_SAMPLE = -32768


class CacheConstants:
    """Cache-related constants."""
    DEFAULT_CACHE_DIR = ".cache"
    CACHE_FILE_NAME = "audio_cache.pkl"
