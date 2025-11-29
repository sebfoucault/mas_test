from dataclasses import dataclass
import re
import wave
import struct
import math
import tempfile
import os
import pyttsx3

@dataclass
class TestConfig:
    init_speed_in_km_per_hour: float
    init_speed_in_meters_per_sec: float
    interval_distance_in_meters: int
    stage_duration_in_sec: int
    stage_duration_threshold_in_sec: int
    stage_speed_increment: float
    max_speed: float

    def __init__(self, init_speed_in_km_per_hour, interval_distance_in_meters, stage_duration_in_sec, stage_duration_threshold_in_sec, stage_speed_increment, max_speed):
        self.init_speed_in_km_per_hour = init_speed_in_km_per_hour
        self.interval_distance_in_meters = interval_distance_in_meters
        self.stage_duration_in_sec = stage_duration_in_sec
        self.stage_duration_threshold_in_sec = stage_duration_threshold_in_sec
        self.stage_speed_increment = stage_speed_increment
        self.max_speed = max_speed
        self.init_speed_in_meters_per_sec = init_speed_in_km_per_hour / 3.6  # Convert km/h to m/s


@dataclass
class IntervalParams:
    duration_in_sec: int
    distance_in_meters: int
    total_duration_at_start_in_sec: int
    total_duration_at_end_in_sec: int
    total_distance_at_start_in_meters: int
    total_distance_at_end_in_meters: int
    duration_time_in_stage_at_start: int
    duration_time_in_stage_at_end: int
    speed_in_meters_per_sec: float
    speed_in_km_per_hour: float  # <-- Added
    move_to_next_stage_at_end: bool

    def __init__(self):
        self.duration_in_sec = 0
        self.distance_in_meters = 0
        self.total_duration_at_start_in_sec = 0
        self.total_duration_at_end_in_sec = 0
        self.total_distance_at_start_in_meters = 0
        self.total_distance_at_end_in_meters = 0
        self.speed_in_meters_per_sec = 0
        self.speed_in_km_per_hour = 0  # <-- Added
        self.move_to_next_stage_at_end = False


def duration_from_speed_and_distance(speed: float, distance: float) -> float:
    if speed == 0:
        return float('inf')  # If speed is 0, duration is infinite
    return distance / speed


def create_init_interval(config: TestConfig) -> IntervalParams:
    ival = IntervalParams()
    ival.duration_in_sec = duration_from_speed_and_distance(config.init_speed_in_meters_per_sec, config.interval_distance_in_meters)
    ival.distance_in_meters = config.interval_distance_in_meters
    ival.total_duration_at_start_in_sec = 0
    ival.total_duration_at_end_in_sec = ival.duration_in_sec
    ival.total_distance_at_start_in_meters = 0
    ival.total_distance_at_end_in_meters = ival.distance_in_meters
    ival.speed_in_meters_per_sec = config.init_speed_in_meters_per_sec
    ival.speed_in_km_per_hour = config.init_speed_in_meters_per_sec * 3.6  # <-- Added
    ival.duration_time_in_stage_at_start = 0
    ival.duration_time_in_stage_at_end = ival.duration_in_sec
    ival.move_to_next_stage_at_end = False
    return ival


def create_next_interval(previous_interval: IntervalParams, config: TestConfig) -> IntervalParams:
    ival = IntervalParams()

    if previous_interval.move_to_next_stage_at_end:
        ival.speed_in_km_per_hour = previous_interval.speed_in_km_per_hour + config.stage_speed_increment
    else:
        ival.speed_in_km_per_hour = previous_interval.speed_in_km_per_hour
    ival.speed_in_meters_per_sec = ival.speed_in_km_per_hour / 3.6  # <-- Added

    ival.distance_in_meters = config.interval_distance_in_meters
    ival.duration_in_sec = duration_from_speed_and_distance(ival.speed_in_meters_per_sec, config.interval_distance_in_meters)
    ival.distance_in_meters = config.interval_distance_in_meters
    ival.total_duration_at_start_in_sec = previous_interval.total_duration_at_end_in_sec
    ival.total_duration_at_end_in_sec = ival.total_duration_at_start_in_sec + ival.duration_in_sec
    ival.total_distance_at_start_in_meters = previous_interval.total_distance_at_end_in_meters
    ival.total_distance_at_end_in_meters = ival.total_distance_at_start_in_meters + ival.distance_in_meters
    ival.duration_time_in_stage_at_start = previous_interval.duration_time_in_stage_at_end if not previous_interval.move_to_next_stage_at_end else 0
    ival.duration_time_in_stage_at_end = ival.duration_time_in_stage_at_start + ival.duration_in_sec

    ival.move_to_next_stage_at_end = move_to_next_stage(ival, config)
    return ival


def move_to_next_stage(current_interval: IntervalParams, config: TestConfig) -> IntervalParams:
    stage_duration = current_interval.duration_time_in_stage_at_end
    return stage_duration > config.stage_duration_in_sec or abs(stage_duration - config.stage_duration_in_sec) < config.stage_duration_threshold_in_sec


