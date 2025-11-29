"""
Unit tests for audio module.
"""

import sys
import unittest
import os
import tempfile
import time
from pathlib import Path

# Add src directory to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from config import TestConfig  # noqa: E402
from intervals import generate_intervals  # noqa: E402
from audio import generate_audio_file  # noqa: E402


class TestAudioCaching(unittest.TestCase):
    """Tests for audio caching functionality."""

    def setUp(self):
        """Set up test configuration."""
        self.test_config = TestConfig(
            init_speed_in_km_per_hour=8.0,
            interval_distance_in_meters=50,
            stage_duration_in_sec=20,
            stage_duration_threshold_in_sec=3,
            stage_speed_increment=0.5,
            max_speed=9.0,
            enable_cache=True
        )

    def test_audio_generation_with_cache_disabled(self):
        """Test that audio can be generated with caching disabled."""
        config = TestConfig(
            init_speed_in_km_per_hour=8.0,
            interval_distance_in_meters=50,
            stage_duration_in_sec=20,
            stage_duration_threshold_in_sec=3,
            stage_speed_increment=0.5,
            max_speed=9.0,
            enable_cache=False
        )

        intervals = generate_intervals(config)

        with tempfile.TemporaryDirectory() as tmpdir:
            output_file = os.path.join(tmpdir, "test_no_cache.wav")
            result = generate_audio_file(intervals, output_file, config)

            # Verify file was created
            self.assertTrue(os.path.exists(result))
            self.assertGreater(os.path.getsize(result), 0)

    def test_audio_generation_with_cache_enabled(self):
        """Test that audio can be generated with caching enabled."""
        config = TestConfig(
            init_speed_in_km_per_hour=8.0,
            interval_distance_in_meters=50,
            stage_duration_in_sec=20,
            stage_duration_threshold_in_sec=3,
            stage_speed_increment=0.5,
            max_speed=9.0,
            enable_cache=True
        )

        intervals = generate_intervals(config)

        with tempfile.TemporaryDirectory() as tmpdir:
            output_file = os.path.join(tmpdir, "test_with_cache.wav")
            result = generate_audio_file(intervals, output_file, config)

            # Verify file was created
            self.assertTrue(os.path.exists(result))
            self.assertGreater(os.path.getsize(result), 0)

    def test_audio_results_match_with_and_without_cache(self):
        """
        Test that audio generation produces same results
        with and without cache.
        """
        config_no_cache = TestConfig(
            init_speed_in_km_per_hour=8.0,
            interval_distance_in_meters=50,
            stage_duration_in_sec=20,
            stage_duration_threshold_in_sec=3,
            stage_speed_increment=0.5,
            max_speed=9.0,
            enable_cache=False
        )

        config_with_cache = TestConfig(
            init_speed_in_km_per_hour=8.0,
            interval_distance_in_meters=50,
            stage_duration_in_sec=20,
            stage_duration_threshold_in_sec=3,
            stage_speed_increment=0.5,
            max_speed=9.0,
            enable_cache=True
        )

        intervals = generate_intervals(config_no_cache)

        # Generate without cache
        with tempfile.TemporaryDirectory() as tmpdir:
            file_no_cache = os.path.join(tmpdir, "no_cache.wav")
            generate_audio_file(intervals, file_no_cache, config_no_cache)
            size_no_cache = os.path.getsize(file_no_cache)
            with open(file_no_cache, 'rb') as f:
                content_no_cache = f.read()

        # Generate with cache
        with tempfile.TemporaryDirectory() as tmpdir:
            file_with_cache = os.path.join(tmpdir, "with_cache.wav")
            generate_audio_file(intervals, file_with_cache, config_with_cache)
            size_with_cache = os.path.getsize(file_with_cache)
            with open(file_with_cache, 'rb') as f:
                content_with_cache = f.read()

        # Files should have same size
        self.assertEqual(
            size_no_cache, size_with_cache,
            "Audio files should have same size with/without cache"
        )

        # Files should have identical content
        self.assertEqual(
            content_no_cache, content_with_cache,
            "Audio files should have identical content"
        )

    def test_cache_performance_improvement(self):
        """
        Test that caching provides significant performance improvement
        on second run.
        """
        config_with_cache = TestConfig(
            init_speed_in_km_per_hour=8.0,
            interval_distance_in_meters=50,
            stage_duration_in_sec=20,
            stage_duration_threshold_in_sec=3,
            stage_speed_increment=0.5,
            max_speed=9.0,
            enable_cache=True,
            cache_dir=tempfile.mkdtemp()
        )

        intervals = generate_intervals(config_with_cache)

        # First run - populate cache
        with tempfile.TemporaryDirectory() as tmpdir:
            output_file1 = os.path.join(tmpdir, "first_run.wav")
            start_time = time.time()
            generate_audio_file(intervals, output_file1, config_with_cache)
            first_run_time = time.time() - start_time

        # Second run - use cache
        with tempfile.TemporaryDirectory() as tmpdir:
            output_file2 = os.path.join(tmpdir, "second_run.wav")
            start_time = time.time()
            generate_audio_file(intervals, output_file2, config_with_cache)
            second_run_time = time.time() - start_time

        print(f"\nFirst run (populating cache): {first_run_time:.2f}s")
        print(f"Second run (using cache): {second_run_time:.2f}s")
        print(
            f"Performance improvement: "
            f"{(first_run_time - second_run_time) / first_run_time * 100:.1f}%"
        )

        # Second run should be faster (at least some improvement)
        self.assertLess(
            second_run_time, first_run_time,
            "Cached run should be faster than first run"
        )

        # Clean up temp cache directory
        import shutil
        shutil.rmtree(config_with_cache.cache_dir, ignore_errors=True)


if __name__ == '__main__':
    unittest.main()
