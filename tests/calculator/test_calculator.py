"""Tests for sleep stage calculator."""

import os
import pickle
from datetime import datetime, timedelta
from pathlib import Path

import pytest
import pytz

from pysleep.calculator import SleepStageCalculator
from pysleep.label import WAKE, LIGHT, DEEP, REM


# Test data path configuration
# Set PYSLEEP_TEST_DATA environment variable to use a custom test data path
# Otherwise, falls back to external asleep-sleep-stage-lib repository location
TEST_DATA_PATH = Path(os.getenv("PYSLEEP_TEST_DATA",
    str(Path(__file__).parent.parent.parent / "asleep-sleep-stage-lib/test_code/data/file/sleep_data.pkl")))


@pytest.fixture
def calculator():
    """Create a calculator instance."""
    return SleepStageCalculator()


@pytest.fixture
def sleep_data():
    """Load test sleep data if available."""
    if TEST_DATA_PATH.exists():
        with open(TEST_DATA_PATH, "rb") as f:
            return pickle.load(f)
    return None


def compare_stats(result, expected, tolerance=0.003):
    """Compare sleep stage statistics with tolerance for floating point.

    Note: The result from SleepStageCalculator returns pysleep.SleepStat with
    timedelta objects for durations. This function compares the values correctly,
    converting timedelta to seconds where needed.
    """
    # Sleep index is not calculated by this calculator
    assert result.sleep_index is None

    # Compare times (datetime objects)
    assert result.start_time == expected["start_time"]
    assert result.end_time == expected["end_time"]
    assert result.sleep_time == expected["sleep_time"]
    assert result.wake_time == expected["wake_time"]

    # Compare latencies (timedelta in result, seconds in expected)
    assert result.sleep_latency.total_seconds() == expected["sleep_latency"]
    assert result.wakeup_latency.total_seconds() == expected["wakeup_latency"]

    # Handle optional latencies that might be None
    if expected["rem_latency"] is None:
        assert result.rem_latency is None
    else:
        assert result.rem_latency.total_seconds() == expected["rem_latency"]

    if expected["light_latency"] is None:
        assert result.light_latency is None
    else:
        assert result.light_latency.total_seconds() == expected["light_latency"]

    if expected["deep_latency"] is None:
        assert result.deep_latency is None
    else:
        assert result.deep_latency.total_seconds() == expected["deep_latency"]

    # Compare durations (timedelta in result, seconds in expected)
    assert result.time_in_bed.total_seconds() == expected["time_in_bed"]
    assert result.time_in_sleep_period.total_seconds() == expected["time_in_sleep_period"]
    assert result.time_in_sleep.total_seconds() == expected["time_in_sleep"]
    assert result.time_in_wake.total_seconds() == expected["time_in_wake"]
    assert result.time_in_light.total_seconds() == expected["time_in_light"]
    assert result.time_in_deep.total_seconds() == expected["time_in_deep"]
    assert result.time_in_rem.total_seconds() == expected["time_in_rem"]

    # Compare ratios
    assert abs(result.sleep_efficiency - expected["sleep_efficiency"]) < tolerance
    assert abs(result.sleep_ratio - expected["sleep_ratio"]) < tolerance
    assert abs(result.wake_ratio - expected["wake_ratio"]) < tolerance
    assert abs(result.light_ratio - expected["light_ratio"]) < tolerance
    assert abs(result.deep_ratio - expected["deep_ratio"]) < tolerance
    assert abs(result.rem_ratio - expected["rem_ratio"]) < tolerance

    # Compare clusters
    assert result.waso_count == expected["waso_count"]
    assert result.longest_waso.total_seconds() == expected["longest_waso"]

    # Handle optional sleep_cycle
    if expected["sleep_cycle"] is None:
        assert result.sleep_cycle is None
    else:
        assert result.sleep_cycle.total_seconds() == expected["sleep_cycle"]

    assert result.sleep_cycle_count == expected["sleep_cycle_count"]
    assert len(result.sleep_cycle_time) == len(expected["sleep_cycle_time"])