def print_intervals_table(intervals, columns):
    # Print header
    header = ""
    for _, title, fmt in columns:
        # Extract width using regex, fallback to 12
        m = re.search(r'<(\d+)', fmt)
        width = int(m.group(1)) if m else 12
        header += f"{title:<{width}}"
    print(header)
    # Print rows
    for i, interval in enumerate(intervals):
        row = ""
        for attr, _, fmt in columns:
            value = getattr(interval, attr) if attr != "index" else i
            # Format floats with .2f if specified
            if isinstance(value, float) and ".2f" in fmt:
                row += f"{value:{fmt}}"
            else:
                row += f"{value!s:{fmt}}"
        print(row)


test_config = TestConfig(
    init_speed_in_km_per_hour=8.0,
    interval_distance_in_meters=50,
    stage_duration_in_sec=60,
    stage_duration_threshold_in_sec=9,
    stage_speed_increment=.5,
    max_speed=25.0
)

intervals = []


next_interval = create_init_interval(test_config)
intervals.append(next_interval)

ival = 0
while ival < 100 and next_interval.speed_in_km_per_hour <= test_config.max_speed:
    next_interval = create_next_interval(intervals[-1], test_config)
    intervals.append(next_interval)
    ival += 1

columns = [
    ("index", "Interval", "<10"),
    ("speed_in_km_per_hour", "Speed (km/h)", "<15.2f"),
    ("duration_in_sec", "Duration (s)", "<15.2f"),
    ("distance_in_meters", "Distance (m)", "<15"),
    ("total_duration_at_end_in_sec", "Total Duration (s)", "<20.2f"),
    ("total_distance_at_end_in_meters", "Total Distance (m)", "<20"),
    ("speed_in_meters_per_sec", "Speed (m/s)", "<15.2f"),
    ("move_to_next_stage_at_end", "Speed Change?", "<15"),
    ("duration_time_in_stage_at_end", "Time In Stage (s)", "<18.2f"),
]

print_intervals_table(intervals, columns)


def generate_sine_wave(frequency, duration, sample_rate=44100, amplitude=0.3):
    """Generate a sine wave as a list of samples."""
    samples = []
    num_samples = int(sample_rate * duration)
    for i in range(num_samples):
        t = i / sample_rate
        sample = amplitude * math.sin(2 * math.pi * frequency * t)
        samples.append(int(sample * 32767))  # Convert to 16-bit integer
    return samples


def generate_silence(duration, sample_rate=44100):
    """Generate silence as a list of samples."""
    return [0] * int(sample_rate * duration)


def generate_beep(frequency=800, duration=0.2, sample_rate=44100):
    """Generate a single beep sound."""
    return generate_sine_wave(frequency, duration, sample_rate)


def generate_triple_beep(frequency=800, beep_duration=0.2, pause_duration=0.1):
    """Generate three beeps with pauses between them."""
    beep = generate_beep(frequency, beep_duration)
    pause = generate_silence(pause_duration)
    return beep + pause + beep + pause + beep


