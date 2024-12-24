from src.trace_deidentifier.common.models.trace import Trace
from src.trace_deidentifier.infrastructure.logging.contract import LoggerContract
from src.trace_deidentifier.infrastructure.logging.loggable_mixin import LoggableMixin

from .exceptions import AnonymizationError
from .strategies.base import BaseAnonymizationStrategy


class Anonymizer(LoggableMixin):
    """Main class responsible for applying anonymization strategies to a trace."""

    def __init__(
        self,
        strategies: list[BaseAnonymizationStrategy],
        logger: LoggerContract,
    ) -> None:
        """
        Initialize the anonymizer with a list of anonymization strategies.

        The anonymizer will apply all provided strategies in sequence when anonymizing traces.

        :param strategies: List of anonymization strategies to apply
        :param logger: LoggerContract instance to use
        :raises ValueError: If no strategies are provided
        """
        if not strategies:
            raise ValueError("At least one anonymization strategy must be provided")
        self.strategies = strategies

        self.logger = logger
        for strategy in self.strategies:
            strategy.logger = self.logger

    def anonymize(self, trace: Trace) -> None:
        """
        Apply all anonymization strategies to a trace.

        :param trace: The trace to anonymize
        :raises AnonymizationError: If any strategy fails to anonymize the trace
        """
        errors = []
        for strategy in self.strategies:
            try:
                self.logger.info(
                    "Apply strategy",
                    {"strategy": type(strategy).__name__},
                )
                strategy.anonymize(trace=trace)
            except Exception as e:
                errors.append(str(e))
                continue

        if errors:
            raise AnonymizationError(f"Failed to anonymize trace: {'; '.join(errors)}")