class TestRatioNormalization:
    """Tests for ratio normalization to ensure ratios sum exactly to 1.0."""

    def test_ratios_sum_to_one(self, calculator):
        """Test that stage ratios sum exactly to 1.0 (no floating-point drift)."""
        start = datetime(2024, 1, 1, 22, 0, 0, tzinfo=pytz.UTC)
        end = datetime(2024, 1, 2, 6, 0, 0, tzinfo=pytz.UTC)

        # Various sleep patterns
        test_cases = [
            [WAKE] * 20 + [LIGHT] * 720 + [DEEP] * 180 + [REM] * 40,  # Normal pattern
            [LIGHT] * 300 + [DEEP] * 100 + [REM] * 100,  # No wake during sleep
            [WAKE] * 10 + [LIGHT] * 333 + [DEEP] * 167 + [REM] * 100,  # Fractional divisions
        ]

        for stages in test_cases:
            result = calculator.calculate(stages, start, end)
            ratio_sum = result.wake_ratio + result.light_ratio + result.deep_ratio + result.rem_ratio

            # Exact equality check (no tolerance)
            assert ratio_sum == 1.0, f"Ratios sum to {ratio_sum}, expected exactly 1.0"

    def test_ratios_rounded_to_two_decimals(self, calculator):
        """Test that all ratios are rounded to exactly 2 decimal places."""
        start = datetime(2024, 1, 1, 22, 0, 0, tzinfo=pytz.UTC)
        end = datetime(2024, 1, 2, 6, 0, 0, tzinfo=pytz.UTC)

        # Pattern that creates fractional ratios
        stages = [WAKE] * 11 + [LIGHT] * 333 + [DEEP] * 222 + [REM] * 111
        result = calculator.calculate(stages, start, end)

        # Check each ratio has at most 2 decimal places
        for ratio_name, ratio_value in [
            ('wake_ratio', result.wake_ratio),
            ('light_ratio', result.light_ratio),
            ('deep_ratio', result.deep_ratio),
            ('rem_ratio', result.rem_ratio),
            ('sleep_ratio', result.sleep_ratio),
            ('sleep_efficiency', result.sleep_efficiency),
        ]:
            # Convert to string and check decimal places
            ratio_str = f"{ratio_value:.10f}"  # Format with many decimals
            decimal_part = ratio_str.split('.')[1].rstrip('0')  # Remove trailing zeros
            assert len(decimal_part) <= 2, f"{ratio_name} has more than 2 decimal places: {ratio_value}"

    def test_sleep_ratio_calculation(self, calculator):
        """Test that sleep_ratio = max(1 - wake_ratio, 0)."""
        start = datetime(2024, 1, 1, 22, 0, 0, tzinfo=pytz.UTC)
        end = datetime(2024, 1, 2, 6, 0, 0, tzinfo=pytz.UTC)

        # Various wake patterns
        test_cases = [
            ([WAKE] * 100 + [LIGHT] * 400, "Low wake"),
            ([WAKE] * 250 + [LIGHT] * 250, "Half wake"),
            ([WAKE] * 400 + [LIGHT] * 100, "High wake"),
        ]

        for stages, description in test_cases:
            result = calculator.calculate(stages, start, end)
            expected_sleep_ratio = max(1 - result.wake_ratio, 0)
            expected_sleep_ratio = round(expected_sleep_ratio, 2)  # Round to 2 decimals

            assert result.sleep_ratio == expected_sleep_ratio, \
                f"{description}: sleep_ratio {result.sleep_ratio} != 1 - wake_ratio {expected_sleep_ratio}"
            assert result.sleep_ratio >= 0, f"{description}: sleep_ratio is negative"

    def test_floating_point_precision(self, calculator):
        """Test that normalization handles floating-point precision errors."""
        start = datetime(2024, 1, 1, 22, 0, 0, tzinfo=pytz.UTC)
        end = datetime(2024, 1, 2, 6, 0, 0, tzinfo=pytz.UTC)

        # Patterns designed to create floating-point rounding issues
        # Example: 333 light + 333 deep + 334 rem = 1000 epochs
        # Raw ratios: 0.333, 0.333, 0.334
        # After rounding to 2 decimals: 0.33 + 0.33 + 0.33 = 0.99 (needs +0.01 adjustment)
        stages = [LIGHT] * 333 + [DEEP] * 333 + [REM] * 334
        result = calculator.calculate(stages, start, end)

        # Verify exact sum despite potential rounding errors
        ratio_sum = result.wake_ratio + result.light_ratio + result.deep_ratio + result.rem_ratio
        assert ratio_sum == 1.0, f"Failed to normalize fractional ratios: sum = {ratio_sum}"

    def test_edge_case_all_wake(self, calculator):
        """Test ratio normalization when session is all wake."""
        start = datetime(2024, 1, 1, 22, 0, 0, tzinfo=pytz.UTC)
        end = datetime(2024, 1, 2, 6, 0, 0, tzinfo=pytz.UTC)

        stages = [WAKE] * 960
        result = calculator.calculate(stages, start, end)

        # All ratios should be 0 (no sleep period)
        assert result.wake_ratio == 0.0
        assert result.light_ratio == 0.0
        assert result.deep_ratio == 0.0
        assert result.rem_ratio == 0.0
        assert result.sleep_ratio == 0.0


