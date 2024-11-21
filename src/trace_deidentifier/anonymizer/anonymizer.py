from src.trace_deidentifier.common.models.trace import Trace

from .exceptions import AnonymizationError
from .strategies.base import BaseAnonymizationStrategy


class Anonymizer:
    """
    Main class responsible for applying anonymization strategies to a trace.
    """

    def __init__(self, strategies: list[BaseAnonymizationStrategy]) -> None:
        """
        :param strategies: List of anonymization strategies to apply
        :raises ValueError: If no strategies are provided
        """
        if not strategies:
            raise ValueError("At least one anonymization strategy must be provided")
        self.strategies = strategies

    def anonymize(self, trace: Trace) -> None:
        """
        Apply all anonymization strategies to a trace.

        :param trace: The trace to anonymize
        :raises AnonymizationError: If any strategy fails to anonymize the trace
        """
        for strategy in self.strategies:
            try:
                strategy.anonymize(trace=trace)
            except Exception as e:
                raise AnonymizationError(f"Failed to anonymize trace: {e!s}") from e
