"""
Interval generation module for MAS Training Audio Generator.
Handles calculation of training intervals and speed progressions.
"""

import logging
from dataclasses import dataclass
from typing import List

from config import TestConfig
from exceptions import IntervalGenerationError

logger = logging.getLogger(__name__)


@dataclass
class IntervalParams:
    """Parameters for a single training interval."""

    duration_in_sec: int
    distance_in_meters: int
    total_duration_at_start_in_sec: int
    total_duration_at_end_in_sec: int
    total_distance_at_start_in_meters: int
    total_distance_at_end_in_meters: int
    duration_time_in_stage_at_start: int
    duration_time_in_stage_at_end: int
    speed_in_meters_per_sec: float
    speed_in_km_per_hour: float
    move_to_next_stage_at_end: bool

    def __init__(self):
        self.duration_in_sec = 0
        self.distance_in_meters = 0
        self.total_duration_at_start_in_sec = 0
        self.total_duration_at_end_in_sec = 0
        self.total_distance_at_start_in_meters = 0
        self.total_distance_at_end_in_meters = 0
        self.speed_in_meters_per_sec = 0
        self.speed_in_km_per_hour = 0
        self.duration_time_in_stage_at_start = 0
        self.duration_time_in_stage_at_end = 0
        self.move_to_next_stage_at_end = False


def duration_from_speed_and_distance(
    speed_in_m_per_sec: float,
    distance_in_meters: int
) -> float:
    """
    Calculate duration from speed and distance.

    Args:
        speed_in_m_per_sec: Speed in meters per second
        distance_in_meters: Distance in meters

    Returns:
        Duration in seconds

    Raises:
        IntervalGenerationError: If speed is zero or negative
    """
    if speed_in_m_per_sec <= 0:
        raise IntervalGenerationError(
            f"Speed must be positive, got {speed_in_m_per_sec}"
        )
    return distance_in_meters / speed_in_m_per_sec


def create_initial_interval(config: TestConfig) -> IntervalParams:
    """
    Create the first interval with initial parameters.

    Args:
        config: Test configuration

    Returns:
        Initial interval parameters
    """
    logger.debug(
        f"Creating initial interval: distance={config.interval_distance_in_meters}m, "
        f"speed={config.init_speed_in_meters_per_sec}m/s"
    )

    ival = IntervalParams()
    ival.distance_in_meters = config.interval_distance_in_meters
    ival.speed_in_meters_per_sec = config.init_speed_in_meters_per_sec
    ival.duration_in_sec = duration_from_speed_and_distance(
        config.init_speed_in_meters_per_sec,
        config.interval_distance_in_meters
    )
    ival.total_duration_at_start_in_sec = 0
    ival.total_duration_at_end_in_sec = ival.duration_in_sec
    ival.total_distance_at_start_in_meters = 0
    ival.total_distance_at_end_in_meters = ival.distance_in_meters
    ival.speed_in_km_per_hour = config.init_speed_in_meters_per_sec * 3.6
    ival.duration_time_in_stage_at_start = 0
    ival.duration_time_in_stage_at_end = ival.duration_in_sec
    ival.move_to_next_stage_at_end = move_to_next_stage(ival, config)
    return ival


def create_next_interval(previous_interval: IntervalParams,
                         config: TestConfig) -> IntervalParams:
    """
    Create the next interval based on the previous one.

    Args:
        previous_interval: Previous interval parameters
        config: Test configuration

    Returns:
        Next interval parameters
    """
    ival = IntervalParams()
    ival.distance_in_meters = config.interval_distance_in_meters

    if previous_interval.move_to_next_stage_at_end:
        ival.speed_in_km_per_hour = (previous_interval.speed_in_km_per_hour +
                                     config.stage_speed_increment)
    else:
        ival.speed_in_km_per_hour = previous_interval.speed_in_km_per_hour

    ival.speed_in_meters_per_sec = ival.speed_in_km_per_hour / 3.6
    ival.duration_in_sec = duration_from_speed_and_distance(
        ival.speed_in_meters_per_sec,
        config.interval_distance_in_meters
    )
    ival.total_duration_at_start_in_sec = previous_interval.total_duration_at_end_in_sec
    ival.total_duration_at_end_in_sec = (ival.total_duration_at_start_in_sec +
                                         ival.duration_in_sec)
    ival.total_distance_at_start_in_meters = previous_interval.total_distance_at_end_in_meters
    ival.total_distance_at_end_in_meters = (ival.total_distance_at_start_in_meters +
                                            ival.distance_in_meters)
    ival.duration_time_in_stage_at_start = (
        previous_interval.duration_time_in_stage_at_end
        if not previous_interval.move_to_next_stage_at_end else 0
    )
    ival.duration_time_in_stage_at_end = (ival.duration_time_in_stage_at_start +
                                          ival.duration_in_sec)
    ival.move_to_next_stage_at_end = move_to_next_stage(ival, config)
    return ival


def move_to_next_stage(current_interval: IntervalParams,
                       config: TestConfig) -> bool:
    """
    Determine if we should move to the next stage.

    Args:
        current_interval: Current interval parameters
        config: Test configuration

    Returns:
        True if should move to next stage, False otherwise
    """
    stage_duration = current_interval.duration_time_in_stage_at_end
    return (stage_duration > config.stage_duration_in_sec or
            abs(stage_duration - config.stage_duration_in_sec) <
            config.stage_duration_threshold_in_sec)


