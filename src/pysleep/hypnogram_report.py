"""Hypnogram report generation utilities for sleep data analysis."""

import json
from datetime import datetime, timedelta
from itertools import groupby
from typing import Any

from .label import DEEP, LIGHT, REM, WAKE

EPOCH_DURATION = 30  # seconds per epoch

# Sleep stage mapping using labels from label.py
STAGE_MAP = {WAKE: "Wake", LIGHT: "Light", DEEP: "Deep", REM: "REM"}


def extract_events_from_hypnogram(hypnogram_data: list[int]) -> list[dict[str, Any]]:
    """
    Extract sleep stage events from numeric hypnogram data using groupby.

    This approach is optimal for sleep data because:
    - Cleanest, most Pythonic code
    - Best performance for typical sleep data (8-10 hours)
    - No external dependencies
    - Memory efficient

    Args:
        hypnogram_data: List of integers (0-4) representing sleep stages

    Returns:
        List of events with start_epoch, stage name, and duration
    """

    if not hypnogram_data:
        return []

    events = []
    start_epoch = 0

    for stage, group in groupby(hypnogram_data):
        duration_epochs = len(list(group))
        duration_seconds = duration_epochs * EPOCH_DURATION

        events.append(
            {
                "start_epoch": start_epoch,
                "stage": STAGE_MAP.get(stage, f"Unknown({stage})"),
                "duration": format_duration(duration_seconds),
            }
        )

        start_epoch += duration_epochs

    return events


def calculate_stage_summary(hypnogram_data: list[int]) -> dict[str, dict[str, Any]]:
    """
    Calculate summary statistics for each sleep stage.

    Args:
        hypnogram_data: List of integers (0-4) representing sleep stages

    Returns:
        Dictionary with duration and percentage for each stage
    """
    if not hypnogram_data:
        return {}

    total_epochs = len(hypnogram_data)
    stage_counts = {}

    # Count epochs for each stage
    for stage in hypnogram_data:
        stage_name = STAGE_MAP.get(stage, f"Unknown({stage})")
        stage_counts[stage_name] = stage_counts.get(stage_name, 0) + 1

    # Calculate duration and percentage
    summary = {}
    for stage_name, count in stage_counts.items():
        duration_seconds = count * EPOCH_DURATION
        percentage = (count / total_epochs) * 100
        summary[stage_name] = {"duration": format_duration(duration_seconds), "percentage": f"{percentage:.1f}%"}

    return summary


def format_duration(seconds: int) -> str:
    """Format duration in seconds to verbose format like '2h 30m 45s'.

    Omits zero values for cleaner output:
    - 0 seconds -> "0s"
    - 300 seconds -> "5m"
    - 3600 seconds -> "1h"
    - 3665 seconds -> "1h 1m 5s"
    """
    if seconds == 0:
        return "0s"

    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    secs = seconds % 60

    parts = []
    if hours > 0:
        parts.append(f"{hours}h")
    if minutes > 0:
        parts.append(f"{minutes}m")
    # Only add seconds if they're non-zero OR if there are no other units
    if secs > 0 or (hours == 0 and minutes == 0):
        parts.append(f"{secs}s")

    return " ".join(parts)


def parse_time(time_str: str) -> datetime | None:
    """Parse a time string to datetime object."""
    if not time_str:
        return None
    try:
        return datetime.strptime(time_str, "%Y-%m-%d %H:%M:%S")
    except (ValueError, TypeError):
        return None


def format_time_range(start_dt: datetime, end_dt: datetime) -> str:
    """Format a time range for display."""
    return f"{start_dt.strftime('%I:%M %p')} - {end_dt.strftime('%I:%M %p')}"


def calculate_end_time(start_dt: datetime, num_epochs: int) -> datetime:
    """Calculate end time based on start time and number of epochs."""
    duration_seconds = num_epochs * EPOCH_DURATION
    return start_dt + timedelta(seconds=duration_seconds)