class TestBasicCalculation:
    """Basic calculation tests."""

    def test_simple_case(self, calculator):
        """Test a simple sleep session."""
        start = datetime(2024, 1, 1, 22, 0, 0, tzinfo=pytz.UTC)
        end = datetime(2024, 1, 2, 6, 0, 0, tzinfo=pytz.UTC)

        # 8 hours = 960 epochs
        # Pattern: 10min wake, 6h sleep (mostly light), 10min wake, 1.5h sleep, 10min wake
        stages = (
            [WAKE] * 20 +  # 10 min wake
            [LIGHT] * 720 +  # 6 hours light sleep
            [WAKE] * 20 +  # 10 min wake
            [LIGHT] * 180 +  # 1.5 hours light sleep
            [WAKE] * 20  # 10 min wake
        )

        result = calculator.calculate(stages, start, end)

        # Basic assertions - values are timedelta objects in SleepStat
        assert result.sleep_index is None
        assert result.time_in_bed.total_seconds() == 28800  # 8 hours
        assert result.time_in_sleep.total_seconds() == 27000  # 7.5 hours
        assert result.sleep_efficiency > 0.9

    def test_validation_empty_stages(self, calculator):
        """Test that empty stages raises ValueError."""
        start = datetime(2024, 1, 1, 22, 0, 0)
        end = datetime(2024, 1, 2, 6, 0, 0)

        with pytest.raises(ValueError, match="cannot be empty"):
            calculator.calculate([], start, end)

    def test_validation_end_before_start(self, calculator):
        """Test that end before start raises ValueError."""
        start = datetime(2024, 1, 2, 6, 0, 0)
        end = datetime(2024, 1, 1, 22, 0, 0)

        with pytest.raises(ValueError, match="must be after"):
            calculator.calculate([WAKE] * 100, start, end)

    def test_validation_invalid_stage(self, calculator):
        """Test that invalid stage value raises ValueError."""
        start = datetime(2024, 1, 1, 22, 0, 0)
        end = datetime(2024, 1, 2, 6, 0, 0)

        with pytest.raises(ValueError, match="Invalid sleep stage"):
            calculator.calculate([0, 1, 2, 4], start, end)  # 4 is invalid