def generate_voice_announcement(text, temp_dir):
    """Generate voice announcement using pyttsx3."""
    try:
        # Initialize the TTS engine
        engine = pyttsx3.init()

        # Set properties for natural speech
        engine.setProperty('rate', 150)    # Speed of speech
        engine.setProperty('volume', 0.9)  # Volume level (0.0 to 1.0)

        # Try to set a female voice if available
        voices = engine.getProperty('voices')
        for voice in voices:
            if 'female' in voice.name.lower() or 'zira' in voice.name.lower():
                engine.setProperty('voice', voice.id)
                break

        engine.setProperty('rate', 175)  # Normal speech rate

        # Create temporary file for TTS output
        import time
        import random
        timestamp = str(int(time.time() * 1000))
        random_suffix = str(random.randint(1000, 9999))
        temp_wav = os.path.join(temp_dir, f"temp_voice_{timestamp}_{random_suffix}.wav")

        # Save speech to file
        engine.save_to_file(text, temp_wav)
        engine.runAndWait()

        # Read the generated WAV file
        if os.path.exists(temp_wav):
            try:
                with wave.open(temp_wav, 'rb') as wav_file:
                    frames = wav_file.readframes(wav_file.getnframes())
                    sample_rate = wav_file.getframerate()
                    channels = wav_file.getnchannels()

                    print(f"pyttsx3 audio: {sample_rate} Hz, {channels} channel(s)")

                    # Convert to list of integers
                    if channels == 1:
                        samples = list(struct.unpack('<' + 'h' * (len(frames) // 2), frames))
                    else:
                        # Convert stereo to mono by averaging channels
                        stereo_samples = list(struct.unpack('<' + 'h' * (len(frames) // 2), frames))
                        samples = []
                        for i in range(0, len(stereo_samples), 2):
                            if i + 1 < len(stereo_samples):
                                mono_sample = (stereo_samples[i] + stereo_samples[i + 1]) // 2
                                samples.append(mono_sample)
                            else:
                                samples.append(stereo_samples[i])

                    # Resample to 44100 Hz if needed
                    if sample_rate != 44100:
                        samples = resample_audio(samples, sample_rate, 44100)
                        print(f"Resampled from {sample_rate} Hz to 44100 Hz")

                    return samples
            finally:
                # Clean up temp file
                if os.path.exists(temp_wav):
                    try:
                        os.remove(temp_wav)
                    except:
                        pass
        else:
            print("TTS audio file was not created")
            return generate_silence(2.0)

    except Exception as e:
        print(f"pyttsx3 error: {e}. Using silence instead.")
        return generate_silence(2.0)


def resample_audio(samples, original_rate, target_rate):
    """Simple audio resampling."""
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
            interpolated = int(samples[index_floor] * (1 - weight) + samples[index_ceil] * weight)
            resampled.append(interpolated)

    return resampled


def write_wav_file(samples, filename, sample_rate=44100):
    """Write samples to a WAV file."""
    with wave.open(filename, 'wb') as wav_file:
        wav_file.setnchannels(1)  # Mono
        wav_file.setsampwidth(2)  # 16-bit
        wav_file.setframerate(sample_rate)

        # Ensure all samples are within 16-bit range
        clipped_samples = []
        for sample in samples:
            if sample > 32767:
                clipped_samples.append(32767)
            elif sample < -32768:
                clipped_samples.append(-32768)
            else:
                clipped_samples.append(int(sample))

        # Convert samples to bytes
        frames = struct.pack('<' + 'h' * len(clipped_samples), *clipped_samples)
        wav_file.writeframes(frames)


def create_audio_timeline(intervals, output_filename="mas_audio.wav"):
    """Create the complete audio timeline with beeps and voice announcements."""
    print("Generating audio timeline...")

    sample_rate = 44100
    audio_samples = []

    # Create a temporary directory for voice files
    with tempfile.TemporaryDirectory() as temp_dir:
        current_time = 0.0

        # Add "starting test" announcement at the very beginning
        print("Adding 'starting test' announcement at the beginning")
        starting_announcement = "Starting test"
        starting_voice_samples = generate_voice_announcement(starting_announcement, temp_dir)
        audio_samples.extend(starting_voice_samples)
        current_time += len(starting_voice_samples) / sample_rate

        # Add a short pause after the starting announcement
        pause_duration = 2.0  # 2 seconds pause
        audio_samples.extend(generate_silence(pause_duration, sample_rate))
        current_time += pause_duration

        for i, interval in enumerate(intervals):
            # Calculate the time until this interval ends (adjusted for starting announcement)
            target_time = interval.total_duration_at_end_in_sec

            # Check if we need a voice announcement 10 seconds before speed change
            if interval.move_to_next_stage_at_end and i < len(intervals) - 1:
                next_interval = intervals[i + 1]
                voice_time = target_time - 10  # 10 seconds before

                if voice_time > current_time and voice_time > 0:
                    # Add silence until voice announcement time
                    silence_duration = voice_time - current_time
                    silence_samples = int(silence_duration * sample_rate)
                    audio_samples.extend([0] * silence_samples)
                    current_time = voice_time

                    # Add voice announcement
                    speed_value = next_interval.speed_in_km_per_hour
                    announcement_text = f"Next speed... {speed_value:.1f}... kilometers per hour"
                    print(f"Adding voice announcement at {voice_time:.1f}s: {announcement_text}")
                    voice_samples = generate_voice_announcement(announcement_text, temp_dir)
                    audio_samples.extend(voice_samples)
                    current_time += len(voice_samples) / sample_rate

            # Add silence until the interval end time
            if target_time > current_time:
                silence_duration = target_time - current_time
                silence_samples = int(silence_duration * sample_rate)
                audio_samples.extend([0] * silence_samples)
                current_time = target_time

            # Add beep(s) at interval end
            if interval.move_to_next_stage_at_end:
                # Triple beep for speed change
                beep_samples = generate_triple_beep()
                print(f"Adding triple beep at {interval.total_duration_at_end_in_sec:.1f}s (speed change)")
            else:
                # Single beep for normal interval
                beep_samples = generate_beep()
                print(f"Adding single beep at {interval.total_duration_at_end_in_sec:.1f}s")

            audio_samples.extend(beep_samples)
            current_time += len(beep_samples) / sample_rate

    # Write the final audio file
    print(f"Exporting audio to {output_filename}...")
    write_wav_file(audio_samples, output_filename, sample_rate)
    print(f"Audio file generated: {output_filename}")
    print(f"Total duration: {len(audio_samples) / sample_rate:.1f} seconds")

    return output_filename


# Generate the audio file
if __name__ == "__main__":
    create_audio_timeline(intervals, "mas_training_audio.wav")