def create_stage_summary(summary: dict[str, dict[str, Any]]) -> dict[str, list[Any]]:
    """Convert stage summary to [duration, percentage] format."""
    return {stage: [data["duration"], data["percentage"]] for stage, data in summary.items()}


def group_events_by_hour(events: list[dict[str, Any]], start_dt: datetime | None) -> list[dict[str, Any]]:
    """Group sleep stage events by hour."""
    if not start_dt:
        # No time info - return all events in one group
        return [
            {
                "hour_range": "All Events",
                "stages": [[i, event["stage"], event["duration"]] for i, event in enumerate(events, 1)],
            }
        ]

    grouped_hours = []
    current_hour = start_dt.replace(minute=0, second=0, microsecond=0)
    next_hour = current_hour + timedelta(hours=1)

    hour_data = {"hour_range": format_time_range(current_hour, next_hour), "stages": []}

    for i, event in enumerate(events, 1):
        # Calculate actual time for this event
        event_start_seconds = event["start_epoch"] * EPOCH_DURATION
        event_start_time = start_dt + timedelta(seconds=event_start_seconds)

        # Check if we've moved to the next hour
        while event_start_time >= next_hour:
            # Add current hour data if it has events
            if hour_data["stages"]:
                grouped_hours.append(hour_data)

            # Move to next hour
            current_hour = next_hour
            next_hour = current_hour + timedelta(hours=1)
            hour_data = {"hour_range": format_time_range(current_hour, next_hour), "stages": []}

        # Add event to current hour as [index, stage, duration]
        hour_data["stages"].append([i, event["stage"], event["duration"]])

    # Add remaining hour data
    if hour_data["stages"]:
        grouped_hours.append(hour_data)

    return grouped_hours


def generate_basic_stage_report(
    hypnogram_data: list[Any],
    events: list[dict[str, Any]],
    summary: dict[str, dict[str, Any]],
) -> dict[str, Any]:
    """
    Generate basic stage report without time dependency.

    Args:
        hypnogram_data: List of sleep stage data for each epoch
        events: List of sleep stage events with start_epoch, stage, and duration
        summary: Dictionary of sleep stage summaries with duration and percentage

    Returns:
        Dictionary containing basic sleep stage information
    """
    return {
        "sleep_time": "",  # Will be filled by add_time_grouping if time info available
        "duration": format_duration(len(hypnogram_data) * EPOCH_DURATION),
        "sleep_stage_summary": create_stage_summary(summary),
        "sleep_stages_by_hour": [],  # Will be filled by add_time_grouping
    }


def add_time_grouping(
    report: dict[str, Any],
    events: list[dict[str, Any]],
    start_time: datetime | None,
    end_time: datetime | None = None,
) -> dict[str, Any]:
    """Add time-based grouping to report."""
    # Update sleep time if available
    if start_time and end_time:
        report["sleep_time"] = format_time_range(start_time, end_time)

    # Group stages by hour
    if start_time:
        report["sleep_stages_by_hour"] = group_events_by_hour(events, start_time)
    else:
        # No time info - all events in one group
        report["sleep_stages_by_hour"] = [
            {
                "hour_range": "All Events",
                "stages": [[i, event["stage"], event["duration"]] for i, event in enumerate(events, 1)],
            }
        ]

    return report


