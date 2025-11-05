"""
Basic example of using SleepStageCalculator to analyze sleep data.

This example demonstrates:
1. How to prepare sleep stage data
2. How to use the calculator
3. How to access various metrics from the returned SleepStat object
"""

from datetime import datetime
from pysleep import SleepStageCalculator


def main():
    # Initialize the calculator
    calculator = SleepStageCalculator()

    # Define session start and end times
    start_time = datetime(2024, 1, 1, 22, 0, 0)  # 10:00 PM
    end_time = datetime(2024, 1, 2, 6, 30, 0)    # 6:30 AM next day

    # Simulate sleep stage data (30-second epochs)
    # In real usage, this would come from a sleep tracking device
    # Stage values: 0=WAKE, 1=LIGHT, 2=DEEP, 3=REM

    # Example pattern: initial wake, then cycles through sleep stages
    sleep_stages = (
        [0] * 10 +         # 5 minutes awake at start
        [1] * 20 +         # 10 minutes light sleep
        [2] * 30 +         # 15 minutes deep sleep
        [1] * 40 +         # 20 minutes light sleep
        [3] * 20 +         # 10 minutes REM
        [1] * 30 +         # 15 minutes light sleep
        [0] * 4 +          # 2 minutes wake (WASO)
        [1] * 40 +         # 20 minutes light sleep
        [2] * 40 +         # 20 minutes deep sleep
        [1] * 50 +         # 25 minutes light sleep
        [3] * 40 +         # 20 minutes REM
        [1] * 60 +         # 30 minutes light sleep
        [2] * 20 +         # 10 minutes deep sleep
        [1] * 80 +         # 40 minutes light sleep
        [3] * 60 +         # 30 minutes REM
        [1] * 40 +         # 20 minutes light sleep
        [0] * 10 +         # 5 minutes wake
        [1] * 40 +         # 20 minutes light sleep
        [3] * 80 +         # 40 minutes REM
        [1] * 40 +         # 20 minutes light sleep
        [0] * 6            # 3 minutes wake at end
    )

    # Calculate sleep statistics with the new API
    # New API: calculate(sleep_stages, start_time, end_time)
    stats = calculator.calculate(sleep_stages, start_time, end_time)

    # Display key metrics
    print("Sleep Analysis Results")
    print("=" * 50)

    # Basic timing metrics
    print("\nTiming Metrics:")
    print(f"  Time in bed: {stats.time_in_bed}")
    print(f"  Time in sleep: {stats.time_in_sleep}")
    print(f"  Sleep efficiency: {stats.sleep_efficiency:.1%}")

    # Latency metrics
    print("\nLatency Metrics:")
    print(f"  Sleep latency: {stats.sleep_latency}")
    print(f"  Wakeup latency: {stats.wakeup_latency}")
    print(f"  REM latency: {stats.rem_latency}")

    # Stage durations
    print("\nTime in Each Stage:")
    print(f"  Wake: {stats.time_in_wake}")
    print(f"  Light sleep: {stats.time_in_light}")
    print(f"  Deep sleep: {stats.time_in_deep}")
    print(f"  REM sleep: {stats.time_in_rem}")

    # Stage ratios
    print("\nStage Ratios (% of sleep period):")
    print(f"  Wake ratio: {stats.wake_ratio:.1%}")
    print(f"  Light ratio: {stats.light_ratio:.1%}")
    print(f"  Deep ratio: {stats.deep_ratio:.1%}")
    print(f"  REM ratio: {stats.rem_ratio:.1%}")

    # Sleep quality metrics
    print("\nSleep Quality:")
    print(f"  Sleep index: {stats.sleep_index}")  # Note: Calculator doesn't compute this (returns None)
    print(f"  Sleep cycles: {stats.sleep_cycle_count}")
    print(f"  WASO (Wake After Sleep Onset): {stats.waso_count} episodes")

    # Additional metrics
    print("\nAdditional Information:")
    print(f"  Longest WASO period: {stats.longest_waso}")
    print(f"  Total epochs analyzed: {len(sleep_stages)}")
    print(f"  Session duration: {(end_time - start_time).total_seconds() / 3600:.1f} hours")


if __name__ == "__main__":
    main()