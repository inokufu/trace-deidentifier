from .contract import LoggerContract


class LoggableMixin:
    """Mixin to add logging capabilities to a class."""

    def __init__(self) -> None:
        """Initialize the mixin."""
        self._logger: LoggerContract | None = None

    @property
    def logger(self) -> LoggerContract:
        """
        Get the logger instance.

        :return: The configured logger instance
        :raises RuntimeError: If logger has not been set
        """
        if self._logger is None:
            raise RuntimeError("Logger not set")
        return self._logger

    @logger.setter
    def logger(self, logger: LoggerContract) -> None:
        """
        Set a logger.

        :param logger: Logger instance to use
        """
        self._logger = logger
