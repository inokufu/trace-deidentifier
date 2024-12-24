from abc import ABC, abstractmethod

from src.trace_deidentifier.common.models.trace import Trace
from src.trace_deidentifier.infrastructure.logging.loggable_mixin import LoggableMixin


class BaseAnonymizationStrategy(ABC, LoggableMixin):
    """Abstract base class for anonymization strategies."""

    @abstractmethod
    def anonymize(self, trace: Trace) -> None:
        """
        Anonymize a given trace according to the strategy's rules.

        :param trace: The trace to anonymize
        """
        raise NotImplementedError
