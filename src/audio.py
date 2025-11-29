"""
Audio generation module for MAS Training Audio Generator.
Handles voice synthesis, beep generation, and WAV file creation.
"""

import logging
import math
import os
import random
import struct
import tempfile
import time
import wave
from typing import List, Optional

import pyttsx3

from audio_cache import AudioCache
from config import TestConfig
from constants import AudioConstants, SampleLimits
from exceptions import AudioGenerationError, TTSError

logger = logging.getLogger(__name__)


def generate_sine_wave(
    duration: float,
    frequency: float,
    sample_rate: int = AudioConstants.SAMPLE_RATE
) -> List[int]:
    """
    Generate a warm tone with harmonics and envelope for a pleasant sound.

    Args:
        duration: Duration in seconds
        frequency: Frequency in Hz
        sample_rate: Sample rate in Hz

    Returns:
        List of audio samples
    """
    samples = []
    num_samples = int(duration * sample_rate)
    attack_samples = int(0.02 * sample_rate)  # 20ms attack
    release_samples = int(0.05 * sample_rate)  # 50ms release

    for i in range(num_samples):
        t = i / sample_rate

        # Create warm tone with fundamental and harmonics
        # Fundamental (full amplitude)
        tone = math.sin(2 * math.pi * frequency * t)
        # Second harmonic (reduced) for warmth
        tone += 0.3 * math.sin(2 * math.pi * frequency * 2 * t)
        # Third harmonic (reduced) for richness
        tone += 0.15 * math.sin(2 * math.pi * frequency * 3 * t)
        # Fifth harmonic (subtle) for bell-like quality
        tone += 0.08 * math.sin(2 * math.pi * frequency * 5 * t)

        # Apply envelope (attack-sustain-release)
        envelope = 1.0
        if i < attack_samples:
            # Smooth attack
            envelope = i / attack_samples
        elif i > num_samples - release_samples:
            # Smooth release
            envelope = (num_samples - i) / release_samples

        sample = int(AudioConstants.BEEP_AMPLITUDE * tone * envelope)
        samples.append(sample)
    return samples


def generate_silence(
    duration: float,
    sample_rate: int = AudioConstants.SAMPLE_RATE
) -> List[int]:
    """
    Generate silence for specified duration.

    Args:
        duration: Duration in seconds
        sample_rate: Sample rate in Hz

    Returns:
        List of zero samples
    """
    return [0] * int(duration * sample_rate)


def generate_beep(
    duration: float = AudioConstants.BEEP_DURATION,
    frequency: float = AudioConstants.BEEP_FREQUENCY,
    cache: Optional[AudioCache] = None
) -> List[int]:
    """
    Generate a single beep with optional caching.

    Args:
        duration: Beep duration in seconds
        frequency: Beep frequency in Hz
        cache: Optional AudioCache instance for caching

    Returns:
        List of audio samples
    """
    cache_key = AudioCache.generate_key("beep", duration, frequency)

    if cache:
        cached = cache.get(cache_key)
        if cached is not None:
            logger.debug(f"Using cached beep: {duration}s @ {frequency}Hz")
            return cached.copy()

    logger.debug(f"Generating beep: {duration}s @ {frequency}Hz")
    samples = generate_sine_wave(duration, frequency)

    if cache:
        cache.set(cache_key, samples.copy())

    return samples


def generate_triple_beep(cache: Optional[AudioCache] = None) -> List[int]:
    """
    Generate a triple beep sequence for speed changes with optional caching.

    Args:
        cache: Optional AudioCache instance for caching

    Returns:
        List of audio samples
    """
    cache_key = AudioCache.generate_key("triple_beep")

    if cache:
        cached = cache.get(cache_key)
        if cached is not None:
            logger.debug("Using cached triple beep")
            return cached.copy()

    logger.debug("Generating triple beep")
    beep = generate_sine_wave(
        AudioConstants.TRIPLE_BEEP_DURATION,
        AudioConstants.BEEP_FREQUENCY
    )
    pause = generate_silence(AudioConstants.TRIPLE_BEEP_PAUSE)
    samples = beep + pause + beep + pause + beep

    if cache:
        cache.set(cache_key, samples.copy())

    return samples


