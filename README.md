# pysleep

A Python library for sleep pattern analysis and sleep metrics calculation commonly used in medical and research fields.

## Installation

```bash
pip install pysleep
```

## Features

- Definition of sleep stages and events in the Python ecosystem
- Various sleep metrics used in medical field
- Sleep statistics calculation and analysis tools
- Comprehensive sleep stage calculator for 30+ metrics from epoch data
- Returns `None` for breathing fields (requires sensor data)
- Returns `None` for sleep_index (scoring not implemented)

## Sleep Stage Calculator

The `SleepStageCalculator` analyzes 30-second epoch sleep stage data to compute comprehensive sleep metrics including latencies, durations, ratios, and sleep quality indices.

### Quick Example

```python
from pysleep import SleepStageCalculator
from datetime import datetime

# Initialize calculator
calculator = SleepStageCalculator()

# Define session times
start_time = datetime(2024, 1, 1, 22, 0, 0)
end_time = datetime(2024, 1, 2, 6, 0, 0)

# Sleep stages (30-second epochs): 0=WAKE, 1=LIGHT, 2=DEEP, 3=REM
sleep_stages = [0, 0, 1, 1, 2, 2, 3, 3, 1, 1, 0, 1, 2, 3]  # ... more epochs

# Calculate metrics
stats = calculator.calculate(sleep_stages, start_time, end_time)

# Access results (returns SleepStat object)
print(f"Sleep efficiency: {stats.sleep_efficiency:.1%}")
print(f"Time in sleep: {stats.time_in_sleep}")
print(f"Sleep latency: {stats.sleep_latency}")
print(f"Sleep cycles: {stats.sleep_cycle}")
```

For detailed documentation on all available metrics and advanced usage, see the [Sleep Stage Calculator documentation](src/pysleep/calculator/README.md).

## License

This project is licensed under the MIT License - see the LICENSE file for details.
