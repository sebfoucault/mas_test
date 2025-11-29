"""
Unit tests for intervals module.
"""

import sys
import unittest
from pathlib import Path

# Add src directory to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from config import TestConfig  # noqa: E402
from intervals import (  # noqa: E402
    IntervalParams,
    duration_from_speed_and_distance,
    create_initial_interval,
    create_next_interval,
    move_to_next_stage,
    generate_intervals
)


class TestDurationFromSpeedAndDistance(unittest.TestCase):
    """Tests for duration_from_speed_and_distance function."""

    def test_normal_calculation(self):
        """Test normal duration calculation."""
        speed = 10.0  # m/s
        distance = 100  # meters
        expected_duration = 10.0  # seconds
        result = duration_from_speed_and_distance(speed, distance)
        self.assertEqual(result, expected_duration)

    def test_with_decimal_values(self):
        """Test with decimal values."""
        speed = 2.5  # m/s
        distance = 50  # meters
        expected_duration = 20.0  # seconds
        result = duration_from_speed_and_distance(speed, distance)
        self.assertEqual(result, expected_duration)

    def test_fractional_result(self):
        """Test when result is fractional."""
        speed = 3.0  # m/s
        distance = 50  # meters
        expected_duration = 16.666666666666668  # seconds
        self.assertAlmostEqual(
            duration_from_speed_and_distance(speed, distance),
            expected_duration,
            places=10
        )


class TestIntervalParams(unittest.TestCase):
    """Tests for IntervalParams dataclass."""

    def test_initialization(self):
        """Test IntervalParams initializes with zero values."""
        params = IntervalParams()
        self.assertEqual(params.duration_in_sec, 0)
        self.assertEqual(params.distance_in_meters, 0)
        self.assertEqual(params.total_duration_at_start_in_sec, 0)
        self.assertEqual(params.total_duration_at_end_in_sec, 0)
        self.assertEqual(params.total_distance_at_start_in_meters, 0)
        self.assertEqual(params.total_distance_at_end_in_meters, 0)
        self.assertEqual(params.speed_in_meters_per_sec, 0)
        self.assertEqual(params.speed_in_km_per_hour, 0)
        self.assertEqual(params.duration_time_in_stage_at_start, 0)
        self.assertEqual(params.duration_time_in_stage_at_end, 0)
        self.assertFalse(params.move_to_next_stage_at_end)


class TestCreateInitialInterval(unittest.TestCase):
    """Tests for create_initial_interval function."""

    def test_basic_interval_creation(self):
        """Test creating initial interval with basic configuration."""
        config = TestConfig(
            init_speed_in_km_per_hour=10.0,
            interval_distance_in_meters=50,
            stage_duration_in_sec=60,
            stage_duration_threshold_in_sec=5,
            stage_speed_increment=0.5,
            max_speed=20.0
        )

        interval = create_initial_interval(config)

        # Verify basic properties
        self.assertEqual(interval.distance_in_meters, 50)
        self.assertAlmostEqual(
            interval.speed_in_km_per_hour, 10.0, places=2
        )
        expected_speed_mps = 10.0 / 3.6
        self.assertAlmostEqual(
            interval.speed_in_meters_per_sec, expected_speed_mps, places=2
        )

        # Verify timing
        self.assertEqual(interval.total_duration_at_start_in_sec, 0)
        self.assertGreater(interval.total_duration_at_end_in_sec, 0)
        self.assertEqual(interval.duration_time_in_stage_at_start, 0)

        # Verify distance
        self.assertEqual(interval.total_distance_at_start_in_meters, 0)
        self.assertEqual(interval.total_distance_at_end_in_meters, 50)

    def test_speed_conversion(self):
        """Test km/h to m/s conversion in initial interval."""
        config = TestConfig(
            init_speed_in_km_per_hour=36.0,  # 10 m/s
            interval_distance_in_meters=100,
            stage_duration_in_sec=60,
            stage_duration_threshold_in_sec=5,
            stage_speed_increment=0.5,
            max_speed=40.0
        )

        interval = create_initial_interval(config)

        self.assertAlmostEqual(
            interval.speed_in_meters_per_sec, 10.0, places=2
        )
        self.assertAlmostEqual(interval.duration_in_sec, 10.0, places=2)


