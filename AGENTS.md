# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

pysleep is a Python library for sleep pattern analysis. It processes 30-second epoch sleep stage data (hypnograms) into clinically relevant metrics including latencies, durations, ratios, and sleep quality indices.

**Sleep stage values:** 0=Wake, 1=Light, 2=Deep, 3=REM

## Common Commands

```bash
# Run tests
python -m pytest tests/ -v

# Run a single test file
python -m pytest tests/calculator/test_calculator.py -v

# Lint and format
ruff check .
ruff format .

# Build package
uv build

# Install dev dependencies
uv pip install pytest parameterized
```

## Architecture

### Data Flow

```
sleep_stages (List[int]) → SleepStageCalculator.calculate() → SleepStat
```

### Key Modules

- **calculator/calculator.py**: Main `SleepStageCalculator` class. Orchestrates the calculation pipeline: validate inputs → calculate key moments → latencies → time points → cluster metrics (WASO, sleep cycles) → durations → ratios.

- **stat.py**: `SleepStat` (40+ field output dataclass) and `SleepStatDelta` (for comparing sessions). SleepStat contains latencies, durations, ratios, WASO metrics, and sleep cycle data.

- **calculator/types.py**: Intermediate dataclasses (`SleepStageMoment`, `SleepStageLatency`, `SleepStageTime`, `SleepStageDuration`, `SleepStageRatio`, `SleepStageClusterMetric`) used during calculation.

- **calculator/constants.py**: `SECONDS_PER_EPOCH` (30), stage values, REM clustering thresholds.

- **label.py**: Public constants for sleep stages (WAKE, LIGHT, DEEP, REM) and events (APNEA, HYPOPNEA, SNORE).

- **hypnogram_report.py**: Utility for generating reports from hypnogram data.

### Key Algorithms

- **Sleep Cycle Detection**: REM-based clustering using `THRESHOLD_REM_CLUSTER_DISTANCE` (20 epochs max gap) and `THRESHOLD_REM_COUNT` (20 epochs minimum).

- **Ratio Precision**: `_adjust_ratios_to_second()` iteratively rounds to ensure stage ratios sum to exactly 1.0.

### Design Notes

- All internal calculations use integers (seconds), converting to timedelta only at return
- Breathing-related fields and sleep_index are always None (not calculated from hypnogram data)
- Datetime parameters are optional; defaults to epoch (1970-01-01)

## Testing

Tests use parameterized fixtures and load external test data via pickle. The `compare_stats()` helper uses tolerance (0.003) for floating-point comparisons.

Test data location controlled by `PYSLEEP_TEST_DATA` environment variable.