def generate_voice_announcement(
    text: str,
    temp_dir: str,
    cache: Optional[AudioCache] = None
) -> List[int]:
    """
    Generate voice announcement using pyttsx3 with optional caching.

    Args:
        text: Text to speak
        temp_dir: Temporary directory for intermediate files
        cache: Optional AudioCache instance for caching

    Returns:
        List of audio samples

    Raises:
        TTSError: If TTS fails completely
    """
    cache_key = AudioCache.generate_key("voice", text)

    if cache:
        cached = cache.get(cache_key)
        if cached is not None:
            logger.info(f"Using cached voice: {text}")
            return cached.copy()

    logger.info(f"Generating voice: {text}")

    try:
        # Initialize the TTS engine
        engine = pyttsx3.init()

        # Set properties for natural speech
        engine.setProperty('rate', AudioConstants.TTS_RATE)
        engine.setProperty('volume', AudioConstants.TTS_VOLUME)

        # Try to set a female voice if available
        voices = engine.getProperty('voices')
        for voice in voices:
            if 'female' in voice.name.lower() or 'zira' in voice.name.lower():
                engine.setProperty('voice', voice.id)
                break

        # Create temporary file for TTS output
        timestamp = str(int(time.time() * 1000))
        random_suffix = str(random.randint(1000, 9999))
        temp_wav = os.path.join(
            temp_dir,
            f"temp_voice_{timestamp}_{random_suffix}.wav"
        )

        # Save speech to file
        engine.save_to_file(text, temp_wav)
        engine.runAndWait()

        # Read the generated WAV file
        if not os.path.exists(temp_wav):
            logger.error("TTS audio file was not created")
            return generate_silence(AudioConstants.SILENCE_FALLBACK)

        try:
            with wave.open(temp_wav, 'rb') as wav_file:
                frames = wav_file.readframes(wav_file.getnframes())
                sample_rate = wav_file.getframerate()
                channels = wav_file.getnchannels()

                logger.debug(
                    f"pyttsx3 audio: {sample_rate} Hz, "
                    f"{channels} channel(s)"
                )

                # Convert to list of integers
                if channels == 1:
                    fmt = '<' + 'h' * (len(frames) // 2)
                    samples = list(struct.unpack(fmt, frames))
                else:
                    # Convert stereo to mono by averaging channels
                    fmt = '<' + 'h' * (len(frames) // 2)
                    stereo_samples = list(struct.unpack(fmt, frames))
                    samples = []
                    for i in range(0, len(stereo_samples), 2):
                        if i + 1 < len(stereo_samples):
                            mono_sample = (
                                stereo_samples[i] +
                                stereo_samples[i + 1]
                            ) // 2
                            samples.append(mono_sample)
                        else:
                            samples.append(stereo_samples[i])

                # Resample to 44100 Hz if needed
                if sample_rate != AudioConstants.SAMPLE_RATE:
                    samples = resample_audio(
                        samples,
                        sample_rate,
                        AudioConstants.SAMPLE_RATE
                    )
                    logger.debug(
                        f"Resampled from {sample_rate} Hz to "
                        f"{AudioConstants.SAMPLE_RATE} Hz"
                    )

                # Cache the result
                if cache:
                    cache.set(cache_key, samples.copy())

                return samples
        finally:
            # Clean up temp file
            if os.path.exists(temp_wav):
                try:
                    os.remove(temp_wav)
                except OSError:
                    pass

    except Exception as e:
        logger.error(f"pyttsx3 error: {e}. Using silence instead.")
        return generate_silence(AudioConstants.SILENCE_FALLBACK)


def resample_audio(
    samples: List[int],
    original_rate: int,
    target_rate: int
) -> List[int]:
    """
    Simple audio resampling using linear interpolation.

    Args:
        samples: Original audio samples
        original_rate: Original sample rate in Hz
        target_rate: Target sample rate in Hz

    Returns:
        Resampled audio samples
    """
    if original_rate == target_rate:
        return samples

    ratio = target_rate / original_rate
    new_length = int(len(samples) * ratio)

    resampled = []
    for i in range(new_length):
        original_index = i / ratio
        # Simple linear interpolation
        index_floor = int(original_index)
        index_ceil = min(index_floor + 1, len(samples) - 1)

        if index_floor == index_ceil:
            resampled.append(samples[index_floor])
        else:
            weight = original_index - index_floor
            interpolated = int(
                samples[index_floor] * (1 - weight) +
                samples[index_ceil] * weight
            )
            resampled.append(interpolated)

    return resampled


def write_wav_file(
    samples: List[int],
    filename: str,
    sample_rate: int = AudioConstants.SAMPLE_RATE
) -> None:
    """
    Write samples to a WAV file.

    Args:
        samples: Audio samples to write
        filename: Output filename
        sample_rate: Sample rate in Hz

    Raises:
        AudioGenerationError: If file writing fails
    """
    try:
        with wave.open(filename, 'wb') as wav_file:
            wav_file.setnchannels(1)  # Mono
            wav_file.setsampwidth(2)  # 16-bit
            wav_file.setframerate(sample_rate)

            # Ensure all samples are within 16-bit range
            clipped_samples = []
            for sample in samples:
                if sample > SampleLimits.MAX_SAMPLE:
                    clipped_samples.append(SampleLimits.MAX_SAMPLE)
                elif sample < SampleLimits.MIN_SAMPLE:
                    clipped_samples.append(SampleLimits.MIN_SAMPLE)
                else:
                    clipped_samples.append(sample)

            # Convert to bytes and write
            fmt = '<' + 'h' * len(clipped_samples)
            frames = struct.pack(fmt, *clipped_samples)
            wav_file.writeframes(frames)
    except Exception as e:
        raise AudioGenerationError(f"Failed to write WAV file: {e}")


def create_audio_timeline(
    intervals: List,
    temp_dir: str,
    cache: Optional[AudioCache] = None
) -> List[int]:
    """
    Create audio timeline with beeps and voice announcements.

    Args:
        intervals: List of interval parameters
        temp_dir: Temporary directory for intermediate files
        cache: Optional AudioCache instance for caching

    Returns:
        List of audio samples for complete timeline
    """
    logger.info("Creating audio timeline...")
    audio_samples = []

    # Add starting test announcement with countdown
    logger.info("Adding 'starting test in 5 seconds' announcement")
    starting_announcement = "Starting... test in 5 seconds"
    starting_voice_samples = generate_voice_announcement(
        starting_announcement, temp_dir, cache
    )
    audio_samples.extend(starting_voice_samples)

    # Add countdown: 4, 3, 2, 1
    countdown_numbers = [4, 3, 2, 1]
    for i, countdown_num in enumerate(countdown_numbers):
        # Add pause before each countdown number
        audio_samples.extend(
            generate_silence(AudioConstants.COUNTDOWN_NUMBER_PAUSE)
        )
        # Add voice for countdown number
        logger.info(f"Adding countdown: {countdown_num}")
        countdown_voice = generate_voice_announcement(
            str(countdown_num), temp_dir, cache
        )
        audio_samples.extend(countdown_voice)

    # Add a short pause before final beep (same duration as between numbers)
    audio_samples.extend(
        generate_silence(AudioConstants.COUNTDOWN_NUMBER_PAUSE)
    )

    # Add final beep to signal start (time zero reference point)
    logger.info("Adding start signal beep (time zero reference)")
    audio_samples.extend(generate_beep(cache=cache))

    # Track the duration including announcement, countdown, and start beep
    # This is the offset - all interval times are relative to the final beep
    starting_offset = len(audio_samples) / AudioConstants.SAMPLE_RATE

    for i, interval in enumerate(intervals):
        # Calculate the time until this interval ends
        interval_end_time = (
            interval.total_duration_at_end_in_sec + starting_offset
        )

        # Check if voice announcement needed before speed change
        # The announcement should be made during the CURRENT interval if this interval
        # ends with a speed change (move_to_next_stage_at_end is True)
        if interval.move_to_next_stage_at_end and i < len(intervals) - 1:
            next_interval = intervals[i + 1]
            # There's a speed change coming at the end of this interval
            voice_time = (
                interval_end_time -
                AudioConstants.VOICE_ANNOUNCEMENT_LEAD_TIME
            )
            # Only if enough time after start beep
            if voice_time > starting_offset:
                # Calculate current audio duration
                current_audio_duration = (
                    len(audio_samples) / AudioConstants.SAMPLE_RATE
                )

                # Add silence until voice announcement time
                silence_duration = (
                    voice_time - current_audio_duration
                )
                if silence_duration > 0:
                    audio_samples.extend(
                        generate_silence(silence_duration)
                    )

                # Add voice announcement for the NEXT interval's speed
                speed_value = next_interval.speed_in_km_per_hour
                announcement_text = (
                    f"Next speed... {speed_value:.1f}... "
                    f"kilometers per hour"
                )
                logger.info(
                    f"Adding voice announcement at "
                    f"{voice_time:.1f}s: {announcement_text}"
                )
                voice_samples = generate_voice_announcement(
                    announcement_text, temp_dir, cache
                )
                audio_samples.extend(voice_samples)

        # Add silence until interval end time
        current_audio_duration = len(audio_samples) / AudioConstants.SAMPLE_RATE
        silence_duration = interval_end_time - current_audio_duration
        if silence_duration > 0:
            audio_samples.extend(generate_silence(silence_duration))

        # Add beep at interval end
        if interval.move_to_next_stage_at_end:
            # Triple beep for speed change
            end_time = interval.total_duration_at_end_in_sec
            logger.info(
                f"Adding triple beep at {end_time:.1f}s "
                f"(speed change)"
            )
            audio_samples.extend(generate_triple_beep(cache=cache))
        else:
            # Single beep for normal interval end
            end_time = interval.total_duration_at_end_in_sec
            logger.info(f"Adding single beep at {end_time:.1f}s")
            audio_samples.extend(generate_beep(cache=cache))

    return audio_samples


def generate_audio_file(
    intervals: List,
    filename: str = "mas_training_audio.wav",
    config: Optional[TestConfig] = None
) -> str:
    """
    Generate the complete audio file for training.

    Args:
        intervals: List of interval parameters
        filename: Output filename for the WAV file
        config: Optional test configuration

    Returns:
        Path to generated audio file

    Raises:
        AudioGenerationError: If audio generation fails
    """
    logger.info("Generating audio timeline...")

    # Create cache if enabled
    cache = None
    if config and config.enable_cache:
        cache = AudioCache(config.cache_dir)
        logger.info(f"Cache enabled: {cache.size()} items")

    with tempfile.TemporaryDirectory() as temp_dir:
        audio_samples = create_audio_timeline(
            intervals, temp_dir, cache
        )

    logger.info(f"Exporting audio to {filename}...")
    write_wav_file(audio_samples, filename)

    duration = len(audio_samples) / AudioConstants.SAMPLE_RATE
    logger.info(f"Audio file generated: {filename}")
    logger.info(f"Total duration: {duration:.1f} seconds")

    return filename
