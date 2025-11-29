"""
MAS Training Audio Generator - Main Module

This is the main entry point for the MAS Training Audio Generator.
It orchestrates interval generation and audio creation using separate modules.
"""

import argparse
import logging
import sys
from pathlib import Path

# Add src directory to path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from audio import generate_audio_file  # noqa: E402
from config import DEFAULT_CACHE_DIR, TestConfig  # noqa: E402
from intervals import generate_intervals, print_intervals_table  # noqa: E402


def setup_logging(verbose: bool = False) -> None:
    """
    Configure logging for the application.

    Args:
        verbose: If True, set DEBUG level; otherwise INFO
    """
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(sys.stdout)
        ]
    )



def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description='Generate MAS (Maximum Aerobic Speed) training audio',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )

    # Training parameters
    parser.add_argument(
        '--init-speed',
        type=float,
        default=8.0,
        help='Initial speed in km/h'
    )
    parser.add_argument(
        '--interval-distance',
        type=int,
        default=50,
        help='Distance for each interval in meters'
    )
    parser.add_argument(
        '--stage-duration',
        type=int,
        default=60,
        help='Duration of each stage in seconds'
    )
    parser.add_argument(
        '--stage-threshold',
        type=int,
        default=5,
        help='Threshold for stage duration in seconds'
    )
    parser.add_argument(
        '--speed-increment',
        type=float,
        default=0.5,
        help='Speed increment between stages in km/h'
    )
    parser.add_argument(
        '--max-speed',
        type=float,
        default=20.0,
        help='Maximum speed in km/h'
    )

    # Cache parameters
    parser.add_argument(
        '--enable-cache',
        action='store_true',
        default=True,
        help='Enable audio sample caching'
    )
    parser.add_argument(
        '--no-cache',
        action='store_false',
        dest='enable_cache',
        help='Disable audio sample caching'
    )
    parser.add_argument(
        '--cache-dir',
        type=str,
        default=DEFAULT_CACHE_DIR,
        help='Directory for cache storage'
    )

    # Output file
    parser.add_argument(
        '--output',
        '-o',
        type=str,
        default='mas_training_audio.wav',
        help='Output audio file name'
    )

    # Logging
    parser.add_argument(
        '--verbose',
        '-v',
        action='store_true',
        help='Enable verbose logging (DEBUG level)'
    )

    return parser.parse_args()


def main():
    """Main function to generate training audio."""
    args = parse_arguments()

    # Setup logging
    setup_logging(verbose=args.verbose)
    logger = logging.getLogger(__name__)

    logger.info("MAS Training Audio Generator")
    logger.info("=" * 50)

    # Configuration for the training test
    test_config = TestConfig(
        init_speed_in_km_per_hour=args.init_speed,
        interval_distance_in_meters=args.interval_distance,
        stage_duration_in_sec=args.stage_duration,
        stage_duration_threshold_in_sec=args.stage_threshold,
        stage_speed_increment=args.speed_increment,
        max_speed=args.max_speed,
        enable_cache=args.enable_cache,
        cache_dir=args.cache_dir
    )

    print("MAS Training Audio Generator")
    print("=" * 50)
    print(f"Initial speed: {test_config.init_speed_in_km_per_hour} km/h")
    print(f"Interval distance: {test_config.interval_distance_in_meters} m")
    print(f"Stage duration: {test_config.stage_duration_in_sec} s")
    print(f"Speed increment: {test_config.stage_speed_increment} km/h")
    print(f"Max speed: {test_config.max_speed} km/h")
    print(f"Cache enabled: {test_config.enable_cache}")
    print(f"Cache directory: {test_config.cache_dir}")
    print(f"Output file: {args.output}")
    print(f"Verbose logging: {args.verbose}")
    print("=" * 50)
    print()

    # Generate intervals
    intervals = generate_intervals(test_config)

    # Print intervals table
    print_intervals_table(intervals)

    # Generate audio file
    generate_audio_file(intervals, args.output, config=test_config)

    logger.info("Generation complete!")


if __name__ == "__main__":
    main()
