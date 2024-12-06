from typing import Any
from unittest.mock import Mock

import pytest

from src.trace_deidentifier.anonymizer.strategies.replace_values import (
    ReplaceSensitiveValuesStrategy,
)
from src.trace_deidentifier.common.models.trace import Trace


class TestReplaceSensitiveValuesStrategy:
    """Test suite for ReplaceSensitiveValuesStrategy class."""

    @pytest.fixture
    def strategy(self, mock_logger: Mock) -> ReplaceSensitiveValuesStrategy:
        """
        Create a ReplaceSensitiveValuesStrategy instance.

        :return: A strategy instance
        """
        strategy = ReplaceSensitiveValuesStrategy()
        strategy.logger = mock_logger
        return strategy

    @pytest.fixture
    def trace_with_sensitive_values(self) -> Trace:
        """
        Create a trace with sensitive values to be replaced.

        :return: A trace with test data
        """
        return Trace.model_construct(
            data={
                "actor": {
                    "name": "John Doe",
                    "mbox": "john@example.com",
                    "mbox_sha1sum": "5d41402abc4b2a76b9719d911017c592",  # sha1 for "hello"
                    "openid": "https://example.com/johndoe",
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
        strategy.anonymize(trace=trace_with_sensitive_values)
        assert trace_with_sensitive_values.data == {
            "actor": {
                "name": "Anonymous",
                "mbox": "mailto:anonymous@anonymous.org",
                "mbox_sha1sum": "84c014de9d5cb87777be0e00a1627798821db5e3",
                "openid": "https://anonymous.org/anonymous",
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
        strategy.anonymize(trace=trace)
        assert trace.data.get("actor") == actor_value

    @pytest.fixture
    def trace_with_group(self) -> Trace:
        """
        Create a trace with group members containing sensitive values to be replaced.

        :return: A trace with test data
        """
        return Trace.model_construct(
            data={
                "actor": {
                    "objectType": "Group",
                    "name": "Group Name",
                    "mbox": "group@example.com",
                    "account": {
                        "name": "groupname",
                        "homePage": "https://example.com",
                    },
                    "member": [
                        {
                            "name": "Member 1",
                            "mbox": "member1@example.com",
                            "account": {
                                "name": "member1",
                                "homePage": "https://example.com",
                            },
                        },
                        {
                            "name": "Member 2",
                            "mbox": "member2@example.com",
                            "openid": "https://example.com/member2",
                        },
                        "invalid member",
                    ],
                },
            },
        )

    def test_should_anonymize_group_and_members(
        self,
        strategy: ReplaceSensitiveValuesStrategy,
        trace_with_group: Trace,
    ) -> None:
        """
        Test that both group and its members are properly anonymized.

        :param strategy: The strategy to test
        :param trace_with_group: A trace containing members sensitive data
        """
        strategy.anonymize(trace=trace_with_group)
        assert trace_with_group.data == {
            "actor": {
                "objectType": "Group",
                "name": "Anonymous",
                "mbox": "mailto:anonymous@anonymous.org",
                "account": {
                    "name": "Anonymous",
                    "homePage": "https://anonymous.org",
                },
                "member": [
                    {
                        "name": "Anonymous",
                        "mbox": "mailto:anonymous@anonymous.org",
                        "account": {
                            "name": "Anonymous",
                            "homePage": "https://anonymous.org",
                        },
                    },
                    {
                        "name": "Anonymous",
                        "mbox": "mailto:anonymous@anonymous.org",
                        "openid": "https://anonymous.org/anonymous",
                    },
                    "invalid member",  # Should remain unchanged
                ],
            },
        }

    @pytest.mark.parametrize(
        "members",
        [
            pytest.param(None, id="null-members"),
            pytest.param([], id="empty-list"),
            pytest.param("not-a-list", id="string-members"),
            pytest.param(123, id="numeric-members"),
            pytest.param(
                [None, "string", 123, {}],
                id="list-with-invalid-items",
            ),
            pytest.param({"key": "value"}, id="dict-instead-of-list"),
        ],
    )
    def test_should_handle_invalid_members(
        self,
        strategy: ReplaceSensitiveValuesStrategy,
        members: Any,
    ) -> None:
        """
        Test handling of invalid member structures in groups.

        :param strategy: The strategy to test
        :param members: Invalid members value to test
        """
        trace = Trace.model_construct(
            data={
                "actor": {
                    "objectType": "Group",
                    "name": "Group Name",
                    "mbox": "group@example.com",
                    "member": members,
                },
            },
        )
        strategy.anonymize(trace=trace)
        assert trace.data == {
            "actor": {
                "objectType": "Group",
                "name": "Anonymous",
                "mbox": "mailto:anonymous@anonymous.org",
                "member": members,
            },
        }

    def test_should_ignore_members_when_not_group(
        self,
        strategy: ReplaceSensitiveValuesStrategy,
    ) -> None:
        """
        Test that members are ignored when actor is not a group.

        :param strategy: The strategy to test
        """
        trace = Trace.model_construct(
            data={
                "actor": {
                    "objectType": "Agent",  # Not a group
                    "name": "John Doe",
                    "mbox": "john@example.com",
                    "member": [  # Should be ignored
                        {
                            "name": "Member 1",
                            "mbox": "member1@example.com",
                        },
                        {
                            "name": "Member 2",
                            "mbox": "member2@example.com",
                        },
                    ],
                },
            },
        )
        strategy.anonymize(trace=trace)
        assert trace.data == {
            "actor": {
                # Actor should be anonymized
                "objectType": "Agent",
                "name": "Anonymous",
                "mbox": "mailto:anonymous@anonymous.org",
                # Members should remain unchanged
                "member": [
                    {
                        "name": "Member 1",
                        "mbox": "member1@example.com",
                    },
                    {
                        "name": "Member 2",
                        "mbox": "member2@example.com",
                    },
                ],
            },
        }