class TestRealData:
    """Tests using real sleep data from data-backend."""

    def test_case0(self, calculator, sleep_data):
        """Test case 0: No REM sleep."""
        if sleep_data is None:
            pytest.skip("Test data not available")

        utc = pytz.timezone("UTC")
        start_time = datetime(2023, 10, 20, 0, 0, 0, tzinfo=utc)
        end_time = datetime(2023, 10, 20, 7, 11, 45, tzinfo=utc)

        expected = {
            "sleep_score": 77.727,
            "sleep_score_version": "0.1",
            "sleep_time": datetime(2023, 10, 20, 0, 10, 0, tzinfo=utc),
            "wake_time": datetime(2023, 10, 20, 7, 3, 45, tzinfo=utc),
            "start_time": start_time,
            "end_time": end_time,
            "sleep_latency": 600,
            "wakeup_latency": 480,
            "rem_latency": None,
            "light_latency": 0,
            "deep_latency": 2850,
            "time_in_bed": 25905,
            "time_in_sleep_period": 24810,
            "time_in_sleep": 22110,
            "time_in_wake": 2700,
            "time_in_light": 21480,
            "time_in_deep": 630,
            "time_in_rem": 0,
            "sleep_efficiency": 0.854,
            "sleep_ratio": 0.891,
            "wake_ratio": 0.109,
            "light_ratio": 0.866,
            "deep_ratio": 0.025,
            "rem_ratio": 0.0,
            "sleep_cycle": None,
            "sleep_cycle_count": 0,
            "sleep_cycle_time": [],
            "waso_count": 16,
            "longest_waso": 600,
        }

        result = calculator.calculate(sleep_data["case0"]["sleep_stages"], start_time, end_time)
        compare_stats(result, expected)

    def test_case1(self, calculator, sleep_data):
        """Test case 1: Some REM sleep, single cycle."""
        if sleep_data is None:
            pytest.skip("Test data not available")

        utc = pytz.timezone("UTC")
        start_time = datetime(2023, 10, 20, 0, 0, 0, tzinfo=utc)
        end_time = datetime(2023, 10, 20, 7, 11, 45, tzinfo=utc)

        expected = {
            "sleep_score": 77.727,
            "sleep_score_version": "0.1",
            "sleep_time": datetime(2023, 10, 20, 0, 10, 0, tzinfo=utc),
            "wake_time": datetime(2023, 10, 20, 7, 3, 45, tzinfo=utc),
            "start_time": start_time,
            "end_time": end_time,
            "sleep_latency": 600,
            "wakeup_latency": 480,
            "rem_latency": 2400,
            "light_latency": 0,
            "deep_latency": 3000,
            "time_in_bed": 25905,
            "time_in_sleep_period": 24810,
            "time_in_sleep": 22110,
            "time_in_wake": 2700,
            "time_in_light": 21030,
            "time_in_deep": 480,
            "time_in_rem": 600,
            "sleep_efficiency": 0.854,
            "sleep_ratio": 0.891,
            "wake_ratio": 0.109,
            "light_ratio": 0.848,
            "deep_ratio": 0.019,
            "rem_ratio": 0.024,
            "sleep_cycle": 2970,  # Note: integer instead of float
            "sleep_cycle_count": 1,
            "sleep_cycle_time": [
                datetime(2023, 10, 20, 0, 10, 0, tzinfo=utc),
                datetime(2023, 10, 20, 0, 59, 30, tzinfo=utc),
            ],
            "waso_count": 16,
            "longest_waso": 600,
        }

        result = calculator.calculate(sleep_data["case1"]["sleep_stages"], start_time, end_time)
        compare_stats(result, expected)

    def test_case2(self, calculator, sleep_data):
        """Test case 2: Multiple sleep cycles."""
        if sleep_data is None:
            pytest.skip("Test data not available")

        utc = pytz.timezone("UTC")
        start_time = datetime(2023, 10, 20, 0, 0, 0, tzinfo=utc)
        end_time = datetime(2023, 10, 20, 7, 11, 45, tzinfo=utc)

        expected = {
            "sleep_score": 75.605,
            "sleep_score_version": "0.1",
            "sleep_time": datetime(2023, 10, 20, 0, 20, 0, tzinfo=utc),
            "wake_time": datetime(2023, 10, 20, 7, 0, 15, tzinfo=utc),
            "start_time": start_time,
            "end_time": end_time,
            "sleep_latency": 1200,
            "wakeup_latency": 690,
            "rem_latency": 1800,
            "light_latency": 0,
            "deep_latency": 2400,
            "time_in_bed": 25905,
            "time_in_sleep_period": 24000,
            "time_in_sleep": 20670,
            "time_in_wake": 3330,
            "time_in_light": 18540,
            "time_in_deep": 330,
            "time_in_rem": 1800,
            "sleep_efficiency": 0.8,
            "sleep_ratio": 0.861,
            "wake_ratio": 0.139,
            "light_ratio": 0.772,
            "deep_ratio": 0.014,
            "rem_ratio": 0.075,
            "sleep_cycle": 3790,  # Note: integer instead of float
            "sleep_cycle_count": 3,
            "sleep_cycle_time": [
                datetime(2023, 10, 20, 0, 20, 0, tzinfo=utc),
                datetime(2023, 10, 20, 0, 59, 30, tzinfo=utc),
                datetime(2023, 10, 20, 2, 39, 30, tzinfo=utc),
                datetime(2023, 10, 20, 3, 29, 30, tzinfo=utc),
            ],
            "waso_count": 14,
            "longest_waso": 630,
        }

        result = calculator.calculate(sleep_data["case2"]["sleep_stages"], start_time, end_time)
        compare_stats(result, expected)


