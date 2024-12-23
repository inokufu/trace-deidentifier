import re
from abc import ABC

from src.trace_deidentifier.common.models.trace import Trace
from src.trace_deidentifier.common.utils.utils_dict import DictUtils

from .base import BaseAnonymizationStrategy


class RegexDetectionStrategy(BaseAnonymizationStrategy, ABC):
    """Base class for strategies that replace values in a trace using regex patterns."""

    def __init__(self, pattern: str, replacement: str) -> None:
        """
        Initialize the strategy with a regex pattern and a replacement value.

        :param pattern: Regex pattern to match
        :param replacement: Replacement value for matching patterns
        """
        super().__init__()
        self.pattern = re.compile(pattern=pattern)
        self.replacement = replacement

    def anonymize(self, trace: Trace) -> None:
        """Inherited from BaseAnonymizationStrategy.anonymize."""
        self.logger.debug(
            "Apply regex replacement",
            {"pattern": self.pattern, "replacement": self.replacement},
        )

        DictUtils.regex_replace(
            data=trace.data,
            pattern=self.pattern,
            value=self.replacement,
        )
