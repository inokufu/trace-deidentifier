from typing import Any
from unittest.mock import Mock

import pytest

from src.trace_deidentifier.anonymizer.strategies.remove_fields import (
    RemoveFieldsStrategy,
)
from src.trace_deidentifier.common.models.trace import Trace
from src.trace_deidentifier.common.types import JsonType


class TestRemoveFieldsStrategy:
    """Test suite for RemoveFieldsStrategy class."""

    @pytest.fixture
    def strategy(self, mock_logger: Mock) -> RemoveFieldsStrategy:
        """
        Create a RemoveFieldsStrategy instance.

        :return: A strategy instance
        """
        strategy = RemoveFieldsStrategy()
        strategy.logger = mock_logger
        return strategy

    @pytest.fixture
    def trace_with_extensions(self) -> Trace:
        """
        Create a trace with various extensions.

        :return: A trace with test data
        """
        return Trace.model_construct(
            data={
                "context": {
                    "extensions": {
                        "http://id.tincanapi.com/extension/browser-info": {
                            "data": "sensitive",
                        },
                        "safe-extension": "keep",
                    },
                },
                "object": {
                    "id": "https://example.com/activity/unique_id",
                    "definition": {
                        "extensions": {
                            "https://id.tincanapi.com/extension/referrer": "http://example.com",
                            "safe-extension": "keep",
                        },
                    },
                },
                "result": {
                    "extensions": {
                        "http://id.tincanapi.com/extensions/ip-address": "12",
                    },
                },
            },
        )

    def test_should_remove_sensitive_extensions(
        self,
        strategy: RemoveFieldsStrategy,
        trace_with_extensions: Trace,
    ) -> None:
        """
        Test that sensitive extensions are removed while preserving safe ones.

        :param strategy: The strategy to test
        :param trace_with_extensions: A trace containing test extensions
        """
        strategy.anonymize(trace=trace_with_extensions)
        assert trace_with_extensions.data == {
            "context": {
                "extensions": {
                    "safe-extension": "keep",
                },
            },
            "object": {
                "id": "https://example.com/activity/unique_id",
                "definition": {
                    "extensions": {
                        "safe-extension": "keep",
                    },
                },
            },
            "result": {
                # Emptied
            },
        }

    @pytest.mark.parametrize(
        "trace_data",
        [
            pytest.param(
                {"context": {}, "object": {"definition": None}},
                id="empty-structure",
            ),
            pytest.param({"context": {}, "result": {}}, id="no-extensions"),
        ],
    )
    def test_should_handle_missing_extensions(
        self,
        strategy: RemoveFieldsStrategy,
        trace_data: JsonType,
    ) -> None:
        """
        Test handling of traces without extensions.

        :param strategy: The strategy to test
        :param trace_data: The test data
        """
        trace = Trace.model_construct(data=trace_data)
        strategy.anonymize(trace=trace)
        assert trace.data == trace_data

    @pytest.mark.parametrize(
        ("extensions", "expected"),
        [
            pytest.param("invalid", "invalid", id="string-extensions"),
            pytest.param(None, None, id="null-extensions"),
            pytest.param([], [], id="list-extensions"),
        ],
    )
    def test_should_handle_invalid_extension_types(
        self,
        strategy: RemoveFieldsStrategy,
        extensions: Any,
        expected: Any,
    ) -> None:
        """
        Test handling of invalid extension types.

        :param strategy: The strategy to test
        :param extensions: Invalid extension value to test
        :param expected: Expected result after anonymization
        """
        trace = Trace.model_construct(data={"context": {"extensions": extensions}})
        strategy.anonymize(trace=trace)
        assert trace.data.get("context").get("extensions") == expected
