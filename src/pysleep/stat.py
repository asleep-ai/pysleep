from datetime import datetime, timedelta
from zoneinfo import ZoneInfo


class SleepStat:
    sleep_time: datetime
    wake_time: datetime
    sleep_latency: timedelta
    wakeup_latency: timedelta
    light_latency: timedelta | None = None
    deep_latency: timedelta | None = None
    rem_latency: timedelta | None = None
    time_in_bed: timedelta
    time_in_sleep_period: timedelta
    time_in_sleep: timedelta
    time_in_wake: timedelta
    time_in_light: timedelta
    time_in_deep: timedelta
    time_in_rem: timedelta
    time_in_stable_breath: timedelta
    time_in_unstable_breath: timedelta
    time_in_snoring: timedelta
    sleep_efficiency: float
    sleep_ratio: float
    wake_ratio: float
    light_ratio: float
    deep_ratio: float
    rem_ratio: float
    stable_breath_ratio: float
    unstable_breath_ratio: float
    snoring_ratio: float
    breathing_pattern: str
    breathing_index: float
    waso_count: int | None = None
    longest_waso: timedelta | None = None
    sleep_cycle_count: int | None = None
    sleep_cycle: timedelta | None = None
    unstable_breath_count: int
    snoring_count: int
    sleep_index: int | None = None
    sleep_cycle_time: list[datetime]

    def update_to_timezone(self, tz_str: str):
        tz = ZoneInfo(tz_str)
        self.sleep_time = self.sleep_time.astimezone(tz)
        self.wake_time = self.wake_time.astimezone(tz)
        self.sleep_cycle_time = [t.astimezone(tz) for t in self.sleep_cycle_time]

    def __sub__(self, other: "SleepStat") -> "SleepStatDelta":
        """
        Calculate the difference between two SleepStat instances.

        Args:
            other (SleepStat): The other SleepStat instance to subtract from this instance.
        """
        return SleepStatDelta(
            sleep_time=subtract_relative_time(self.sleep_time, other.sleep_time),
            wake_time=subtract_relative_time(self.wake_time, other.wake_time),
            sleep_latency=self.sleep_latency - other.sleep_latency,
            wakeup_latency=self.wakeup_latency - other.wakeup_latency,
            time_in_bed=self.time_in_bed - other.time_in_bed,
            time_in_sleep_period=self.time_in_sleep_period - other.time_in_sleep_period,
            time_in_sleep=self.time_in_sleep - other.time_in_sleep,
            time_in_wake=self.time_in_wake - other.time_in_wake,
            time_in_light=self.time_in_light - other.time_in_light,
            time_in_deep=self.time_in_deep - other.time_in_deep,
            time_in_rem=self.time_in_rem - other.time_in_rem,
            time_in_stable_breath=self.time_in_stable_breath - other.time_in_stable_breath,
            time_in_unstable_breath=self.time_in_unstable_breath - other.time_in_unstable_breath,
            time_in_snoring=self.time_in_snoring - other.time_in_snoring,
            sleep_efficiency=self.sleep_efficiency - other.sleep_efficiency,
            sleep_ratio=(self.sleep_ratio, other.sleep_ratio),
            wake_ratio=self.wake_ratio - other.wake_ratio,
            light_ratio=self.light_ratio - other.light_ratio,
            deep_ratio=self.deep_ratio - other.deep_ratio,
            rem_ratio=self.rem_ratio - other.rem_ratio,
            stable_breath_ratio=self.stable_breath_ratio - other.stable_breath_ratio,
            unstable_breath_ratio=self.unstable_breath_ratio - other.unstable_breath_ratio,
            snoring_ratio=self.snoring_ratio - other.snoring_ratio,
            breathing_index=self.breathing_index - other.breathing_index,
            unstable_breath_count=self.unstable_breath_count - other.unstable_breath_count,
            snoring_count=self.snoring_count - other.snoring_count,
            light_latency=subtract_if_not_none(self.light_latency, other.light_latency),
            deep_latency=subtract_if_not_none(self.deep_latency, other.deep_latency),
            rem_latency=subtract_if_not_none(self.rem_latency, other.rem_latency),
            waso_count=subtract_if_not_none(self.waso_count, other.waso_count),
            longest_waso=subtract_if_not_none(self.longest_waso, other.longest_waso),
            sleep_cycle_count=subtract_if_not_none(self.sleep_cycle_count, other.sleep_cycle_count),
            sleep_cycle=subtract_if_not_none(self.sleep_cycle, other.sleep_cycle),
            sleep_index=subtract_if_not_none(self.sleep_index, other.sleep_index),
        )


