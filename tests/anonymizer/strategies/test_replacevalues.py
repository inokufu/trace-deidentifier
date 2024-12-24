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

    def test_should_replace_object_agent(
        self,
        strategy: ReplaceSensitiveValuesStrategy,
    ) -> None:
        """
        Test that sensitives values are replaced in trace object when it's an agent.

        :param strategy: The strategy to test
        """
        trace = Trace.model_construct(
            data={
                "object": {
                    "name": "Andrew Downes",
                    "mbox": "mailto:andrew@example.co.uk",
                    "objectType": "Agent",
                },
            },
        )
        strategy.anonymize(trace=trace)
        assert trace.data == {
            "object": {
                "name": "Anonymous",
                "mbox": "mailto:anonymous@anonymous.org",
                "objectType": "Agent",
            },
        }

    def test_should_replace_object_group(
        self,
        strategy: ReplaceSensitiveValuesStrategy,
    ) -> None:
        """
        Test that sensitives values are replaced in trace object when it's a group.

        :param strategy: The strategy to test
        """
        trace = Trace.model_construct(
            data={
                "object": {
                    "name": "Example Group",
                    "account": {
                        "homePage": "http://example.com/homePage",
                        "name": "GroupAccount",
                    },
                    "objectType": "Group",
                    "member": [
                        {
                            "name": "Andrew Downes",
                            "mbox": "mailto:andrew@example.com",
                            "objectType": "Agent",
                        },
                        {
                            "name": "Aaron Silvers",
                            "openid": "http://aaron.openid.example.org",
                            "objectType": "Agent",
                        },
                    ],
                },
            },
        )
        strategy.anonymize(trace=trace)
        assert trace.data == {
            "object": {
                "name": "Anonymous",
                "account": {
                    "homePage": "https://anonymous.org",
                    "name": "Anonymous",
                },
                "objectType": "Group",
                "member": [
                    {
                        "name": "Anonymous",
                        "mbox": "mailto:anonymous@anonymous.org",
                        "objectType": "Agent",
                    },
                    {
                        "name": "Anonymous",
                        "openid": "https://anonymous.org/anonymous",
                        "objectType": "Agent",
                    },
                ],
            },
        }

    def test_should_replace_substatement(
        self,
        strategy: ReplaceSensitiveValuesStrategy,
    ) -> None:
        """
        Test that sensitives values are recursively replaced in trace substatements.

        :param strategy: The strategy to test
        """
        trace = Trace.model_construct(
            data={
                "object": {
                    "objectType": "SubStatement",
                    "actor": {
                        "objectType": "Agent",
                        "mbox": "mailto:agent@example.com",
                    },
                    "verb": {
                        "id": "http://example.com/confirmed",
                        "display": {"en": "confirmed"},
                    },
                    "object": {
                        "objectType": "SubStatement",
                        "actor": {
                            "objectType": "Agent",
                            "mbox": "mailto:agent@example.com",
                        },
                        "object": {
                            "objectType": "StatementRef",
                            "id": "9e13cefd-53d3-4eac-b5ed-2cf6693903bb",
                        },
                    },
                },
            },
        )
        strategy.anonymize(trace=trace)
        assert trace.data == {
            "object": {
                "objectType": "SubStatement",
                "actor": {
                    "objectType": "Agent",
                    "mbox": "mailto:anonymous@anonymous.org",
                },
                "verb": {
                    "id": "http://example.com/confirmed",
                    "display": {"en": "confirmed"},
                },
                "object": {
                    "objectType": "SubStatement",
                    "actor": {
                        "objectType": "Agent",
                        "mbox": "mailto:anonymous@anonymous.org",
                    },
                    "object": {
                        "objectType": "StatementRef",
                        "id": "9e13cefd-53d3-4eac-b5ed-2cf6693903bb",
                    },
                },
            },
        }

    def test_should_replace_authority(
        self,
        strategy: ReplaceSensitiveValuesStrategy,
    ) -> None:
        """
        Test that sensitives values are replaced in trace authority.

        :param strategy: The strategy to test
        """
        trace = Trace.model_construct(
            data={
                "authority": {
                    "objectType": "Group",
                    "member": [
                        {
                            "account": {
                                "homePage": "http://example.com/xAPI/OAuth/Token",
                                "name": "oauth_consumer_x75db",
                            },
                        },
                        {"mbox": "mailto:bob@example.com"},
                    ],
                },
            },
        )
        strategy.anonymize(trace=trace)
        assert trace.data == {
            "authority": {
                "objectType": "Group",
                "member": [
                    {
                        "account": {
                            "homePage": "https://anonymous.org",
                            "name": "Anonymous",
                        },
                    },
                    {"mbox": "mailto:anonymous@anonymous.org"},
                ],
            },
        }

    def test_should_replace_context(
        self,
        strategy: ReplaceSensitiveValuesStrategy,
    ) -> None:
        """
        Test that sensitives values are replaced in trace context.

        :param strategy: The strategy to test
        """
        trace = Trace.model_construct(
            data={
                "context": {
                    "instructor": {
                        "name": "Andrew Downes",
                        "account": {
                            "homePage": "http://www.example.com",
                            "name": "13936749",
                        },
                        "objectType": "Agent",
                    },
                    "team": {
                        "name": "Team PB",
                        "objectType": "Group",
                        "member": [
                            {
                                "name": "Andrew Downes",
                                "account": {
                                    "homePage": "http://www.example.com",
                                    "name": "13936749",
                                },
                                "objectType": "Agent",
                            },
                        ],
                    },
                },
            },
        )
        strategy.anonymize(trace=trace)
        assert trace.data == {
            "context": {
                "instructor": {
                    "name": "Anonymous",
                    "account": {
                        "homePage": "https://anonymous.org",
                        "name": "Anonymous",
                    },
                    "objectType": "Agent",
                },
                "team": {
                    "name": "Anonymous",
                    "objectType": "Group",
                    "member": [
                        {
                            "name": "Anonymous",
                            "account": {
                                "homePage": "https://anonymous.org",
                                "name": "Anonymous",
                            },
                            "objectType": "Agent",
                        },
                    ],
                },
            },
        }

    def test_complete_trace(
        self,
        strategy: ReplaceSensitiveValuesStrategy,
    ) -> None:
        """
        Test that sensitives values are replaced in a complete trace.

        :param strategy: The strategy to test
        """
        trace = Trace.model_construct(
            data={
                "id": "6690e6c9-3ef0-4ed3-8b37-7f3964730bee",
                "actor": {
                    "name": "Team PB",
                    "mbox": "mailto:teampb@example.com",
                    "member": [
                        {
                            "name": "Andrew Downes",
                            "account": {
                                "homePage": "http://www.example.com",
                                "name": "13936749",
                            },
                            "objectType": "Agent",
                        },
                        {
                            "name": "Toby Nichols",
                            "openid": "http://toby.openid.example.org/",
                            "objectType": "Agent",
                        },
                        {
                            "name": "Ena Hills",
                            "mbox_sha1sum": "ebd31e95054c018b10727ccffd2ef2ec3a016ee9",
                            "objectType": "Agent",
                        },
                    ],
                    "objectType": "Group",
                },
                "verb": {
                    "id": "http://adlnet.gov/expapi/verbs/attended",
                    "display": {"en-GB": "attended", "en-US": "attended"},
                },
                "result": {
                    "extensions": {
                        "http://example.com/profiles/meetings/resultextensions/minuteslocation": "X:\\meetings\\minutes\\examplemeeting.one",
                    },
                    "success": True,
                    "completion": True,
                    "response": "We agreed on some example actions.",
                    "duration": "PT1H0M0S",
                },
                "context": {
                    "registration": "ec531277-b57b-4c15-8d91-d292c5b2b8f7",
                    "contextActivities": {
                        "parent": [
                            {
                                "id": "http://www.example.com/meetings/series/267",
                                "objectType": "Activity",
                            },
                        ],
                        "category": [
                            {
                                "id": "http://www.example.com/meetings/categories/teammeeting",
                                "objectType": "Activity",
                                "definition": {
                                    "name": {"en": "team meeting"},
                                    "description": {
                                        "en": "A category of meeting used for regular team meetings.",
                                    },
                                    "type": "http://example.com/expapi/activities/meetingcategory",
                                },
                            },
                        ],
                        "other": [
                            {
                                "id": "http://www.example.com/meetings/occurances/34257",
                                "objectType": "Activity",
                            },
                            {
                                "id": "http://www.example.com/meetings/occurances/3425567",
                                "objectType": "Activity",
                            },
                        ],
                    },
                    "instructor": {
                        "name": "Andrew Downes",
                        "account": {
                            "homePage": "http://www.example.com",
                            "name": "13936749",
                        },
                        "objectType": "Agent",
                    },
                    "team": {
                        "name": "Team PB",
                        "objectType": "Group",
                        "member": [
                            {
                                "name": "Andrew Downes",
                                "account": {
                                    "homePage": "http://www.example.com",
                                    "name": "13936749",
                                },
                                "objectType": "Agent",
                            },
                        ],
                    },
                    "platform": "Example virtual meeting software",
                    "language": "tlh",
                    "statement": {
                        "objectType": "StatementRef",
                        "id": "6690e6c9-3ef0-4ed3-8b37-7f3964730bee",
                    },
                },
                "timestamp": "2013-05-18T05:32:34.804+00:00",
                "stored": "2013-05-18T05:32:34.804+00:00",
                "authority": {
                    "account": {
                        "homePage": "http://cloud.scorm.com/",
                        "name": "anonymous",
                    },
                    "objectType": "Agent",
                },
                "version": "1.0.0",
                "object": {
                    "id": "http://www.example.com/meetings/occurances/34534",
                    "definition": {
                        "extensions": {
                            "http://example.com/profiles/meetings/activitydefinitionextensions/room": {
                                "name": "Kilby",
                                "id": "http://example.com/rooms/342",
                            },
                        },
                        "name": {
                            "en-GB": "example meeting",
                            "en-US": "example meeting",
                        },
                        "description": {
                            "en-GB": "An example meeting that happened on a specific occasion with certain people present.",
                            "en-US": "An example meeting that happened on a specific occasion with certain people present.",
                        },
                        "type": "http://adlnet.gov/expapi/activities/meeting",
                        "moreInfo": "http://virtualmeeting.example.com/345256",
                    },
                    "objectType": "Activity",
                },
            },
        )

        strategy.anonymize(trace=trace)
        assert trace.data == {
            "id": "6690e6c9-3ef0-4ed3-8b37-7f3964730bee",
            "actor": {
                "name": "Anonymous",
                "mbox": "mailto:anonymous@anonymous.org",
                "member": [
                    {
                        "name": "Anonymous",
                        "account": {
                            "homePage": "https://anonymous.org",
                            "name": "Anonymous",
                        },
                        "objectType": "Agent",
                    },
                    {
                        "name": "Anonymous",
                        "openid": "https://anonymous.org/anonymous",
                        "objectType": "Agent",
                    },
                    {
                        "name": "Anonymous",
                        "mbox_sha1sum": "84c014de9d5cb87777be0e00a1627798821db5e3",
                        "objectType": "Agent",
                    },
                ],
                "objectType": "Group",
            },
            "verb": {
                "id": "http://adlnet.gov/expapi/verbs/attended",
                "display": {"en-GB": "attended", "en-US": "attended"},
            },
            "result": {
                "extensions": {
                    "http://example.com/profiles/meetings/resultextensions/minuteslocation": "X:\\meetings\\minutes\\examplemeeting.one",
                },
                "success": True,
                "completion": True,
                "response": "We agreed on some example actions.",
                "duration": "PT1H0M0S",
            },
            "context": {
                "registration": "ec531277-b57b-4c15-8d91-d292c5b2b8f7",
                "contextActivities": {
                    "parent": [
                        {
                            "id": "http://www.example.com/meetings/series/267",
                            "objectType": "Activity",
                        },
                    ],
                    "category": [
                        {
                            "id": "http://www.example.com/meetings/categories/teammeeting",
                            "objectType": "Activity",
                            "definition": {
                                "name": {"en": "team meeting"},
                                "description": {
                                    "en": "A category of meeting used for regular team meetings.",
                                },
                                "type": "http://example.com/expapi/activities/meetingcategory",
                            },
                        },
                    ],
                    "other": [
                        {
                            "id": "http://www.example.com/meetings/occurances/34257",
                            "objectType": "Activity",
                        },
                        {
                            "id": "http://www.example.com/meetings/occurances/3425567",
                            "objectType": "Activity",
                        },
                    ],
                },
                "instructor": {
                    "name": "Anonymous",
                    "account": {
                        "homePage": "https://anonymous.org",
                        "name": "Anonymous",
                    },
                    "objectType": "Agent",
                },
                "team": {
                    "name": "Anonymous",
                    "objectType": "Group",
                    "member": [
                        {
                            "name": "Anonymous",
                            "account": {
                                "homePage": "https://anonymous.org",
                                "name": "Anonymous",
                            },
                            "objectType": "Agent",
                        },
                    ],
                },
                "platform": "Example virtual meeting software",
                "language": "tlh",
                "statement": {
                    "objectType": "StatementRef",
                    "id": "6690e6c9-3ef0-4ed3-8b37-7f3964730bee",
                },
            },
            "timestamp": "2013-05-18T05:32:34.804+00:00",
            "stored": "2013-05-18T05:32:34.804+00:00",
            "authority": {
                "account": {"homePage": "https://anonymous.org", "name": "Anonymous"},
                "objectType": "Agent",
            },
            "version": "1.0.0",
            "object": {
                "id": "http://www.example.com/meetings/occurances/34534",
                "definition": {
                    "extensions": {
                        "http://example.com/profiles/meetings/activitydefinitionextensions/room": {
                            "name": "Kilby",
                            "id": "http://example.com/rooms/342",
                        },
                    },
                    "name": {"en-GB": "example meeting", "en-US": "example meeting"},
                    "description": {
                        "en-GB": "An example meeting that happened on a specific occasion with certain people present.",
                        "en-US": "An example meeting that happened on a specific occasion with certain people present.",
                    },
                    "type": "http://adlnet.gov/expapi/activities/meeting",
                    "moreInfo": "http://virtualmeeting.example.com/345256",
                },
                "objectType": "Activity",
            },
        }
