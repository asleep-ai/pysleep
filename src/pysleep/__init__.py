"""
pysleep
=====

Provides
  1. Definition of the sleep in python ecosystem
  2. Metrics used in medical field
"""

__version__ = "0.1.1"

from .label import APNEA, DEEP, HYPOPNEA, LIGHT, NO_EVENT, REM, SNORE, WAKE
from .stat import SleepStat, SleepStatDelta

__all__ = ["APNEA", "DEEP", "HYPOPNEA", "LIGHT", "NO_EVENT", "REM", "SNORE", "WAKE", "SleepStat", "SleepStatDelta"]