class TestMoveToNextStage(unittest.TestCase):
    """Tests for move_to_next_stage function."""

    def test_move_when_exceeds_stage_duration(self):
        """Test moving to next stage when duration exceeds threshold."""
        config = TestConfig(
            init_speed_in_km_per_hour=10.0,
            interval_distance_in_meters=50,
            stage_duration_in_sec=60,
            stage_duration_threshold_in_sec=5,
            stage_speed_increment=0.5,
            max_speed=20.0
        )

        interval = IntervalParams()
        interval.duration_time_in_stage_at_end = 65  # Exceeds 60

        self.assertTrue(move_to_next_stage(interval, config))

    def test_move_when_within_threshold(self):
        """Test moving to next stage when within threshold."""
        config = TestConfig(
            init_speed_in_km_per_hour=10.0,
            interval_distance_in_meters=50,
            stage_duration_in_sec=60,
            stage_duration_threshold_in_sec=5,
            stage_speed_increment=0.5,
            max_speed=20.0
        )

        interval = IntervalParams()
        interval.duration_time_in_stage_at_end = 58  # Within threshold

        self.assertTrue(move_to_next_stage(interval, config))

    def test_no_move_when_below_threshold(self):
        """Test not moving when below threshold."""
        config = TestConfig(
            init_speed_in_km_per_hour=10.0,
            interval_distance_in_meters=50,
            stage_duration_in_sec=60,
            stage_duration_threshold_in_sec=5,
            stage_speed_increment=0.5,
            max_speed=20.0
        )

        interval = IntervalParams()
        interval.duration_time_in_stage_at_end = 50  # Below threshold

        self.assertFalse(move_to_next_stage(interval, config))


class TestCreateNextInterval(unittest.TestCase):
    """Tests for create_next_interval function."""

    def test_next_interval_same_speed(self):
        """Test creating next interval with same speed."""
        config = TestConfig(
            init_speed_in_km_per_hour=10.0,
            interval_distance_in_meters=50,
            stage_duration_in_sec=60,
            stage_duration_threshold_in_sec=5,
            stage_speed_increment=0.5,
            max_speed=20.0
        )

        prev_interval = create_initial_interval(config)
        prev_interval.move_to_next_stage_at_end = False

        next_interval = create_next_interval(prev_interval, config)

        # Speed should remain the same
        self.assertAlmostEqual(
            next_interval.speed_in_km_per_hour,
            prev_interval.speed_in_km_per_hour,
            places=2
        )

        # Cumulative totals should increase
        self.assertGreater(
            next_interval.total_duration_at_end_in_sec,
            prev_interval.total_duration_at_end_in_sec
        )
        self.assertGreater(
            next_interval.total_distance_at_end_in_meters,
            prev_interval.total_distance_at_end_in_meters
        )

    def test_next_interval_increased_speed(self):
        """Test creating next interval with increased speed."""
        config = TestConfig(
            init_speed_in_km_per_hour=10.0,
            interval_distance_in_meters=50,
            stage_duration_in_sec=60,
            stage_duration_threshold_in_sec=5,
            stage_speed_increment=0.5,
            max_speed=20.0
        )

        prev_interval = create_initial_interval(config)
        prev_interval.move_to_next_stage_at_end = True

        next_interval = create_next_interval(prev_interval, config)

        # Speed should increase
        self.assertAlmostEqual(
            next_interval.speed_in_km_per_hour,
            prev_interval.speed_in_km_per_hour + 0.5,
            places=2
        )

        # Stage time should reset
        self.assertLess(
            next_interval.duration_time_in_stage_at_end,
            prev_interval.duration_time_in_stage_at_end
        )

    def test_cumulative_values(self):
        """Test that cumulative values are correctly calculated."""
        config = TestConfig(
            init_speed_in_km_per_hour=10.0,
            interval_distance_in_meters=50,
            stage_duration_in_sec=60,
            stage_duration_threshold_in_sec=5,
            stage_speed_increment=0.5,
            max_speed=20.0
        )

        interval1 = create_initial_interval(config)
        interval2 = create_next_interval(interval1, config)

        # Check cumulative distance
        self.assertEqual(
            interval2.total_distance_at_start_in_meters,
            interval1.total_distance_at_end_in_meters
        )
        self.assertEqual(
            interval2.total_distance_at_end_in_meters,
            interval1.total_distance_at_end_in_meters + 50
        )

        # Check cumulative duration
        self.assertAlmostEqual(
            interval2.total_duration_at_start_in_sec,
            interval1.total_duration_at_end_in_sec,
            places=2
        )


