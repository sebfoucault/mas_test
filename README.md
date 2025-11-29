# MAS Training Audio Generator

A Python application that generates audio training files for athletic interval training with voice announcements and timing beeps.

## Features

- **Interval Calculation**: Automatically calculates training intervals based on speed progression
- **Voice Announcements**: Natural text-to-speech voice guidance using Windows SAPI
- **Audio Timing**:
  - Single beeps at the end of each interval
  - Triple beeps when speed changes
  - Voice announcements 10 seconds before speed changes
  - Starting test announcement
- **Cross-platform Audio**: Generates standard WAV files (44.1kHz, 16-bit, mono)

## Requirements

- Python 3.7+ (tested with Python 3.13)
- Windows OS (for pyttsx3 voice synthesis)

## Installation

1. Clone or download this repository
2. Create a virtual environment:
   ```bash
   python -m venv .venv
   ```
3. Activate the virtual environment:
   ```bash
   # Windows
   .venv\Scripts\activate
   ```
4. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

### Basic Usage

Run the application with default settings:
```bash
python mas_main.py
```

### Command Line Options

View all available options:
```bash
python mas_main.py --help
```

### Examples

**Generate audio with custom speed range:**
```bash
python mas_main.py --init-speed 10 --max-speed 15
```

**Create a shorter training session:**
```bash
python mas_main.py --stage-duration 30 --max-speed 12
```

**Disable caching for testing:**
```bash
python mas_main.py --no-cache
```

**Specify custom output file:**
```bash
python mas_main.py --output my_training.wav
```

**Custom cache directory:**
```bash
python mas_main.py --cache-dir my_cache
```

**Complete custom configuration:**
```bash
python mas_main.py \
  --init-speed 9.0 \
  --interval-distance 100 \
  --stage-duration 45 \
  --stage-threshold 3 \
  --speed-increment 0.3 \
  --max-speed 14.0 \
  --output custom_training.wav
```

### Command Line Arguments

| Argument | Default | Description |
|----------|---------|-------------|
| `--init-speed` | 8.0 | Initial speed in km/h |
| `--interval-distance` | 50 | Distance for each interval in meters |
| `--stage-duration` | 60 | Duration of each stage in seconds |
| `--stage-threshold` | 5 | Threshold for stage duration in seconds |
| `--speed-increment` | 0.5 | Speed increment between stages in km/h |
| `--max-speed` | 20.0 | Maximum speed in km/h |
| `--enable-cache` | True | Enable audio sample caching |
| `--no-cache` | - | Disable audio sample caching |
| `--cache-dir` | .cache | Directory for cache storage |
| `--output, -o` | mas_training_audio.wav | Output audio file name |

### Audio Caching

The application caches generated audio samples (voice announcements and beeps) to improve performance on subsequent runs. The cache provides approximately **80% performance improvement** on repeated generations.

- **Enable cache (default)**: Audio samples are cached in `.cache` directory
- **Disable cache**: Use `--no-cache` flag
- **Custom cache location**: Use `--cache-dir` argument

This will:
1. Calculate training intervals based on the configured parameters
2. Generate voice announcements and timing beeps
3. Create audio file for your training session

## Configuration

### Programmatic Configuration

Edit the training parameters in `mas_main.py`:

```python
test_config = TestConfig(
    init_speed_in_km_per_hour=8.0,      # Starting speed
    interval_distance_in_meters=50,      # Distance per interval
    stage_duration_in_sec=60,           # Target duration per stage
    stage_duration_threshold_in_sec=5,   # Threshold for stage completion
    stage_speed_increment=0.5,          # Speed increase per stage (km/h)
    max_speed=20.0                      # Maximum speed
)
```

## Output

The application generates:
- Console output showing all calculated intervals
- `mas_training_audio.wav` - Audio file for training sessions

## Dependencies

- **pyttsx3**: Text-to-speech library for voice announcements
- **Standard Python libraries**: wave, struct, math, tempfile, os, dataclasses, re

## Audio Features

- **Sample Rate**: 44.1kHz (CD quality)
- **Bit Depth**: 16-bit
- **Channels**: Mono
- **Voice**: Natural Windows SAPI voice with configurable speed and volume
- **Timing**: Precise synchronization between voice announcements and interval timing

## Project Structure

```
mas.py/
├── mas.py              # Main application
├── requirements.txt    # Python dependencies
├── README.md          # This file
└── mas_training_audio.wav  # Generated audio file (after running)
```

## Contributing

This is a personal training tool. Feel free to fork and modify for your own needs.

## License

Open source - use as needed for personal training applications.