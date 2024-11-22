from unittest.mock import Mock

import pytest

from src.trace_deidentifier.anonymizer.anonymizer import Anonymizer
from src.trace_deidentifier.anonymizer.exceptions import AnonymizationError
from src.trace_deidentifier.anonymizer.strategies.base import BaseAnonymizationStrategy
from src.trace_deidentifier.common.models.trace import Trace


class TestAnonymizer:
    """Test suite for Anonymizer class."""

    @pytest.fixture
    def mock_strategy(self) -> Mock:
        """
        Create a mock anonymization strategy.

        :return: A mock strategy with anonymize method
        """
        strategy = Mock(spec=BaseAnonymizationStrategy)
        strategy.anonymize = Mock()
        return strategy

    def test_should_require_at_least_one_strategy(self) -> None:
        """Test that initializing without strategies raises ValueError."""
        with pytest.raises(ValueError) as exc_info:
            Anonymizer(strategies=[])
        assert (
            str(exc_info.value)
            == "At least one anonymization strategy must be provided"
        )

    def test_should_apply_all_strategies(self, mock_strategy: Mock) -> None:
        """
        Test that all strategies are applied to the trace.

        :param mock_strategy: Mock strategy fixture
        """
        # Create multiple strategy instances
        strategies = [mock_strategy, Mock(spec=BaseAnonymizationStrategy)]
        anonymizer = Anonymizer(strategies=strategies)

        # Create a trace and anonymize it
        trace = Trace.model_construct(data={"some": "data"})
        anonymizer.anonymize(trace)

        # Verify each strategy was called exactly once with the trace
        for strategy in strategies:
            strategy.anonymize.assert_called_once_with(trace=trace)

    def test_should_continue_on_strategy_error(self, mock_strategy: Mock) -> None:
        """
        Test that anonymization continues even if a strategy fails.

        :param mock_strategy: Mock strategy fixture
        """
        # First strategy will raise an exception
        failing_strategy = Mock(spec=BaseAnonymizationStrategy)
        failing_strategy.anonymize.side_effect = Exception("Strategy failed")

        # Second strategy should still be called
        working_strategy = mock_strategy

        anonymizer = Anonymizer(strategies=[failing_strategy, working_strategy])
        trace = Trace.model_construct(data={"some": "data"})

        # Should raise an Exception
        with pytest.raises(AnonymizationError) as exc_info:
            anonymizer.anonymize(trace)
            assert "Strategy failed" in str(exc_info.value)

        # Verify second strategy was still called
        working_strategy.anonymize.assert_called_once_with(trace=trace)

    @pytest.mark.parametrize(
        "num_strategies,trace_data,expected_calls",
        [
            # Empty trace should still be processed
            pytest.param(1, {}, 1, id="empty-trace"),
            # Single strategy should process once
            pytest.param(1, {"complex": {"nested": "data"}}, 1, id="single-strategy"),
            # Multiple strategies should all process
            pytest.param(3, {"field": "value"}, 3, id="multiple-strategies"),
        ],
    )
    def test_anonymization_scenarios(
        self,
        num_strategies: int,
        trace_data: dict,
        expected_calls: int,
    ) -> None:
        """
        Test various anonymization scenarios.

        :param num_strategies: Number of strategies to create
        :param trace_data: Input trace data
        :param expected_calls: Expected number of strategy calls
        """
        strategies = [
            Mock(spec=BaseAnonymizationStrategy) for _ in range(num_strategies)
        ]

        anonymizer = Anonymizer(strategies=strategies)
        trace = Trace.model_construct(data=trace_data)

        anonymizer.anonymize(trace)

        # Verify each strategy was called the expected number of times
        for strategy in strategies:
            assert strategy.anonymize.call_count == 1
        # Verify total number of strategy calls
        total_calls = sum(strategy.anonymize.call_count for strategy in strategies)
        assert total_calls == expected_calls
