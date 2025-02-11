import sys
from collections.abc import Mapping
from typing import Any

from loguru import logger

from .contract import LoggerContract
from .loglevel import LogLevel


class LoguruLogger(LoggerContract):
    """
    Loguru implementation of the logger contract.

    Produces logs in a structured JSON format.
    """

    def __init__(self, level: LogLevel) -> None:
        """Initialize the Loguru logger with default configuration."""
        self._logger = logger
        self._logger.remove()

        self._logger.add(
            sink=sys.stderr,
            level=level,
            format="{time:%Y-%m-%d %H:%M:%S} | <level>{level}</level> | {message}",
            colorize=True,
            backtrace=level == LogLevel.DEBUG,  # Include full stack trace
            diagnose=level == LogLevel.DEBUG,  # Include variables in stack trace
        )

    def _log_with_context(
        self,
        level: LogLevel,
        message: str,
        context: Mapping[str, Any] | None = None,
    ) -> None:
        log_data = {"message": message}
        if context:
            log_data["context"] = context

        self._logger.log(level.name, log_data)

    def debug(self, message: str, context: Mapping[str, Any] | None = None) -> None:
        """Inherited from LoggerContract.debug."""
        self._log_with_context(level=LogLevel.DEBUG, message=message, context=context)

    def info(self, message: str, context: Mapping[str, Any] | None = None) -> None:
        """Inherited from LoggerContract.info."""
        self._log_with_context(level=LogLevel.INFO, message=message, context=context)

    def warning(self, message: str, context: Mapping[str, Any] | None = None) -> None:
        """Inherited from LoggerContract.warning."""
        self._log_with_context(level=LogLevel.WARNING, message=message, context=context)

    def error(self, message: str, context: Mapping[str, Any] | None = None) -> None:
        """Inherited from LoggerContract.error."""
        self._log_with_context(level=LogLevel.ERROR, message=message, context=context)

    def critical(self, message: str, context: Mapping[str, Any] | None = None) -> None:
        """Inherited from LoggerContract.critical."""
        self._log_with_context(
            level=LogLevel.CRITICAL,
            message=message,
            context=context,
        )

    def exception(
        self,
        message: str,
        exc: Exception,
        context: Mapping[str, Any] | None = None,
    ) -> None:
        """Inherited from LoggerContract.exception."""
        exc_context = {
            "exception_type": type(exc).__name__,
            "exception_message": str(exc),
        }
        if context:
            exc_context.update(context)

        self.error(message=message, context=exc_context)
