"""
Data types for sleep stage calculations.

This module defines all data structures used in sleep stage analysis,
from intermediate calculations to final output statistics.
"""

from dataclasses import dataclass
from datetime import datetime
from typing import List, Optional


@dataclass
class SleepStageMoment:
    """
    Key moment indices in the sleep stage sequence.

    This class stores indices that mark important transitions in the sleep data,
    along with counts of each sleep stage (excluding leading and trailing wake).

    Attributes:
        first_sleep_idx: Index of first non-wake epoch
        last_sleep_idx: Index of last non-wake epoch
        first_light_idx: Index of first light sleep epoch (-1 if none)
        first_deep_idx: Index of first deep sleep epoch (-1 if none)
        first_rem_idx: Index of first REM epoch (-1 if none)
        last_stage_idx: Index of last epoch (len(stages) - 1)
        wake_count: Number of wake epochs during sleep period
        sleep_count: Total sleep epochs (light + deep + rem)
        light_count: Number of light sleep epochs
        deep_count: Number of deep sleep epochs
        rem_count: Number of REM sleep epochs
    """

    first_sleep_idx: int
    last_sleep_idx: int
    first_light_idx: int
    first_deep_idx: int
    first_rem_idx: int
    last_stage_idx: int
    wake_count: int
    sleep_count: int
    light_count: int
    deep_count: int
    rem_count: int


@dataclass
class SleepStageLatency:
    """
    Latencies in seconds.

    Latencies measure the time delay to reach specific sleep stages or states.

    Attributes:
        sleep_latency: Time from session start to first sleep (any non-wake)
        wakeup_latency: Time from last sleep to session end
        light_latency: Time from first sleep to first light sleep (None if no light)
        deep_latency: Time from first sleep to first deep sleep (None if no deep)
        rem_latency: Time from first sleep to first REM (None if no REM)
    """

    sleep_latency: int
    wakeup_latency: int
    light_latency: Optional[int]
    deep_latency: Optional[int]
    rem_latency: Optional[int]


@dataclass
class SleepStageTime:
    """
    Key time points in the sleep session.

    Attributes:
        start_time: Session start time
        end_time: Session end time
        sleep_time: Time of first sleep onset
        wake_time: Final wake time (last sleep + wakeup latency)
    """

    start_time: datetime
    end_time: datetime
    sleep_time: datetime
    wake_time: datetime


@dataclass
class SleepStageDuration:
    """
    Durations in seconds for each sleep stage and overall metrics.

    Attributes:
        time_in_bed: Total session duration (end_time - start_time)
        time_in_sleep_period: Sleep period duration (first sleep to last sleep)
        time_in_sleep: Total sleep time (light + deep + rem)
        time_in_wake: Wake time during sleep period
        time_in_light: Total light sleep time
        time_in_deep: Total deep sleep time
        time_in_rem: Total REM sleep time
    """

    time_in_bed: int
    time_in_sleep_period: int
    time_in_sleep: int
    time_in_wake: int
    time_in_light: int
    time_in_deep: int
    time_in_rem: int


@dataclass
class SleepStageRatio:
    """
    Ratios (0.0 to 1.0) for sleep efficiency and stage distributions.

    All ratios are expressed as decimal values between 0.0 and 1.0.

    Attributes:
        sleep_efficiency: time_in_sleep / time_in_bed
        sleep_ratio: time_in_sleep / time_in_sleep_period
        wake_ratio: time_in_wake / time_in_sleep_period
        light_ratio: time_in_light / time_in_sleep_period
        deep_ratio: time_in_deep / time_in_sleep_period
        rem_ratio: time_in_rem / time_in_sleep_period
    """

    sleep_efficiency: float
    sleep_ratio: float
    wake_ratio: float
    light_ratio: float
    deep_ratio: float
    rem_ratio: float


@dataclass
class SleepStageClusterMetric:
    """
    Sleep cycle and WASO (Wake After Sleep Onset) cluster metrics.

    Attributes:
        waso_count: Number of wake episodes during sleep period
        longest_waso: Duration of longest wake episode in seconds
        sleep_cycle: Average sleep cycle length in seconds (None if no cycles)
        sleep_cycle_count: Number of complete sleep cycles detected
        sleep_cycle_time: List of datetime values marking cycle endpoints
    """

    waso_count: int
    longest_waso: int
    sleep_cycle: Optional[float]
    sleep_cycle_count: int
    sleep_cycle_time: List[datetime]


@dataclass
class SleepStageStats:
    """
    Complete sleep stage statistics output.

    This is the main result type returned by the sleep stage calculator.
    It contains comprehensive sleep metrics including scores, times,
    latencies, durations, ratios, and cluster information.

    Attributes:
        sleep_score: Overall sleep quality score (50-100)
        sleep_score_version: Algorithm version used for score calculation
        start_time: Session start time
        end_time: Session end time
        sleep_time: Time of first sleep onset
        wake_time: Final wake time
        sleep_latency: Time to fall asleep (seconds)
        wakeup_latency: Time from last sleep to end (seconds)
        light_latency: Time from first sleep to first light (seconds, None if no light)
        deep_latency: Time from first sleep to first deep (seconds, None if no deep)
        rem_latency: Time from first sleep to first REM (seconds, None if no REM)
        time_in_bed: Total session duration (seconds)
        time_in_sleep_period: Sleep period duration (seconds)
        time_in_sleep: Total sleep time (seconds)
        time_in_wake: Wake time during sleep period (seconds)
        time_in_light: Light sleep duration (seconds)
        time_in_deep: Deep sleep duration (seconds)
        time_in_rem: REM sleep duration (seconds)
        sleep_efficiency: Sleep efficiency ratio (0.0-1.0)
        sleep_ratio: Sleep ratio (0.0-1.0)
        wake_ratio: Wake ratio (0.0-1.0)
        light_ratio: Light sleep ratio (0.0-1.0)
        deep_ratio: Deep sleep ratio (0.0-1.0)
        rem_ratio: REM sleep ratio (0.0-1.0)
        waso_count: Number of wake episodes
        longest_waso: Longest wake episode duration (seconds)
        sleep_cycle: Average cycle length (seconds, None if no cycles)
        sleep_cycle_count: Number of complete sleep cycles
        sleep_cycle_time: List of cycle endpoint times
    """

    # Score
    sleep_score: float
    sleep_score_version: str

    # Times
    start_time: datetime
    end_time: datetime
    sleep_time: datetime
    wake_time: datetime

    # Latencies (seconds)
    sleep_latency: int
    wakeup_latency: int
    light_latency: Optional[int]
    deep_latency: Optional[int]
    rem_latency: Optional[int]

    # Durations (seconds)
    time_in_bed: int
    time_in_sleep_period: int
    time_in_sleep: int
    time_in_wake: int
    time_in_light: int
    time_in_deep: int
    time_in_rem: int

    # Ratios (0.0-1.0)
    sleep_efficiency: float
    sleep_ratio: float
    wake_ratio: float
    light_ratio: float
    deep_ratio: float
    rem_ratio: float

    # Clusters
    waso_count: int
    longest_waso: int
    sleep_cycle: Optional[int]
    sleep_cycle_count: int
    sleep_cycle_time: List[datetime]
