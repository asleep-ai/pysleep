from datetime import datetime, timedelta
from zoneinfo import ZoneInfo


class SleepStat:
    sleep_time: datetime
    wake_time: datetime
    sleep_index: int
    sleep_latency: timedelta
    wakeup_latency: timedelta
    light_latency: timedelta
    deep_latency: timedelta
    rem_latency: timedelta
    time_in_bed: timedelta
    time_in_sleep_period: timedelta
    time_in_sleep: timedelta
    time_in_wake: timedelta
    time_in_light: timedelta
    time_in_deep: timedelta
    time_in_rem: timedelta
    time_in_stable_breath: timedelta
    time_in_unstable_breath: timedelta
    time_in_snoring: timedelta | None = None
    time_in_no_snoring: timedelta | None = None
    sleep_efficiency: float
    sleep_ratio: float | None = None
    wake_ratio: float | None = None
    light_ratio: float | None = None
    deep_ratio: float | None = None
    rem_ratio: float | None = None
    stable_breath_ratio: float | None = None
    unstable_breath_ratio: float | None = None
    snoring_ratio: float | None = None
    no_snoring_ratio: float | None = None
    breathing_index: float
    breathing_pattern: str
    waso_count: int | None = None
    longest_waso: timedelta | None = None
    sleep_cycle_count: int | None = None
    sleep_cycle: timedelta | None = None
    sleep_cycle_time: list[datetime]
    unstable_breath_count: int | None = None
    snoring_count: int | None = None

    def update_to_timezone(self, tz_str: str):
        tz = ZoneInfo(tz_str)
        self.sleep_time = self.sleep_time.astimezone(tz)
        self.wake_time = self.wake_time.astimezone(tz)
        self.sleep_cycle_time = [t.astimezone(tz) for t in self.sleep_cycle_time]

    def __sub__(self, other: "SleepStat") -> "SleepStatDelta":
        return SleepStatDelta(
            sleep_time=subtract_relative_time(self.sleep_time, other.sleep_time),
            wake_time=subtract_relative_time(self.wake_time, other.wake_time),
            sleep_index=self.sleep_index - other.sleep_index,
            sleep_latency=self.sleep_latency - other.sleep_latency,
            wakeup_latency=self.wakeup_latency - other.wakeup_latency,
            light_latency=self.light_latency - other.light_latency,
            deep_latency=self.deep_latency - other.deep_latency,
            rem_latency=self.rem_latency - other.rem_latency,
            time_in_bed=self.time_in_bed - other.time_in_bed,
            time_in_sleep_period=self.time_in_sleep_period - other.time_in_sleep_period,
            time_in_sleep=self.time_in_sleep - other.time_in_sleep,
            time_in_wake=self.time_in_wake - other.time_in_wake,
            time_in_light=self.time_in_light - other.time_in_light,
            time_in_deep=self.time_in_deep - other.time_in_deep,
            time_in_rem=self.time_in_rem - other.time_in_rem,
            time_in_stable_breath=self.time_in_stable_breath - other.time_in_stable_breath,
            time_in_unstable_breath=self.time_in_unstable_breath - other.time_in_unstable_breath,
            time_in_snoring=self.time_in_snoring - other.time_in_snoring
            if self.time_in_snoring and other.time_in_snoring
            else None,
            time_in_no_snoring=self.time_in_no_snoring - other.time_in_no_snoring
            if self.time_in_no_snoring and other.time_in_no_snoring
            else None,
            sleep_efficiency=self.sleep_efficiency - other.sleep_efficiency,
            sleep_ratio=self.sleep_ratio - other.sleep_ratio if self.sleep_ratio and other.sleep_ratio else None,
            wake_ratio=self.wake_ratio - other.wake_ratio if self.wake_ratio and other.wake_ratio else None,
            light_ratio=self.light_ratio - other.light_ratio if self.light_ratio and other.light_ratio else None,
            deep_ratio=self.deep_ratio - other.deep_ratio if self.deep_ratio and other.deep_ratio else None,
            rem_ratio=self.rem_ratio - other.rem_ratio if self.rem_ratio and other.rem_ratio else None,
            stable_breath_ratio=self.stable_breath_ratio - other.stable_breath_ratio
            if self.stable_breath_ratio and other.stable_breath_ratio
            else None,
            unstable_breath_ratio=self.unstable_breath_ratio - other.unstable_breath_ratio
            if self.unstable_breath_ratio and other.unstable_breath_ratio
            else None,
            snoring_ratio=self.snoring_ratio - other.snoring_ratio
            if self.snoring_ratio and other.snoring_ratio
            else None,
            no_snoring_ratio=self.no_snoring_ratio - other.no_snoring_ratio
            if self.no_snoring_ratio and other.no_snoring_ratio
            else None,
            breathing_index=self.breathing_index - other.breathing_index,
            waso_count=self.waso_count - other.waso_count if self.waso_count and other.waso_count else None,
            longest_waso=self.longest_waso - other.longest_waso if self.longest_waso and other.longest_waso else None,
            sleep_cycle_count=self.sleep_cycle_count - other.sleep_cycle_count
            if self.sleep_cycle_count and other.sleep_cycle_count
            else None,
            sleep_cycle=self.sleep_cycle - other.sleep_cycle if self.sleep_cycle and other.sleep_cycle else None,
            unstable_breath_count=self.unstable_breath_count - other.unstable_breath_count
            if self.unstable_breath_count and other.unstable_breath_count
            else None,
            snoring_count=self.snoring_count - other.snoring_count if self.snoring_count and other.snoring_count else None 
        )


