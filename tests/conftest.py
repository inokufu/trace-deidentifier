from unittest.mock import Mock

import pytest
from logger import LoggerContract

from src.trace_deidentifier.anonymizer.strategies.base import BaseAnonymizationStrategy


@pytest.fixture
def mock_logger() -> Mock:
    """
    Create a mock logger.

    :return: A mock logger conforming to LoggerContract
    """
    return Mock(spec=LoggerContract)


@pytest.fixture
def mock_strategy(mock_logger: Mock) -> Mock:
    """
    Create a mock anonymization strategy.

    :param mock_logger: Mock logger to use with the strategy
    :return: A mock strategy with anonymize method and logger
    """
    strategy = Mock(spec=BaseAnonymizationStrategy)
    strategy.anonymize = Mock()
    strategy.logger = mock_logger
    return strategy
