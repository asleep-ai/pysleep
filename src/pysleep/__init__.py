"""
pysleep
=====

Provides
  1. Definition of the sleep in python ecosystem
  2. Metrics used in medical field
"""

from .hypnogram_report import generate_hypnogram_report
from .label import APNEA, DEEP, HYPOPNEA, LIGHT, NO_EVENT, REM, SNORE, WAKE
from .stat import SleepStat, SleepStatDelta

__version__ = "0.1.5"


__all__ = [
    "APNEA",
    "DEEP",
    "HYPOPNEA",
    "LIGHT",
    "NO_EVENT",
    "REM",
    "SNORE",
    "WAKE",
    "SleepStat",
    "SleepStatDelta",
    "generate_hypnogram_report",
]