class SleepStatDelta:
    """
    A class to represent the difference between two SleepStat instances.
    It contains the differences in various sleep metrics.
    """

    def __init__(
        self,
        sleep_time: timedelta,
        wake_time: timedelta,
        sleep_latency: timedelta,
        wakeup_latency: timedelta,
        time_in_bed: timedelta,
        time_in_sleep_period: timedelta,
        time_in_sleep: timedelta,
        time_in_wake: timedelta,
        time_in_light: timedelta,
        time_in_deep: timedelta,
        time_in_rem: timedelta,
        time_in_stable_breath: timedelta,
        time_in_unstable_breath: timedelta,
        time_in_snoring: timedelta,
        sleep_efficiency: float,
        sleep_ratio: float,
        wake_ratio: float,
        light_ratio: float,
        deep_ratio: float,
        rem_ratio: float,
        stable_breath_ratio: float,
        unstable_breath_ratio: float,
        snoring_ratio: float,
        breathing_index: float,
        unstable_breath_count: int,
        snoring_count: int,
        light_latency: timedelta | None = None,
        deep_latency: timedelta | None = None,
        rem_latency: timedelta | None = None,
        waso_count: int | None = None,
        longest_waso: timedelta | None = None,
        sleep_cycle_count: int | None = None,
        sleep_cycle: timedelta | None = None,
        sleep_index: int | None = None,
    ):
        self.sleep_time = sleep_time
        self.wake_time = wake_time
        self.sleep_index = sleep_index
        self.sleep_latency = sleep_latency
        self.wakeup_latency = wakeup_latency
        self.light_latency = light_latency
        self.deep_latency = deep_latency
        self.rem_latency = rem_latency
        self.time_in_bed = time_in_bed
        self.time_in_sleep_period = time_in_sleep_period
        self.time_in_sleep = time_in_sleep
        self.time_in_wake = time_in_wake
        self.time_in_light = time_in_light
        self.time_in_deep = time_in_deep
        self.time_in_rem = time_in_rem
        self.time_in_stable_breath = time_in_stable_breath
        self.time_in_unstable_breath = time_in_unstable_breath
        self.time_in_snoring = time_in_snoring
        self.sleep_efficiency = sleep_efficiency
        self.sleep_ratio = sleep_ratio
        self.wake_ratio = wake_ratio
        self.light_ratio = light_ratio
        self.deep_ratio = deep_ratio
        self.rem_ratio = rem_ratio
        self.stable_breath_ratio = stable_breath_ratio
        self.unstable_breath_ratio = unstable_breath_ratio
        self.snoring_ratio = snoring_ratio
        self.breathing_index = breathing_index
        self.waso_count = waso_count
        self.longest_waso = longest_waso
        self.sleep_cycle_count = sleep_cycle_count
        self.sleep_cycle = sleep_cycle
        self.unstable_breath_count = unstable_breath_count
        self.snoring_count = snoring_count


def subtract_if_not_none(a, b):
    if a is not None and b is not None:
        return a - b
    return None


def subtract_relative_time(dt1: datetime, dt2: datetime) -> timedelta:
    dt1_time = datetime.combine(datetime.min, dt1.time())
    dt2_time = datetime.combine(datetime.min, dt2.time())
    delta_seconds = (dt1_time - dt2_time).total_seconds()
    delta_seconds_mod = ((delta_seconds + 12 * 3600) % (24 * 3600)) - 12 * 3600

    if delta_seconds_mod == -12 * 3600:
        delta_seconds_mod = 12 * 3600

    return timedelta(seconds=delta_seconds_mod)
