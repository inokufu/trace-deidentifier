from typing import Any

import pytest

from src.trace_deidentifier.common.utils.utils_dict import (
    get_nested_field,
    replace_nested_field,
)


class TestGetNestedField:
    """Test suite for get_nested_field function."""

    @pytest.mark.parametrize(
        "data,keys,expected",
        [
            pytest.param(
                {"a": {"b": {"c": "value"}}},
                ["a", "b", "c"],
                "value",
                id="deep-nested-value",
            ),
            pytest.param(
                {"a": {"b": {"c": "value"}}},
                ["a", "b"],
                {"c": "value"},
                id="nested-dict",
            ),
            pytest.param(
                {"a": {"b": {"c": "value"}}},
                ["a"],
                {"b": {"c": "value"}},
                id="first-level",
            ),
            pytest.param(
                {"a": {"b": None}},
                ["a", "b", "c"],
                None,
                id="none-value-in-path",
            ),
            pytest.param(
                {"a": {"b": {"c": "value"}}},
                ["x"],
                None,
                id="missing-first-key",
            ),
            pytest.param(
                {"a": {"b": {"c": "value"}}},
                ["a", "x"],
                None,
                id="missing-middle-key",
            ),
            pytest.param(
                {"a": {"b": {"c": "value"}}},
                ["a", "b", "x"],
                None,
                id="missing-last-key",
            ),
            pytest.param(
                {},
                ["any"],
                None,
                id="empty-dict",
            ),
            pytest.param(
                {"a": {"b": "not-a-dict"}},
                ["a", "b", "c"],
                None,
                id="non-dict-in-path",
            ),
        ],
    )
    def test_get_nested_field(
        self,
        data: dict[str, Any],
        keys: list[str],
        expected: Any,
    ) -> None:
        """
        Test getting nested field values for various scenarios.

        :param data: Input dictionary
        :param keys: Path to the nested field
        :param expected: Expected value
        """
        assert get_nested_field(data, keys) == expected


class TestReplaceNestedField:
    """Test suite for replace_nested_field function."""

    @pytest.mark.parametrize(
        "initial_data,keys,new_value,expected_data",
        [
            # Basic replacement test - just replace a simple nested value
            pytest.param(
                {"a": {"b": {"c": "old_value"}}},
                ["a", "b", "c"],
                "new_value",
                {"a": {"b": {"c": "new_value"}}},
                id="basic-replacement",
            ),
            # Should not modify when keys list is empty
            pytest.param(
                {"a": "value"},
                [],
                "new_value",
                {"a": "value"},
                id="empty-keys",
            ),
            # Should not modify when intermediate key is missing
            pytest.param(
                {"a": {"c": "value"}},
                ["a", "b", "c"],
                "new_value",
                {"a": {"c": "value"}},
                id="missing-key",
            ),
            # Should not modify when encountering a non-dict value in path
            pytest.param(
                {"a": {"b": "not_a_dict"}},
                ["a", "b", "c"],
                "new_value",
                {"a": {"b": "not_a_dict"}},
                id="non-dict-value",
            ),
            # Should not add new keys if final key doesn't exist
            pytest.param(
                {"a": {"b": {}}},
                ["a", "b", "c"],
                "new_value",
                {"a": {"b": {}}},
                id="missing-final-key",
            ),
            # Should handle replacing with a dictionary value
            pytest.param(
                {"a": {"b": {"c": "old"}}},
                ["a", "b"],
                {"c": "new"},
                {"a": {"b": {"c": "new"}}},
                id="dict-replacement",
            ),
            # Should properly handle None values in the path
            pytest.param(
                {"a": {"b": None}},
                ["a", "b"],
                "new",
                {"a": {"b": "new"}},
                id="none-replacement",
            ),
            # Test deep nested structure replacement
            pytest.param(
                {"a": {"b": {"c": "old"}}},
                ["a", "b", "c"],
                "new",
                {"a": {"b": {"c": "new"}}},
                id="deep-replacement",
            ),
            # Test shallow structure replacement
            pytest.param(
                {"a": {"b": "old"}},
                ["a", "b"],
                "new",
                {"a": {"b": "new"}},
                id="shallow-replacement",
            ),
            # Test with lists
            pytest.param(
                {"a": {"b": [1, 2, 3]}},
                ["a", "b"],
                "new_value",
                {"a": {"b": "new_value"}},
                id="list-value-replacement",
            ),
            # Test with None
            pytest.param(
                {"a": {"b": {"c": "value"}}},
                ["a", "b", "c"],
                None,
                {"a": {"b": {"c": None}}},
                id="None-value",
            ),
        ],
    )
    def test_replace_field_cases(
        self,
        initial_data: dict[str, Any],
        keys: list[str],
        new_value: Any,
        expected_data: dict[str, Any],
    ) -> None:
        """
        Test all field replacement scenarios.

        :param initial_data: Initial dictionary state
        :param keys: Path to the field to replace
        :param new_value: New value to set
        :param expected_data: Expected dictionary state after replacement
        """
        replace_nested_field(initial_data, keys, new_value)
        assert initial_data == expected_data