def generate_intervals(config: TestConfig) -> List[IntervalParams]:
    """
    Generate all training intervals based on configuration.

    Args:
        config: Test configuration

    Returns:
        List of interval parameters

    Raises:
        IntervalGenerationError: If maximum iterations reached
    """
    logger.info("Generating intervals...")
    intervals = []

    # Create initial interval
    initial_interval = create_initial_interval(config)
    intervals.append(initial_interval)

    # Generate subsequent intervals
    max_iterations = 100
    ival = 1
    next_interval = initial_interval

    while ival < max_iterations and next_interval.speed_in_km_per_hour <= config.max_speed:
        next_interval = create_next_interval(intervals[-1], config)
        intervals.append(next_interval)
        ival += 1

    if ival >= max_iterations:
        logger.warning(
            f"Maximum iterations ({max_iterations}) reached during interval generation"
        )

    logger.info(f"Generated {len(intervals)} intervals")
    return intervals


def print_intervals_table(intervals: List[IntervalParams]) -> None:
    """
    Print a formatted table of all intervals.

    Args:
        intervals: List of interval parameters to display
    """
    # Define column widths
    col_widths = {
        'interval': 8,
        'speed_kmh': 12,
        'duration': 11,
        'distance': 11,
        'total_dur': 20,  # Increased for min:ss.sss format
        'total_dist': 13,
        'speed_ms': 11,
        'change': 7,
        'stage_time': 12
    }

    # Calculate total width
    total_width = sum(col_widths.values()) + len(col_widths) * 3 + 1

    # Top border
    print("┌" + "─" * (total_width - 2) + "┐")

    # Title
    title = "INTERVAL TRAINING SCHEDULE"
    padding = (total_width - len(title) - 2) // 2
    print(f"│{' ' * padding}{title}{' ' * (total_width - len(title) - padding - 2)}│")

    # Header separator
    print("├" + "─" * (total_width - 2) + "┤")

    # Header
    header = (
        f"│ {'#':<{col_widths['interval']}} │ "
        f"{'Speed':<{col_widths['speed_kmh']}} │ "
        f"{'Duration':<{col_widths['duration']}} │ "
        f"{'Distance':<{col_widths['distance']}} │ "
        f"{'Total Time':<{col_widths['total_dur']}} │ "
        f"{'Total Dist':<{col_widths['total_dist']}} │ "
        f"{'Speed':<{col_widths['speed_ms']}} │ "
        f"{'Change':<{col_widths['change']}} │ "
        f"{'Stage':<{col_widths['stage_time']}} │"
    )
    print(header)

    # Subheader with units
    subheader = (
        f"│ {'':<{col_widths['interval']}} │ "
        f"{'(km/h)':<{col_widths['speed_kmh']}} │ "
        f"{'(s)':<{col_widths['duration']}} │ "
        f"{'(m)':<{col_widths['distance']}} │ "
        f"{'(min:ss.sss)':<{col_widths['total_dur']}} │ "
        f"{'(m)':<{col_widths['total_dist']}} │ "
        f"{'(m/s)':<{col_widths['speed_ms']}} │ "
        f"{'?':<{col_widths['change']}} │ "
        f"{'Time (s)':<{col_widths['stage_time']}} │"
    )
    print(subheader)

    # Header separator
    print("├" + "─" * (total_width - 2) + "┤")

    # Intervals with alternating separators for speed changes
    for i, interval in enumerate(intervals):
        # Format change indicator
        change_indicator = "★" if interval.move_to_next_stage_at_end else ""

        # Format total time as min:ss.sss (ss.sss)
        total_sec = interval.total_duration_at_end_in_sec
        minutes = int(total_sec // 60)
        seconds = total_sec % 60
        time_formatted = f"{minutes}:{seconds:06.3f} ({total_sec:.2f}s)"

        row = (
            f"│ {i:<{col_widths['interval']}} │ "
            f"{interval.speed_in_km_per_hour:<{col_widths['speed_kmh']}.2f} │ "
            f"{interval.duration_in_sec:<{col_widths['duration']}.2f} │ "
            f"{interval.distance_in_meters:<{col_widths['distance']}} │ "
            f"{time_formatted:<{col_widths['total_dur']}} │ "
            f"{interval.total_distance_at_end_in_meters:<{col_widths['total_dist']}} │ "
            f"{interval.speed_in_meters_per_sec:<{col_widths['speed_ms']}.2f} │ "
            f"{change_indicator:^{col_widths['change']}} │ "
            f"{interval.duration_time_in_stage_at_end:<{col_widths['stage_time']}.2f} │"
        )
        print(row)

        # Add visual separator for speed changes
        if interval.move_to_next_stage_at_end and i < len(intervals) - 1:
            print("├" + "┄" * (total_width - 2) + "┤")

    # Bottom border
    print("└" + "─" * (total_width - 2) + "┘")

    # Summary
    total_duration = intervals[-1].total_duration_at_end_in_sec if intervals else 0
    total_distance = intervals[-1].total_distance_at_end_in_meters if intervals else 0
    print(f"\n📊 Summary: {len(intervals)} intervals | "
          f"Total time: {total_duration:.1f}s ({total_duration/60:.1f}min) | "
          f"Total distance: {total_distance}m ({total_distance/1000:.2f}km)")
