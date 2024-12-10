import json
from unittest.mock import Mock

import pytest
from fastapi import Request, status

from src.trace_deidentifier.api.exception_handler import ExceptionHandler
from src.trace_deidentifier.common.exceptions import InvalidTraceError


@pytest.fixture
def mock_request() -> Request:
    """
    Create a mocked request with config and logger.

    :return: Mocked FastAPI Request object
    """
    request = Mock(spec=Request)
    request.state.config.is_env_production = Mock(return_value=False)
    return request


@pytest.fixture
def handler() -> ExceptionHandler:
    """
    Create an ExceptionHandler instance.

    :return: ExceptionHandler instance
    """
    return ExceptionHandler()


@pytest.mark.asyncio
async def test_known_exception(handler: ExceptionHandler, mock_request: Request) -> None:
    """
    Test formatting of known exceptions.

    :param handler: ExceptionHandler instance
    :param mock_request: Mocked FastAPI request
    """
    error_message = "Known error"
    exc = InvalidTraceError(error_message)

    response = await handler.known_exception_handler(mock_request, exc)

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert json.loads(response.body.decode()) == {"detail": error_message}


@pytest.mark.asyncio
async def test_unknown_exception(handler: ExceptionHandler, mock_request: Request) -> None:
    """
    Test formatting of unknown exceptions.

    :param handler: ExceptionHandler instance
    :param mock_request: Mocked FastAPI request
    """
    error_message = "Unexpected error"
    exc = Exception(error_message)

    response = await handler.global_exception_handler(
        mock_request,
        exc,
    )

    assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
    assert json.loads(response.body.decode()) == {"detail": error_message}


def test_exception_with_cause(handler: ExceptionHandler, mock_request: Request) -> None:
    """
    Test formatting of chained exceptions.

    :param handler: ExceptionHandler instance
    :param mock_request: Mocked FastAPI request
    """
    cause_message = "Original error"
    error_message = "Wrapped error"

    try:
        raise ValueError(cause_message)  # noqa: TRY301
    except ValueError as e:
        try:
            raise TypeError(error_message) from e  # noqa: TRY301
        except TypeError as exc:
            response = handler.get_error_detail(
                exc,
                status.HTTP_500_INTERNAL_SERVER_ERROR,
                mock_request,
            )
            assert response["detail"] == error_message
            assert response["cause"] == cause_message


def test_production_error_message(
    handler: ExceptionHandler,
    mock_request: Request,
) -> None:
    """
    Test error formatting in production environment.

    :param handler: ExceptionHandler instance
    :param mock_request: Mocked FastAPI request
    """
    mock_request.state.config.is_env_production.return_value = True
    sensitive_message = "Sensitive error"
    exc = RuntimeError(sensitive_message)
    response = handler.get_error_detail(
        exc,
        status.HTTP_500_INTERNAL_SERVER_ERROR,
        mock_request,
    )
    assert response["detail"] == "An internal server error occurred."
    assert sensitive_message not in str(response)
