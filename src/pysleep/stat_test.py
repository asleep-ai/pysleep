import unittest
from datetime import datetime, timedelta, timezone

from parameterized import parameterized

from .stat import subtract_relative_time


class TestSubtractTime(unittest.TestCase):
    @parameterized.expand(
        [
            ("positive_diff", datetime(2023, 10, 2, 0, 10), datetime(2023, 10, 1, 23, 50), timedelta(minutes=20)),
            (
                "negative_diff",
                datetime(2023, 10, 1, 23, 40),
                datetime(2023, 10, 1, 23, 50),
                timedelta(minutes=-10),
            ),
            ("same_time", datetime(2023, 10, 2, 12, 0), datetime(2023, 10, 1, 12, 0), timedelta(0)),
            (
                "wrap_around_midnight",
                datetime(2023, 10, 1, 0, 10),
                datetime(2023, 10, 1, 23, 50),
                timedelta(minutes=20),
            ),
            (
                "wrap_around_midnight_negative",
                datetime(2023, 10, 1, 23, 50),
                datetime(2023, 10, 5, 0, 10),
                timedelta(minutes=-20),
            ),
            (
                "different_timezones",
                datetime(2023, 10, 1, 10, 0, tzinfo=timezone(timedelta(hours=-4))),
                datetime(2023, 10, 1, 10, 0, tzinfo=timezone(timedelta(hours=9))),
                timedelta(0),
            ),
            ("large_diff", datetime(2023, 10, 1, 18, 0), datetime(2023, 10, 1, 6, 0), timedelta(hours=12)),
            ("more_than_12_hours", datetime(2023, 10, 1, 6, 0), datetime(2023, 10, 1, 18, 0), timedelta(hours=12)),
        ]
    )
    def test_subtract_time(self, name, dt1, dt2, expected):
        result = subtract_relative_time(dt1, dt2)
        self.assertEqual(result, expected)


if __name__ == "__main__":
    unittest.main()
