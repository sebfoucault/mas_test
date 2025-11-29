"""
MAS Training Audio Generator - Main Module

This is the main entry point for the MAS Training Audio Generator.
It orchestrates interval generation and audio creation using separate modules.
"""

from config import TestConfig
from intervals import generate_intervals, print_intervals_table
from audio import generate_audio_file


def main():
    """Main function to generate training audio."""
    # Configuration for the training test
    test_config = TestConfig(
        init_speed_in_km_per_hour=8.0,
        interval_distance_in_meters=50,
        stage_duration_in_sec=60,
        stage_duration_threshold_in_sec=5,
        stage_speed_increment=0.5,
        max_speed=20.0
    )

    # Generate intervals
    intervals = generate_intervals(test_config)

    # Print intervals table
    print_intervals_table(intervals)

    # Generate audio file
    generate_audio_file(intervals)


if __name__ == "__main__":
    main()