"""
Sleep stage statistics calculator.

This module contains the main calculator class that processes sleep stage data
and computes comprehensive sleep metrics.
"""

from datetime import datetime, timedelta
from typing import List, Tuple

from ..stat import SleepStat
from .constants import (
    DEEP,
    LIGHT,
    REM,
    SECONDS_PER_EPOCH,
    THRESHOLD_REM_CLUSTER_DISTANCE,
    THRESHOLD_REM_COUNT,
    WAKE,
)
from .types import (
    SleepStageClusterMetric,
    SleepStageDuration,
    SleepStageLatency,
    SleepStageMoment,
    SleepStageRatio,
    SleepStageTime,
)


class SleepStageCalculator:
    """
    Main calculator for sleep stage statistics.

    This calculator processes sleep stage data (30-second epochs) and computes
    comprehensive sleep metrics including latencies, durations, ratios, and sleep score.

    Example:
        >>> from datetime import datetime
        >>> calculator = SleepStageCalculator()
        >>> start = datetime(2024, 1, 1, 22, 0, 0)
        >>> end = datetime(2024, 1, 2, 6, 0, 0)
        >>> stages = [0, 0, 1, 1, 2, 2, 3, 1, 1, 0, ...]
        >>> result = calculator.calculate(start, end, stages)
        >>> print(f"Sleep index: {result.sleep_index}")
    """

    def calculate(
        self,
        sleep_stages: List[int],
        start_time: datetime | None = None,
        end_time: datetime | None = None,
    ) -> SleepStat:
        """
        Calculate comprehensive sleep statistics from sleep stage data.

        Args:
            sleep_stages: List of sleep stage values (0=WAKE, 1=LIGHT, 2=DEEP, 3=REM)
                         Each value represents a 30-second epoch.
            start_time: Optional session start time. If None, uses epoch 0 as reference.
            end_time: Optional session end time. If None, calculated from start_time + duration.

        Returns:
            SleepStat object with all calculated metrics

        Raises:
            ValueError: If inputs are invalid (empty stages, end before start, etc.)

        Examples:
            # Simple hypnogram analysis (no datetime needed)
            >>> calc = SleepStageCalculator()
            >>> result = calc.calculate([0, 1, 1, 2, 2, 3, 1, 0])
            >>> print(result.sleep_efficiency)

            # With actual session times
            >>> start = datetime(2024, 1, 1, 22, 0, 0)
            >>> end = datetime(2024, 1, 2, 6, 0, 0)
            >>> result = calc.calculate([0, 1, 2, ...], start, end)
        """
        # Handle default datetime values if not provided
        if start_time is None:
            start_time = datetime(1970, 1, 1, 0, 0, 0)  # Use epoch as default

        if end_time is None:
            # Calculate from sleep_stages duration
            duration_seconds = len(sleep_stages) * SECONDS_PER_EPOCH
            end_time = start_time + timedelta(seconds=duration_seconds)

        # Validate inputs
        self._validate_inputs(start_time, end_time, sleep_stages)

        # Step 1: Calculate key moments (indices and counts)
        moments = self._calculate_key_moments(sleep_stages)

        # Step 2: Calculate latencies
        latencies = self._calculate_latencies(moments)

        # Step 3: Calculate time points
        times = self._calculate_times(start_time, end_time, latencies)

        # Step 4: Calculate cluster metrics (WASO, sleep cycles)
        clusters = self._calculate_cluster_metrics(times, moments, sleep_stages)

        # Step 5: Calculate durations
        durations = self._calculate_durations(times, moments)

        # Step 6: Calculate ratios
        ratios = self._calculate_ratios(durations)

        # Return complete statistics as SleepStat
        # Create the SleepStat object with all required fields
        result = SleepStat()

        # Set datetime fields
        result.start_time = start_time
        result.end_time = end_time
        result.sleep_time = times.sleep_time
        result.wake_time = times.wake_time

        # Convert latencies from seconds to timedelta
        result.sleep_latency = timedelta(seconds=latencies.sleep_latency)
        result.wakeup_latency = timedelta(seconds=latencies.wakeup_latency)
        result.light_latency = (
            timedelta(seconds=latencies.light_latency) if latencies.light_latency is not None else None
        )
        result.deep_latency = timedelta(seconds=latencies.deep_latency) if latencies.deep_latency is not None else None
        result.rem_latency = timedelta(seconds=latencies.rem_latency) if latencies.rem_latency is not None else None

        # Convert durations from seconds to timedelta
        result.time_in_bed = timedelta(seconds=durations.time_in_bed)
        result.time_in_sleep_period = timedelta(seconds=durations.time_in_sleep_period)
        result.time_in_sleep = timedelta(seconds=durations.time_in_sleep)
        result.time_in_wake = timedelta(seconds=durations.time_in_wake)
        result.time_in_light = timedelta(seconds=durations.time_in_light)
        result.time_in_deep = timedelta(seconds=durations.time_in_deep)
        result.time_in_rem = timedelta(seconds=durations.time_in_rem)

        # Set breathing-related fields to default values
        result.time_in_stable_breath = timedelta(0)
        result.time_in_unstable_breath = timedelta(0)
        result.time_in_snoring = timedelta(0)
        result.time_in_no_snoring = timedelta(0)

        # Set ratio fields
        result.sleep_efficiency = ratios.sleep_efficiency
        result.sleep_ratio = ratios.sleep_ratio
        result.wake_ratio = ratios.wake_ratio
        result.light_ratio = ratios.light_ratio
        result.deep_ratio = ratios.deep_ratio
        result.rem_ratio = ratios.rem_ratio

        # Set breathing ratios to defaults
        result.stable_breath_ratio = 0.0
        result.unstable_breath_ratio = 0.0
        result.snoring_ratio = 0.0
        result.no_snoring_ratio = 0.0

        # Set breathing pattern and index to defaults
        result.breathing_pattern = ""
        result.breathing_index = 0.0

        # Set WASO and cycle metrics
        result.waso_count = clusters.waso_count
        result.longest_waso = timedelta(seconds=clusters.longest_waso)
        result.sleep_cycle_count = clusters.sleep_cycle_count
        result.sleep_cycle = timedelta(seconds=clusters.sleep_cycle) if clusters.sleep_cycle is not None else None
        result.sleep_cycle_time = clusters.sleep_cycle_time

        # Set breathing counts to defaults
        result.unstable_breath_count = 0
        result.snoring_count = 0

        # Sleep index not calculated by this calculator
        result.sleep_index = None

        return result

    def _validate_inputs(self, start_time: datetime, end_time: datetime, sleep_stages: List[int]) -> None:
        """Validate input parameters."""
        if not sleep_stages:
            raise ValueError("sleep_stages cannot be empty")

        if end_time <= start_time:
            raise ValueError("end_time must be after start_time")

        valid_stages = {WAKE, LIGHT, DEEP, REM}
        if any(stage not in valid_stages for stage in sleep_stages):
            raise ValueError("Invalid sleep stage value. Must be 0, 1, 2, or 3")

    def _calculate_key_moments(self, sleep_stages: List[int]) -> SleepStageMoment:
        """
        Calculate key moment indices and stage counts.

        Args:
            sleep_stages: List of sleep stage values

        Returns:
            SleepStageMoment with all indices and counts
        """
        first_sleep_idx = -1
        first_light_idx = -1
        first_deep_idx = -1
        first_rem_idx = -1
        last_sleep_idx = -1
        last_stage_idx = len(sleep_stages) - 1

        wake_count = 0
        light_count = 0
        deep_count = 0
        rem_count = 0

        for idx, stage in enumerate(sleep_stages):
            # Track first sleep (any non-wake)
            if stage != WAKE:
                if first_sleep_idx == -1:
                    first_sleep_idx = idx
                last_sleep_idx = idx

            # Count and track first occurrence of each stage
            if stage == WAKE:
                wake_count += 1
            elif stage == LIGHT:
                if first_light_idx == -1:
                    first_light_idx = idx
                light_count += 1
            elif stage == DEEP:
                if first_deep_idx == -1:
                    first_deep_idx = idx
                deep_count += 1
            elif stage == REM:
                if first_rem_idx == -1:
                    first_rem_idx = idx
                rem_count += 1

        # Exclude leading wake and trailing wake from wake count
        if first_sleep_idx != -1:
            wake_count -= first_sleep_idx
            wake_count -= last_stage_idx - last_sleep_idx
        else:
            # No sleep at all - WASO count should be 0
            wake_count = 0

        sleep_count = light_count + deep_count + rem_count

        return SleepStageMoment(
            first_sleep_idx=first_sleep_idx,
            last_sleep_idx=last_sleep_idx,
            first_light_idx=first_light_idx,
            first_deep_idx=first_deep_idx,
            first_rem_idx=first_rem_idx,
            last_stage_idx=last_stage_idx,
            wake_count=wake_count,
            sleep_count=sleep_count,
            light_count=light_count,
            deep_count=deep_count,
            rem_count=rem_count,
        )

    def _calculate_latencies(self, moments: SleepStageMoment) -> SleepStageLatency:
        """
        Calculate latencies for each sleep stage.

        Args:
            moments: SleepStageMoment object with indices

        Returns:
            SleepStageLatency with all latency values in seconds
        """
        sleep_latency = moments.first_sleep_idx * SECONDS_PER_EPOCH
        wakeup_latency = (moments.last_stage_idx - moments.last_sleep_idx) * SECONDS_PER_EPOCH

        light_latency = (
            (moments.first_light_idx - moments.first_sleep_idx) * SECONDS_PER_EPOCH
            if moments.first_light_idx != -1
            else None
        )
        deep_latency = (
            (moments.first_deep_idx - moments.first_sleep_idx) * SECONDS_PER_EPOCH
            if moments.first_deep_idx != -1
            else None
        )
        rem_latency = (
            (moments.first_rem_idx - moments.first_sleep_idx) * SECONDS_PER_EPOCH
            if moments.first_rem_idx != -1
            else None
        )

        return SleepStageLatency(
            sleep_latency=sleep_latency,
            wakeup_latency=wakeup_latency,
            light_latency=light_latency,
            deep_latency=deep_latency,
            rem_latency=rem_latency,
        )

    def _calculate_times(
        self, start_time: datetime, end_time: datetime, latencies: SleepStageLatency
    ) -> SleepStageTime:
        """
        Calculate key time points from latencies.

        Args:
            start_time: Session start time
            end_time: Session end time
            latencies: Calculated latencies

        Returns:
            SleepStageTime with all time points
        """
        sleep_time = start_time + timedelta(seconds=latencies.sleep_latency)
        wake_time = end_time - timedelta(seconds=latencies.wakeup_latency)

        return SleepStageTime(
            start_time=start_time,
            end_time=end_time,
            sleep_time=sleep_time,
            wake_time=wake_time,
        )

    def _calculate_durations(self, times: SleepStageTime, moments: SleepStageMoment) -> SleepStageDuration:
        """
        Calculate durations for each sleep stage.

        Args:
            times: Key time points
            moments: Key moments with counts

        Returns:
            SleepStageDuration with all duration values in seconds
        """
        time_in_bed = int((times.end_time - times.start_time).total_seconds())
        time_in_wake = moments.wake_count * SECONDS_PER_EPOCH
        time_in_light = moments.light_count * SECONDS_PER_EPOCH
        time_in_deep = moments.deep_count * SECONDS_PER_EPOCH
        time_in_rem = moments.rem_count * SECONDS_PER_EPOCH
        time_in_sleep = time_in_light + time_in_deep + time_in_rem
        time_in_sleep_period = time_in_sleep + time_in_wake

        return SleepStageDuration(
            time_in_bed=time_in_bed,
            time_in_sleep_period=time_in_sleep_period,
            time_in_sleep=time_in_sleep,
            time_in_wake=time_in_wake,
            time_in_light=time_in_light,
            time_in_deep=time_in_deep,
            time_in_rem=time_in_rem,
        )

    def _calculate_ratios(self, durations: SleepStageDuration) -> SleepStageRatio:
        """
        Calculate ratios for sleep efficiency and stage distributions.

        Args:
            durations: Calculated durations

        Returns:
            SleepStageRatio with all ratio values (0.0-1.0)
        """
        # Avoid division by zero
        if durations.time_in_bed > 0:
            sleep_efficiency = durations.time_in_sleep / durations.time_in_bed
        else:
            sleep_efficiency = 0.0

        if durations.time_in_sleep_period > 0:
            sleep_ratio = durations.time_in_sleep / durations.time_in_sleep_period
            wake_ratio = durations.time_in_wake / durations.time_in_sleep_period
            light_ratio = durations.time_in_light / durations.time_in_sleep_period
            deep_ratio = durations.time_in_deep / durations.time_in_sleep_period
            rem_ratio = durations.time_in_rem / durations.time_in_sleep_period
        else:
            sleep_ratio = 0.0
            wake_ratio = 0.0
            light_ratio = 0.0
            deep_ratio = 0.0
            rem_ratio = 0.0

        return SleepStageRatio(
            sleep_efficiency=sleep_efficiency,
            sleep_ratio=sleep_ratio,
            wake_ratio=wake_ratio,
            light_ratio=light_ratio,
            deep_ratio=deep_ratio,
            rem_ratio=rem_ratio,
        )

    def _calculate_wake_cluster_indices(self, moments: SleepStageMoment, sleep_stages: List[int]) -> Tuple[int, int]:
        """
        Calculate WASO (Wake After Sleep Onset) metrics.

        Args:
            moments: Key moments with indices
            sleep_stages: List of sleep stage values

        Returns:
            Tuple of (wake_cluster_count, longest_wake_count_in_epochs)
        """
        start = moments.first_sleep_idx
        end = moments.last_sleep_idx

        wake_cls_start = -1
        wake_cls_count = 0
        longest_wake_count = 0

        for idx in range(start, end + 1):
            stage = sleep_stages[idx]

            # Start of a wake cluster
            if stage == WAKE and wake_cls_start == -1:
                wake_cls_start = idx

            # End of a wake cluster
            if stage != WAKE and wake_cls_start != -1:
                cluster_length = idx - wake_cls_start
                longest_wake_count = max(longest_wake_count, cluster_length)
                wake_cls_count += 1
                wake_cls_start = -1

            # Handle wake cluster at the end
            if idx == end and wake_cls_start != -1:
                cluster_length = idx - wake_cls_start + 1
                longest_wake_count = max(longest_wake_count, cluster_length)
                wake_cls_count += 1

        return wake_cls_count, longest_wake_count

    def _calculate_rem_cluster_indices(
        self, moments: SleepStageMoment, sleep_stages: List[int]
    ) -> Tuple[List[int], List[int]]:
        """
        Calculate REM cluster start and end indices.

        Args:
            moments: Key moments with indices
            sleep_stages: List of sleep stage values

        Returns:
            Tuple of (cluster_starts, cluster_ends)
        """
        start = moments.first_sleep_idx
        end = moments.last_sleep_idx

        rem_cls_start = -1
        rem_cls_end = -1
        rem_cls_starts = []
        rem_cls_ends = []

        distance = 0
        rem_count = 0

        for idx in range(start, end + 1):
            stage = sleep_stages[idx]

            # Check if we should start a new cluster
            if stage == REM and distance > THRESHOLD_REM_CLUSTER_DISTANCE:
                # Save previous cluster if valid
                if rem_count >= THRESHOLD_REM_COUNT:
                    rem_cls_starts.append(rem_cls_start)
                    rem_cls_ends.append(rem_cls_end)

                # Start new cluster
                rem_cls_start = idx
                rem_cls_end = idx
                rem_count = 1
                distance = 0
            elif stage == REM and distance <= THRESHOLD_REM_CLUSTER_DISTANCE:
                # Continue current cluster
                distance = 0
            elif stage != REM:
                # Non-REM: increment distance
                distance += 1

            # Update cluster if in REM
            if stage == REM:
                if rem_cls_start == -1:
                    rem_cls_start = idx
                rem_cls_end = idx
                rem_count += 1

        # Save last cluster if valid
        if rem_count >= THRESHOLD_REM_COUNT:
            rem_cls_starts.append(rem_cls_start)
            rem_cls_ends.append(rem_cls_end)

        return rem_cls_starts, rem_cls_ends

    def _calculate_average_cluster_distance(self, moments: SleepStageMoment, cluster_ends: List[int]) -> float | None:
        """
        Calculate average distance between REM cluster endpoints.

        Args:
            moments: Key moments with indices
            cluster_ends: List of REM cluster end indices

        Returns:
            Average distance in epochs, or None if no clusters
        """
        if len(cluster_ends) == 0:
            return None

        total_distance = cluster_ends[0] - moments.first_sleep_idx
        total_distance += sum(cluster_ends[idx + 1] - cluster_ends[idx] for idx in range(len(cluster_ends) - 1))

        return total_distance / len(cluster_ends)

    def _calculate_sleep_cycle_time(
        self, moments: SleepStageMoment, times: SleepStageTime, cluster_ends: List[int]
    ) -> List[datetime]:
        """
        Calculate datetime for each sleep cycle endpoint.

        Args:
            moments: Key moments with indices
            times: Key time points
            cluster_ends: List of REM cluster end indices

        Returns:
            List of datetime values for cycle endpoints
        """
        if len(cluster_ends) == 0:
            return []

        sleep_cycle_time = [times.sleep_time]

        for cluster_end in cluster_ends:
            epochs_from_sleep = cluster_end - moments.first_sleep_idx
            cluster_end_time = times.sleep_time + timedelta(seconds=epochs_from_sleep * SECONDS_PER_EPOCH)
            sleep_cycle_time.append(cluster_end_time)

        return sleep_cycle_time

    def _calculate_cluster_metrics(
        self, times: SleepStageTime, moments: SleepStageMoment, sleep_stages: List[int]
    ) -> SleepStageClusterMetric:
        """
        Calculate all cluster-related metrics.

        Args:
            times: Key time points
            moments: Key moments with indices
            sleep_stages: List of sleep stage values

        Returns:
            SleepStageClusterMetric with all cluster metrics
        """
        wake_cluster_count, longest_wake_count = self._calculate_wake_cluster_indices(moments, sleep_stages)
        rem_cluster_starts, rem_cluster_ends = self._calculate_rem_cluster_indices(moments, sleep_stages)

        sleep_cycle_time = self._calculate_sleep_cycle_time(moments, times, rem_cluster_ends)

        average_rem_cluster_distance = self._calculate_average_cluster_distance(moments, rem_cluster_ends)

        sleep_cycle = (
            int(average_rem_cluster_distance * SECONDS_PER_EPOCH) if average_rem_cluster_distance is not None else None
        )

        return SleepStageClusterMetric(
            waso_count=wake_cluster_count,
            longest_waso=longest_wake_count * SECONDS_PER_EPOCH,
            sleep_cycle=sleep_cycle,
            sleep_cycle_count=len(rem_cluster_starts),
            sleep_cycle_time=sleep_cycle_time,
        )
