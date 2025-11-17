"""
Constants for sleep stage calculations.

This module defines all constants used in sleep stage analysis and statistics calculations.
All timing values are in seconds unless otherwise specified.

Sleep stages are represented as integer values for 30-second epochs:
- WAKE (0): Awake state
- LIGHT (1): Light sleep (same as SLEEP for 2-stage classification)
- DEEP (2): Deep sleep
- REM (3): Rapid Eye Movement sleep
"""

# Sleep stage values (30-second epochs)
WAKE: int = 0
"""Wake stage value."""

LIGHT: int = 1
"""Light sleep stage value (same as SLEEP for 2-stage classification)."""

DEEP: int = 2
"""Deep sleep stage value."""

REM: int = 3
"""REM (Rapid Eye Movement) sleep stage value."""

# Timing constants
SECONDS_PER_EPOCH: int = 30
"""Duration of each sleep stage epoch in seconds."""

# REM cluster detection thresholds
THRESHOLD_REM_CLUSTER_DISTANCE: int = 20
"""
Maximum distance in epochs between REM periods to be considered part of the same cluster.
Value of 20 epochs = 10 minutes. If REM epochs are separated by more than this distance,
they are considered separate clusters (separate sleep cycles).
"""

THRESHOLD_REM_COUNT: int = 20
"""
Minimum number of REM epochs required to form a valid REM cluster.
Value of 20 epochs = 10 minutes of REM sleep.
Clusters with fewer REM epochs are discarded.
"""