class SleepStatDelta:
    def __init__(
        self,
        sleep_time: timedelta,
        wake_time: timedelta,
        sleep_index: int,
        sleep_latency: timedelta,
        wakeup_latency: timedelta,
        light_latency: timedelta,
        deep_latency: timedelta,
        rem_latency: timedelta,
        time_in_bed: timedelta,
        time_in_sleep_period: timedelta,
        time_in_sleep: timedelta,
        time_in_wake: timedelta,
        time_in_light: timedelta,
        time_in_deep: timedelta,
        time_in_rem: timedelta,
        time_in_stable_breath: timedelta,
        time_in_unstable_breath: timedelta,
        sleep_efficiency: float,
        breathing_index: float,
        time_in_snoring: timedelta | None = None,
        time_in_no_snoring: timedelta | None = None,
        sleep_ratio: float | None = None,
        wake_ratio: float | None = None,
        light_ratio: float | None = None,
        deep_ratio: float | None = None,
        rem_ratio: float | None = None,
        stable_breath_ratio: float | None = None,
        unstable_breath_ratio: float | None = None,
        snoring_ratio: float | None = None,
        no_snoring_ratio: float | None = None,
        waso_count: int | None = None,
        longest_waso: timedelta | None = None,
        sleep_cycle_count: int | None = None,
        sleep_cycle: timedelta | None = None,
        unstable_breath_count: int | None = None,
        snoring_count: int | None = None,
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
        self.time_in_no_snoring = time_in_no_snoring
        self.sleep_efficiency = sleep_efficiency
        self.sleep_ratio = sleep_ratio
        self.wake_ratio = wake_ratio
        self.light_ratio = light_ratio
        self.deep_ratio = deep_ratio
        self.rem_ratio = rem_ratio
        self.stable_breath_ratio = stable_breath_ratio
        self.unstable_breath_ratio = unstable_breath_ratio
        self.snoring_ratio = snoring_ratio
        self.no_snoring_ratio = no_snoring_ratio
        self.breathing_index = breathing_index
        self.waso_count = waso_count
        self.longest_waso = longest_waso
        self.sleep_cycle_count = sleep_cycle_count
        self.sleep_cycle = sleep_cycle
        self.unstable_breath_count = unstable_breath_count
        self.snoring_count = snoring_count


def subtract_relative_time(dt1: datetime, dt2: datetime) -> timedelta:
    dt1_time = datetime.combine(datetime.min, dt1.time())
    dt2_time = datetime.combine(datetime.min, dt2.time())
    delta_seconds = (dt1_time - dt2_time).total_seconds()
    delta_seconds_mod = ((delta_seconds + 12 * 3600) % (24 * 3600)) - 12 * 3600

    if delta_seconds_mod == -12 * 3600:
        delta_seconds_mod = 12 * 3600

    return timedelta(seconds=delta_seconds_mod)
