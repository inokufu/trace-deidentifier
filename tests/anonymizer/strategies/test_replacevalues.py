from typing import Any

import pytest

from src.trace_deidentifier.anonymizer.strategies.replacevalues import (
    ReplaceSensitiveValuesStrategy,
)
from src.trace_deidentifier.common.models.trace import Trace


class TestReplaceSensitiveValuesStrategy:
    @pytest.fixture
    def strategy(self) -> ReplaceSensitiveValuesStrategy:
        """
        Create a ReplaceSensitiveValuesStrategy instance.

        :return: A strategy instance
        :rtype: ReplaceSensitiveValuesStrategy
        """
        return ReplaceSensitiveValuesStrategy()

    @pytest.fixture
    def trace_with_sensitive_values(self) -> Trace:
        """
        Create a trace with sensitive values to be replaced.

        :return: A trace with test data
        :rtype: Trace
        """
        return Trace.model_construct(
            data={
                "actor": {
                    "name": "John Doe",
                    "mbox": "john@example.com",
                    "mbox_sha1sum": "5d41402abc4b2a76b9719d911017c592",  # sha1 for "hello"
                    "account": {
                        "name": "johndoe",
                        "homePage": "https://example.com",
                    },
                    "other": "value",
                },
                "verb": {
                    "id": "http://example.com/verbs/completed",
                },
            },
        )

    def test_should_replace_sensitive_values(
        self,
        strategy: ReplaceSensitiveValuesStrategy,
        trace_with_sensitive_values: Trace,
    ) -> None:
        """
        Test that sensitive values are properly replaced with anonymous values.

        :param strategy: The strategy to test
        :param trace_with_sensitive_values: A trace containing sensitive data
        """
        strategy.anonymize(trace_with_sensitive_values)
        assert trace_with_sensitive_values.data == {
            "actor": {
                "name": "Anonymous",
                "mbox": "mailto:anonymous@anonymous.org",
                "mbox_sha1sum": "84c014de9d5cb87777be0e00a1627798821db5e3",
                "account": {
                    "name": "Anonymous",
                    "homePage": "https://anonymous.org",
                },
                "other": "value",
            },
            "verb": {
                "id": "http://example.com/verbs/completed",
            },
        }

    @pytest.mark.parametrize(
        "actor_value",
        [
            pytest.param({}, id="empty-actor"),
            pytest.param(None, id="null-actor"),
            pytest.param("invalid", id="string-actor"),
            pytest.param(123, id="numeric-actor"),
        ],
    )
    def test_should_handle_invalid_actor_types(
        self,
        strategy: ReplaceSensitiveValuesStrategy,
        actor_value: Any,
    ) -> None:
        """
        Test handling of invalid actor types.

        :param strategy: The strategy to test
        :param actor_value: Invalid actor value to test
        """
        trace = Trace.model_construct(data={"actor": actor_value})
        strategy.anonymize(trace)
        assert trace.data.get("actor") == actor_value
