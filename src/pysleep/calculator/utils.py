"""Utility functions for sleep stage calculations."""


def round_second(value: float | None) -> float | None:
    """
    Round a number to 2 decimal places using half-to-even rounding.

    Python 3's built-in round() function uses banker's rounding (half-to-even)
    by default, which reduces bias by rounding 0.5 to the nearest even number.

    Examples:
        >>> round_second(0.125)
        0.12
        >>> round_second(0.135)
        0.14
        >>> round_second(0.5)
        0.5
        >>> round_second(1.5)
        1.5
        >>> round_second(2.5)
        2.5
        >>> round_second(None)
        None

    Args:
        value: Number to round, or None

    Returns:
        Number rounded to 2 decimal places, or None if input is None
    """
    return round(value, 2) if value is not None else None
