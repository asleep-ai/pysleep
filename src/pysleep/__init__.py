"""
pysleep
=====

Provides
  1. Definition of the sleep in python ecosystem
  2. Metrics used in medical field
"""

from .calculator import SleepStageCalculator
from .hypnogram_report import generate_hypnogram_report
from .label import APNEA, DEEP, HYPOPNEA, LIGHT, NO_EVENT, REM, SNORE, WAKE
from .stat import SleepStat, SleepStatDelta

__version__ = "0.2.0"


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
    "SleepStageCalculator",
    "generate_hypnogram_report",
]