class TestGenerateIntervals(unittest.TestCase):
    """Tests for generate_intervals function."""

    def test_basic_interval_generation(self):
        """Test generating intervals with basic configuration."""
        config = TestConfig(
            init_speed_in_km_per_hour=8.0,
            interval_distance_in_meters=50,
            stage_duration_in_sec=60,
            stage_duration_threshold_in_sec=5,
            stage_speed_increment=0.5,
            max_speed=10.0
        )

        intervals = generate_intervals(config)

        # Should generate multiple intervals
        self.assertGreater(len(intervals), 1)

        # First interval should have correct initial speed
        self.assertAlmostEqual(
            intervals[0].speed_in_km_per_hour, 8.0, places=2
        )

        # Last interval may exceed max speed by one increment
        self.assertLessEqual(
            intervals[-1].speed_in_km_per_hour,
            config.max_speed + config.stage_speed_increment
        )

    def test_speed_progression(self):
        """Test that speed increases correctly through stages."""
        config = TestConfig(
            init_speed_in_km_per_hour=8.0,
            interval_distance_in_meters=50,
            stage_duration_in_sec=60,
            stage_duration_threshold_in_sec=5,
            stage_speed_increment=0.5,
            max_speed=10.0
        )

        intervals = generate_intervals(config)

        # Find where speed changes occur
        speeds = [interval.speed_in_km_per_hour for interval in intervals]
        unique_speeds = sorted(set(speeds))

        # Verify speed increments
        for i in range(1, len(unique_speeds)):
            self.assertAlmostEqual(
                unique_speeds[i] - unique_speeds[i-1],
                0.5,
                places=2
            )

    def test_max_speed_limit(self):
        """Test that generation stops at max speed."""
        config = TestConfig(
            init_speed_in_km_per_hour=8.0,
            interval_distance_in_meters=50,
            stage_duration_in_sec=60,
            stage_duration_threshold_in_sec=5,
            stage_speed_increment=0.5,
            max_speed=9.0
        )

        intervals = generate_intervals(config)

        # No interval should exceed max speed by more than one increment
        for interval in intervals:
            self.assertLessEqual(
                interval.speed_in_km_per_hour,
                config.max_speed + config.stage_speed_increment
            )

    def test_distance_accumulation(self):
        """Test that distances accumulate correctly."""
        config = TestConfig(
            init_speed_in_km_per_hour=10.0,
            interval_distance_in_meters=50,
            stage_duration_in_sec=60,
            stage_duration_threshold_in_sec=5,
            stage_speed_increment=0.5,
            max_speed=12.0
        )

        intervals = generate_intervals(config)

        # Each interval should add exactly 50 meters
        for i, interval in enumerate(intervals):
            expected_distance = (i + 1) * 50
            self.assertEqual(
                interval.total_distance_at_end_in_meters,
                expected_distance
            )

    def test_duration_accumulation(self):
        """Test that durations accumulate correctly."""
        config = TestConfig(
            init_speed_in_km_per_hour=10.0,
            interval_distance_in_meters=50,
            stage_duration_in_sec=60,
            stage_duration_threshold_in_sec=5,
            stage_speed_increment=0.5,
            max_speed=11.0
        )

        intervals = generate_intervals(config)

        # Duration should be monotonically increasing
        for i in range(1, len(intervals)):
            self.assertGreater(
                intervals[i].total_duration_at_end_in_sec,
                intervals[i-1].total_duration_at_end_in_sec
            )


if __name__ == '__main__':
    unittest.main()
