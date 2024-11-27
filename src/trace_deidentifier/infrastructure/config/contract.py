from abc import ABC, abstractmethod

from src.trace_deidentifier.infrastructure.logging.loglevel import LogLevel

from .environment import Environment


class ConfigContract(ABC):
    """Abstract base class defining the contract for configuration management."""

    @abstractmethod
    def get_log_level(self) -> LogLevel:
        """
        Get the log level.

        :return: The log level as a string (LogLevel type).
        """
        raise NotImplementedError

    @abstractmethod
    def get_environment(self) -> Environment:
        """
        Get the current environment.

        :return: The current environment as a string (Environment type).
        """
        raise NotImplementedError

    def is_env_production(self) -> bool:
        """
        Check if the current environment is production.

        :return: True if the environment is production, False otherwise.
        """
        return self.get_environment() == Environment.PRODUCTION
