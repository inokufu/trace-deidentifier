import logging
from enum import IntEnum
from typing import Self


class LogLevel(IntEnum):
    """
    Represents the different log levels.
    """

    DEBUG = logging.DEBUG
    INFO = logging.INFO
    WARNING = logging.WARNING
    ERROR = logging.ERROR
    CRITICAL = logging.CRITICAL

    @classmethod
    def from_str(cls, value: str) -> Self:
        """Create a LogLevel from a string, case-insensitive."""
        try:
            return cls[value.upper()]
        except KeyError:
            valid_values = [e.name for e in cls]
            raise ValueError(
                f"Invalid log level '{value}'. Must be one of: {valid_values}",
            )
