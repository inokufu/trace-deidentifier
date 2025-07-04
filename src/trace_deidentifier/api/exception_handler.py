from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from logger import LogLevel

from src.trace_deidentifier.anonymizer.exceptions import AnonymizationError
from src.trace_deidentifier.common.exceptions import InvalidTraceError


class ExceptionHandler:
    """
    A handler for managing and configuring FastAPI exception handling.

    This class provides a centralized way to handle different types of exceptions
    in a FastAPI application, mapping them to appropriate HTTP status codes and
    providing consistent error response formatting.

    The handler supports both known exceptions (configured via error_mapping)
    and unexpected exceptions through a global handler.
    """

    def __init__(self) -> None:
        """Initialize the exception handler with default error mappings."""
        self.error_mapping: dict[type[Exception], int] = {
            ValueError: status.HTTP_400_BAD_REQUEST,
            TypeError: status.HTTP_500_INTERNAL_SERVER_ERROR,
            InvalidTraceError: status.HTTP_400_BAD_REQUEST,
            AnonymizationError: status.HTTP_500_INTERNAL_SERVER_ERROR,
        }

    def configure(self, app: FastAPI) -> None:
        """
        Configure exception handlers for the FastAPI application.

        :param app: The FastAPI application instance
        """
        # Configure the known_exception_handler for all custom exceptions
        for exception in self.error_mapping:
            app.add_exception_handler(
                exc_class_or_status_code=exception,
                handler=self.known_exception_handler,
            )

        # Add a catch-all handler for any unhandled exceptions
        app.add_exception_handler(
            exc_class_or_status_code=Exception,
            handler=self.global_exception_handler,
        )

    async def known_exception_handler(
        self,
        request: Request,
        exc: Exception,
    ) -> JSONResponse:
        """
        Handle known exceptions and return appropriate JSON responses.

        :param request: The request that caused the exception
        :param exc: The exception that was raised

        :return: A JSON response containing error details
        """
        status_code = self.error_mapping.get(
            type(exc),
            status.HTTP_500_INTERNAL_SERVER_ERROR,
        )

        return JSONResponse(
            status_code=status_code,
            content=self.get_error_detail(
                exc=exc,
                status_code=status_code,
                request=request,
            ),
        )

    async def global_exception_handler(
        self,
        request: Request,
        exc: Exception,
    ) -> JSONResponse:
        """
        Global exception handler for unhandled exceptions.

        :param request: The request that caused the exception
        :param exc: The unhandled exception
        :return: A JSON response indicating an internal server error
        """
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content=self.get_error_detail(
                exc=exc,
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                request=request,
            ),
        )

    @staticmethod
    def get_error_detail(
        exc: Exception,
        status_code: int,
        request: Request,
    ) -> dict[str, str]:
        """
        Generate an error detail dictionary based on the exception, status code, and environment.

        In production, internal server errors are given a generic message.

        :param exc: The exception that was raised
        :param status_code: The HTTP status code associated with the error
        :param request: The request that caused the exception
        :return: A dictionary containing the error detail
        """
        if (
            request.state.config.is_env_production()
            and status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
        ):
            return {"detail": "An internal server error occurred."}

        details = {"detail": str(exc)}
        if exc.__cause__ is not None:
            details["cause"] = str(exc.__cause__)

        request.state.logger.exception(
            "HTTP Error",
            exc,
            {
                "status_code": status_code,
                "details": details
                if request.state.config.get_log_level() == LogLevel.DEBUG
                else None,
            },
        )

        return details
