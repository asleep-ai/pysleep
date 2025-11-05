# pysleep Examples

This directory contains example scripts demonstrating how to use the pysleep library, particularly the `SleepStageCalculator`.

## Examples

### basic_calculator_usage.py
Demonstrates the fundamental usage of `SleepStageCalculator`:
- How to prepare 30-second epoch sleep stage data
- How to initialize and use the calculator
- How to access various metrics from the returned `SleepStat` object
- Understanding all available sleep metrics

Run with:
```bash
python3 basic_calculator_usage.py
```

### working_with_sleepstat.py
Advanced example showing:
- Detailed access to different categories of metrics
- Working with `timedelta` fields
- Comparing multiple sleep sessions
- Sleep quality assessment based on thresholds
- Using `SleepStatDelta` for comparisons

Run with:
```bash
python3 working_with_sleepstat.py
```

## Sleep Stage Values

In all examples, sleep stages are represented as integers:
- `0`: Wake
- `1`: Light sleep (N1/N2)
- `2`: Deep sleep (N3)
- `3`: REM sleep

## Data Format

The calculator expects:
- **start_time**: Session start as a `datetime` object
- **end_time**: Session end as a `datetime` object
- **sleep_stages**: List of integers representing 30-second epochs

## Key Metrics

The `SleepStat` object returned by the calculator includes:
- **Efficiency metrics**: sleep_efficiency, sleep_index
- **Duration metrics**: time_in_bed, time_in_sleep, time_in_[stage]
- **Latency metrics**: sleep_latency, rem_latency, wakeup_latency
- **Ratio metrics**: wake_ratio, light_ratio, deep_ratio, rem_ratio
- **WASO metrics**: waso_count, longest_waso
- **Sleep cycles**: Based on REM periods

For complete documentation, see the [Sleep Stage Calculator README](../src/pysleep/calculator/README.md).