class TestEdgeCases:
    """Test edge cases."""

    def test_all_wake(self, calculator):
        """Test session with all wake stages."""
        start = datetime(2024, 1, 1, 22, 0, 0, tzinfo=pytz.UTC)
        end = datetime(2024, 1, 2, 6, 0, 0, tzinfo=pytz.UTC)
        stages = [WAKE] * 960

        result = calculator.calculate(stages, start, end)

        # When no sleep, most values should be 0 or minimal
        assert result.time_in_sleep.total_seconds() == 0
        assert result.sleep_efficiency == 0.0

        # Verify no negative latencies
        assert result.sleep_latency.total_seconds() >= 0
        assert result.wakeup_latency.total_seconds() >= 0
        assert result.sleep_latency == result.time_in_bed
        assert result.wakeup_latency.total_seconds() == 0

        # Verify time ordering
        assert result.sleep_time >= result.start_time
        assert result.wake_time >= result.sleep_time
        assert result.end_time >= result.wake_time

        # Stage latencies should be None when no sleep occurred
        assert result.rem_latency is None
        assert result.light_latency is None
        assert result.deep_latency is None

        # All stage durations should be 0
        assert result.time_in_light == timedelta(0)
        assert result.time_in_deep == timedelta(0)
        assert result.time_in_rem == timedelta(0)

        # WASO and cycle metrics
        assert result.waso_count == 0
        assert result.sleep_cycle_count == 0
        assert result.sleep_cycle is None

    def test_no_rem(self, calculator):
        """Test session with no REM sleep."""
        start = datetime(2024, 1, 1, 22, 0, 0, tzinfo=pytz.UTC)
        end = datetime(2024, 1, 2, 6, 0, 0, tzinfo=pytz.UTC)
        stages = [WAKE] * 20 + [LIGHT] * 920 + [WAKE] * 20

        result = calculator.calculate(stages, start, end)

        assert result.rem_latency is None
        assert result.time_in_rem.total_seconds() == 0
        assert result.rem_ratio == 0.0
        assert result.sleep_cycle_count == 0

    def test_short_session(self, calculator):
        """Test a very short sleep session."""
        start = datetime(2024, 1, 1, 22, 0, 0, tzinfo=pytz.UTC)
        end = datetime(2024, 1, 1, 23, 0, 0, tzinfo=pytz.UTC)
        stages = [WAKE] * 10 + [LIGHT] * 100 + [WAKE] * 10

        result = calculator.calculate(stages, start, end)

        assert result.time_in_bed.total_seconds() == 3600  # 1 hour
        assert result.time_in_sleep.total_seconds() == 3000  # 50 minutes
        assert result.sleep_index is None  # Calculator doesn't compute sleep index

    def test_time_invariants(self, calculator):
        """Test that time values always maintain proper ordering."""
        # Test with various patterns
        test_cases = [
            ([WAKE] * 100, "all wake"),
            ([LIGHT] * 100, "all sleep"),
            ([WAKE] * 50 + [LIGHT] * 50, "wake then sleep"),
            ([LIGHT] * 50 + [WAKE] * 50, "sleep then wake"),
        ]

        for stages, description in test_cases:
            start = datetime(2024, 1, 1, 22, 0, 0, tzinfo=pytz.UTC)
            end = start + timedelta(seconds=len(stages) * 30)
            result = calculator.calculate(stages, start, end)

            # Time ordering invariants
            assert result.start_time <= result.sleep_time, f"Failed for {description}: start_time > sleep_time"
            assert result.sleep_time <= result.wake_time, f"Failed for {description}: sleep_time > wake_time"
            assert result.wake_time <= result.end_time, f"Failed for {description}: wake_time > end_time"

            # Non-negative latencies
            assert result.sleep_latency.total_seconds() >= 0, f"Failed for {description}: negative sleep_latency"
            assert result.wakeup_latency.total_seconds() >= 0, f"Failed for {description}: negative wakeup_latency"

    def test_breathing_fields_none_when_unavailable(self, calculator):
        """Verify breathing fields are None when breathing data unavailable."""
        start = datetime(2024, 1, 1, 22, 0, 0, tzinfo=pytz.UTC)
        end = datetime(2024, 1, 2, 6, 0, 0, tzinfo=pytz.UTC)

        # Simple sleep session
        stages = [WAKE] * 20 + [LIGHT] * 400 + [DEEP] * 200 + [REM] * 100
        result = calculator.calculate(stages, start, end)

        # Verify all breathing durations are None
        assert result.time_in_stable_breath is None
        assert result.time_in_unstable_breath is None
        assert result.time_in_snoring is None
        assert result.time_in_no_snoring is None

        # Verify all breathing ratios are None
        assert result.stable_breath_ratio is None
        assert result.unstable_breath_ratio is None
        assert result.snoring_ratio is None
        assert result.no_snoring_ratio is None

        # Verify breathing metrics are None
        assert result.breathing_pattern is None
        assert result.breathing_index is None
        assert result.unstable_breath_count is None
        assert result.snoring_count is None

        # Verify sleep_index also None
        assert result.sleep_index is None