def format_json_compact(report: dict[str, Any]) -> str:
    """
    Format report dictionary as compact JSON with inline stage arrays.

    Keeps [index, stage, duration] arrays on single lines for readability
    while maintaining proper JSON structure.

    Args:
        report: Sleep report dictionary from generate_json_report

    Returns:
        Formatted JSON string with compact stage arrays
    """

    def format_value(obj, indent=0):
        """Recursively format JSON with special handling for stage arrays."""
        spaces = "  " * indent

        if isinstance(obj, dict):
            if not obj:
                return "{}"

            lines = ["{"]
            items = list(obj.items())
            for i, (key, value) in enumerate(items):
                # Check if this is a stages array
                if key == "stages" and isinstance(value, list) and value:
                    # Format stages array compactly
                    lines.append(f'{spaces}  "{key}": [')
                    for j, stage in enumerate(value):
                        if isinstance(stage, list) and len(stage) == 3:
                            # Format [index, stage, duration] on one line
                            formatted_stage = json.dumps(stage)
                            comma = "," if j < len(value) - 1 else ""
                            lines.append(f"{spaces}    {formatted_stage}{comma}")
                        else:
                            # Fallback for unexpected format
                            comma = "," if j < len(value) - 1 else ""
                            lines.append(f"{spaces}    {json.dumps(stage)}{comma}")
                    lines.append(f"{spaces}  ]" + ("," if i < len(items) - 1 else ""))
                elif key == "sleep_stages_by_hour" and isinstance(value, list):
                    # Special handling for hour groups
                    lines.append(f'{spaces}  "{key}": [')
                    for j, hour_group in enumerate(value):
                        lines.append(f"{spaces}    {{")
                        lines.append(f'{spaces}      "hour_range": {json.dumps(hour_group.get("hour_range", ""))},')
                        stages = hour_group.get("stages", [])
                        lines.append(f'{spaces}      "stages": [')
                        for k, stage in enumerate(stages):
                            comma = "," if k < len(stages) - 1 else ""
                            lines.append(f"{spaces}        {json.dumps(stage)}{comma}")
                        lines.append(f"{spaces}      ]")
                        lines.append(f"{spaces}    }}" + ("," if j < len(value) - 1 else ""))
                    lines.append(f"{spaces}  ]" + ("," if i < len(items) - 1 else ""))
                else:
                    # Regular key-value pair
                    formatted_value = (
                        json.dumps(value) if not isinstance(value, (dict, list)) else format_value(value, indent + 1)
                    )
                    comma = "," if i < len(items) - 1 else ""
                    lines.append(f'{spaces}  "{key}": {formatted_value}{comma}')
            lines.append(spaces + "}")
            return "\n".join(lines)

        elif isinstance(obj, list):
            # For simple lists, use default JSON formatting
            return json.dumps(obj)

        else:
            return json.dumps(obj)

    return format_value(report)


def generate_hypnogram_report(
    hypnogram_data: list[int],
    start_time: str = "",
    end_time: str = "",
    compact: bool = True,
) -> str | dict[str, Any]:
    """
    Generate a complete hypnogram report from raw data.

    This is the main function that handles the entire pipeline:
    1. Extract events from hypnogram data
    2. Calculate sleep stage summary
    3. Generate the report with optional time info
    4. Format as compact JSON or return raw dict

    Args:
        hypnogram_data: List of integers (0-3) representing sleep stages
        start_time: Optional start time in "YYYY-MM-DD HH:MM:SS" format
        end_time: Optional end time in "YYYY-MM-DD HH:MM:SS" format
        compact: If True, return formatted compact JSON string. If False, return dict

    Returns:
        Formatted JSON string if compact=True, otherwise dictionary

    Example:
        >>> data = [0]*120 + [1]*60 + [2]*80 + [3]*40
        >>> report = generate_hypnogram_report(data, "2024-01-15 23:00:00", "2024-01-16 01:30:00")
        >>> print(report)  # Prints compact JSON
    """
    # Extract events and calculate summary
    events = extract_events_from_hypnogram(hypnogram_data)
    summary = calculate_stage_summary(hypnogram_data)

    # Generate basic report structure
    report = generate_basic_stage_report(hypnogram_data, events, summary)

    # Parse times if provided
    start_dt = parse_time(start_time)
    end_dt = parse_time(end_time)

    # Calculate end time if needed
    if start_dt and end_dt == start_dt and hypnogram_data:
        end_dt = calculate_end_time(start_dt, len(hypnogram_data))

    # Add time-based enhancements
    report = add_time_grouping(report, events, start_dt, end_dt)

    # Return formatted or raw based on preference
    return format_json_compact(report) if compact else report
