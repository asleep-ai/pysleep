"""
Example demonstrating how to work with the SleepStat object returned by SleepStageCalculator.

This example shows:
1. How to access different categories of metrics
2. How to work with timedelta fields
3. How to create comparisons between multiple sleep sessions
"""

from datetime import datetime, timedelta
from pysleep import SleepStageCalculator


def analyze_single_night(calculator, sleep_stages, start_time, end_time):
    """Analyze a single night of sleep and return the stats."""
    # New API: calculate(sleep_stages, start_time, end_time)
    stats = calculator.calculate(sleep_stages, start_time, end_time)
    return stats


def format_duration(td):
    """Format a timedelta as hours and minutes."""
    if td is None:
        return "N/A"
    total_seconds = int(td.total_seconds())
    hours = total_seconds // 3600
    minutes = (total_seconds % 3600) // 60
    return f"{hours}h {minutes}m"


def print_detailed_stats(stats, night_label):
    """Print detailed statistics for a sleep session."""
    print(f"\n{night_label} Sleep Statistics")
    print("=" * 60)

    # Access duration fields (all are timedelta objects)
    print("\nDuration Metrics:")
    print(f"  Time in bed: {format_duration(stats.time_in_bed)}")
    print(f"  Time in sleep: {format_duration(stats.time_in_sleep)}")
    print(f"  Time in sleep period: {format_duration(stats.time_in_sleep_period)}")

    # Access latency fields (also timedelta objects)
    print("\nLatency Metrics:")
    print(f"  Sleep latency: {format_duration(stats.sleep_latency)}")
    print(f"  Light latency: {format_duration(stats.light_latency)}")
    print(f"  Deep latency: {format_duration(stats.deep_latency)}")
    print(f"  REM latency: {format_duration(stats.rem_latency)}")
    print(f"  Wakeup latency: {format_duration(stats.wakeup_latency)}")

    # Access ratio fields (float values between 0 and 1)
    print("\nSleep Stage Distribution:")
    print(f"  Wake: {stats.wake_ratio:.1%} ({format_duration(stats.time_in_wake)})")
    print(f"  Light: {stats.light_ratio:.1%} ({format_duration(stats.time_in_light)})")
    print(f"  Deep: {stats.deep_ratio:.1%} ({format_duration(stats.time_in_deep)})")
    print(f"  REM: {stats.rem_ratio:.1%} ({format_duration(stats.time_in_rem)})")

    # Access quality metrics
    print("\nQuality Metrics:")
    print(f"  Sleep efficiency: {stats.sleep_efficiency:.1%}")
    print(f"  Sleep index: {stats.sleep_index}")  # Calculator doesn't compute this (returns None)
    print(f"  Sleep cycle count: {stats.sleep_cycle_count}")
    if stats.sleep_cycle:
        print(f"  Average sleep cycle: {format_duration(stats.sleep_cycle)}")

    # WASO (Wake After Sleep Onset) metrics
    print("\nWASO Analysis:")
    print(f"  WASO count: {stats.waso_count}")
    print(f"  Longest WASO period: {format_duration(stats.longest_waso)}")

    # Working with datetime fields
    if stats.start_time and stats.end_time:
        duration = stats.end_time - stats.start_time
        print(f"\nSession Info:")
        print(f"  Start: {stats.start_time.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"  End: {stats.end_time.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"  Total duration: {format_duration(duration)}")


def compare_two_nights(stats1, stats2):
    """Compare two nights of sleep."""
    print("\nSleep Comparison")
    print("=" * 60)

    # Compare sleep efficiency
    print("\nEfficiency Comparison:")
    eff_diff = (stats2.sleep_efficiency - stats1.sleep_efficiency) * 100
    direction = "improved" if eff_diff > 0 else "decreased"
    print(f"  Night 1: {stats1.sleep_efficiency:.1%}")
    print(f"  Night 2: {stats2.sleep_efficiency:.1%}")
    print(f"  Sleep efficiency {direction} by {abs(eff_diff):.1f}%")

    print("\nSleep Duration Comparison:")
    sleep_diff = stats2.time_in_sleep - stats1.time_in_sleep
    direction = "more" if sleep_diff.total_seconds() > 0 else "less"
    print(f"  Night 1: {format_duration(stats1.time_in_sleep)}")
    print(f"  Night 2: {format_duration(stats2.time_in_sleep)}")
    print(f"  {format_duration(abs(sleep_diff))} {direction} sleep")

    print("\nDeep Sleep Comparison:")
    deep_diff = stats2.deep_ratio - stats1.deep_ratio
    direction = "more" if deep_diff > 0 else "less"
    print(f"  Night 1: {stats1.deep_ratio:.1%}")
    print(f"  Night 2: {stats2.deep_ratio:.1%}")
    print(f"  {abs(deep_diff)*100:.1f}% {direction} deep sleep")


def main():
    # Initialize calculator
    calculator = SleepStageCalculator()

    # Night 1: Good quality sleep
    night1_start = datetime(2024, 1, 1, 22, 30, 0)
    night1_end = datetime(2024, 1, 2, 6, 30, 0)
    night1_stages = (
        [0] * 6 +          # 3 minutes to fall asleep
        [1] * 40 +         # 20 minutes light
        [2] * 60 +         # 30 minutes deep
        [1] * 60 +         # 30 minutes light
        [3] * 40 +         # 20 minutes REM
        [1] * 80 +         # 40 minutes light
        [2] * 40 +         # 20 minutes deep
        [1] * 100 +        # 50 minutes light
        [3] * 80 +         # 40 minutes REM
        [1] * 120 +        # 60 minutes light
        [3] * 100 +        # 50 minutes REM
        [1] * 60 +         # 30 minutes light
        [0] * 4            # 2 minutes awake before alarm
    )

    # Night 2: Restless sleep with more wake periods
    night2_start = datetime(2024, 1, 2, 23, 0, 0)
    night2_end = datetime(2024, 1, 3, 6, 30, 0)
    night2_stages = (
        [0] * 20 +         # 10 minutes to fall asleep
        [1] * 30 +         # 15 minutes light
        [0] * 10 +         # 5 minutes awake (restless)
        [1] * 20 +         # 10 minutes light
        [2] * 30 +         # 15 minutes deep
        [1] * 40 +         # 20 minutes light
        [0] * 8 +          # 4 minutes awake
        [1] * 60 +         # 30 minutes light
        [3] * 30 +         # 15 minutes REM
        [0] * 6 +          # 3 minutes awake
        [1] * 80 +         # 40 minutes light
        [2] * 20 +         # 10 minutes deep
        [1] * 100 +        # 50 minutes light
        [3] * 40 +         # 20 minutes REM
        [0] * 12 +         # 6 minutes awake
        [1] * 80 +         # 40 minutes light
        [3] * 60 +         # 30 minutes REM
        [1] * 40 +         # 20 minutes light
        [0] * 10           # 5 minutes awake before alarm
    )

    # Analyze both nights (note: parameter order changed)
    stats1 = analyze_single_night(calculator, night1_stages, night1_start, night1_end)
    stats2 = analyze_single_night(calculator, night2_stages, night2_start, night2_end)

    # Print detailed statistics for each night
    print_detailed_stats(stats1, "Night 1 (Good Sleep)")
    print_detailed_stats(stats2, "Night 2 (Restless Sleep)")

    # Compare the two nights
    compare_two_nights(stats1, stats2)

    # Demonstrate checking for specific conditions
    print("\nSleep Quality Assessment:")
    for i, stats in enumerate([stats1, stats2], 1):
        print(f"\nNight {i}:")

        # Check sleep efficiency
        if stats.sleep_efficiency >= 0.85:
            print("  ✓ Good sleep efficiency (≥85%)")
        else:
            print("  ✗ Poor sleep efficiency (<85%)")

        # Check deep sleep ratio
        if stats.deep_ratio >= 0.15:
            print("  ✓ Adequate deep sleep (≥15%)")
        else:
            print("  ✗ Insufficient deep sleep (<15%)")

        # Check REM sleep ratio
        if stats.rem_ratio >= 0.20:
            print("  ✓ Adequate REM sleep (≥20%)")
        else:
            print("  ✗ Insufficient REM sleep (<20%)")

        # Check WASO
        if stats.waso_count <= 2:
            print("  ✓ Minimal sleep interruptions (≤2 WASO)")
        else:
            print("  ✗ Frequent sleep interruptions (>2 WASO)")


if __name__ == "__main__":
    main()