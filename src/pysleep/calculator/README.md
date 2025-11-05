# Sleep Stage Calculator

The Sleep Stage Calculator module provides comprehensive sleep metrics calculation from 30-second epoch sleep stage data.

## Overview

This module processes sleep stage data and computes various sleep metrics including:
- Sleep latencies (time to fall asleep, wake up, and reach different stages)
- Sleep durations (time in each stage)
- Sleep ratios and efficiency
- WASO (Wake After Sleep Onset) metrics
- Sleep cycle detection

## Usage

```python
from pysleep import SleepStageCalculator, SleepStat
from datetime import datetime

# Create calculator instance
calculator = SleepStageCalculator()

# Define session times
start_time = datetime(2024, 1, 1, 22, 0, 0)
end_time = datetime(2024, 1, 2, 6, 0, 0)

# Provide sleep stage data (30-second epochs)
# 0=WAKE, 1=LIGHT, 2=DEEP, 3=REM
sleep_stages = [0, 0, 1, 1, 2, 2, 3, 3, 1, 1, ...]

# Calculate statistics
result = calculator.calculate(sleep_stages, start_time, end_time)

# Access results (returns pysleep.SleepStat object)
print(f"Sleep efficiency: {result.sleep_efficiency:.1%}")
print(f"Time in sleep: {result.time_in_sleep}")
print(f"WASO count: {result.waso_count}")
print(f"Sleep cycles: {result.sleep_cycle_count}")
```

## Integration with pysleep

The calculator is fully integrated with pysleep's `SleepStat` model:
- Returns `SleepStat` objects instead of internal types
- All duration fields use `timedelta` for consistency
- Sets `sleep_index` to None (sleep scoring not performed by this calculator)
- Sets breathing-related fields to sensible defaults

## Internal Architecture

The calculator maintains high performance by:
- Performing all internal calculations in seconds (integers)
- Converting to `timedelta` only at the return point
- Using efficient numpy-style indexing for stage analysis
- Minimizing object creation during calculations

## Sleep Stage Values

- `0`: Wake
- `1`: Light sleep (N1/N2)
- `2`: Deep sleep (N3)
- `3`: REM sleep

## Metrics Calculated

### Latencies
- **Sleep latency**: Time from start to first sleep
- **Wakeup latency**: Time from last sleep to end
- **Light/Deep/REM latency**: Time from first sleep to first occurrence of each stage

### Durations
- **Time in bed**: Total session duration
- **Time in sleep period**: From first sleep to last sleep
- **Time in sleep**: Total time in all sleep stages
- **Time in wake/light/deep/rem**: Time in each stage

### Ratios
- **Sleep efficiency**: time_in_sleep / time_in_bed
- **Stage ratios**: Proportion of each stage in sleep period

### Sleep Quality
- **WASO metrics**: Wake episodes during sleep, longest wake duration
- **Sleep cycles**: REM-based cycle detection and timing