def test_simple_hypnogram_without_datetime():
    """Test calculating from just a hypnogram without providing datetime."""
    calculator = SleepStageCalculator()

    # Just a simple hypnogram - no datetime needed!
    hypnogram = [WAKE, WAKE, LIGHT, LIGHT, DEEP, DEEP, REM, REM, LIGHT, WAKE]

    # Calculate with just the hypnogram
    result = calculator.calculate(hypnogram)

    # All metrics should be calculated correctly
    # hypnogram has: 3 WAKE, 3 LIGHT, 2 DEEP, 2 REM = 7 sleep epochs
    assert result.time_in_bed.total_seconds() == 300  # 10 epochs * 30s
    assert result.time_in_sleep.total_seconds() == 210  # 7 sleep epochs * 30s
    assert result.sleep_efficiency == 0.7  # 210 / 300
    assert result.time_in_light.total_seconds() == 90  # 3 epochs
    assert result.time_in_deep.total_seconds() == 60  # 2 epochs
    assert result.time_in_rem.total_seconds() == 60  # 2 epochs
    assert result.waso_count == 0  # Wake at end is wakeup latency, not WASO

    # Datetime fields should exist but use default epoch time
    assert result.start_time.year == 1970


def test_timedelta_conversion_helper():
    """Test that the calculator returns pysleep.SleepStat with timedelta objects.

    This test verifies that the integrated calculator properly returns
    a pysleep.SleepStat object with timedelta fields.
    """
    calculator = SleepStageCalculator()
    start = datetime(2024, 1, 1, 22, 0, 0, tzinfo=pytz.UTC)
    end = datetime(2024, 1, 2, 6, 0, 0, tzinfo=pytz.UTC)
    stages = [LIGHT] * 960  # Simple test case

    result = calculator.calculate(stages, start, end)

    # Verify that result contains timedelta objects
    assert isinstance(result.time_in_bed, timedelta)
    assert isinstance(result.time_in_sleep, timedelta)
    assert isinstance(result.sleep_latency, timedelta)

    # Verify the values are correct
    assert result.time_in_bed.total_seconds() == 28800  # 8 hours
    assert result.time_in_sleep.total_seconds() == 28800  # All light sleep
    assert result.sleep_latency.total_seconds() == 0  # No wake at start


if __name__ == "__main__":
    pytest.main([__file__, "-v"])