import re
from copy import deepcopy
from typing import Any

import pytest

from src.trace_deidentifier.common.utils import utils_dict


class TestGetNestedField:
    """Test suite for get_nested_field function."""

    @pytest.mark.parametrize(
        ("data", "keys", "expected"),
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
        assert utils_dict.get_nested_field(data=data, keys=keys) == expected


class TestReplaceNestedField:
    """Test suite for replace_nested_field function."""

    @pytest.mark.parametrize(
        ("initial_data", "keys", "new_value", "expected_data", "expected_result"),
        [
            # Basic replacement test - just replace a simple nested value
            pytest.param(
                {"a": {"b": {"c": "old_value"}}},
                ["a", "b", "c"],
                "new_value",
                {"a": {"b": {"c": "new_value"}}},
                True,
                id="basic-replacement",
            ),
            # Should not modify when keys list is empty
            pytest.param(
                {"a": "value"},
                [],
                "new_value",
                {"a": "value"},
                False,
                id="empty-keys",
            ),
            # Should not modify when intermediate key is missing
            pytest.param(
                {"a": {"c": "value"}},
                ["a", "b", "c"],
                "new_value",
                {"a": {"c": "value"}},
                False,
                id="missing-key",
            ),
            # Should not modify when encountering a non-dict value in path
            pytest.param(
                {"a": {"b": "not_a_dict"}},
                ["a", "b", "c"],
                "new_value",
                {"a": {"b": "not_a_dict"}},
                False,
                id="non-dict-value",
            ),
            # Should not add new keys if final key doesn't exist
            pytest.param(
                {"a": {"b": {}}},
                ["a", "b", "c"],
                "new_value",
                {"a": {"b": {}}},
                False,
                id="missing-final-key",
            ),
            # Should handle replacing with a dictionary value
            pytest.param(
                {"a": {"b": {"c": "old"}}},
                ["a", "b"],
                {"c": "new"},
                {"a": {"b": {"c": "new"}}},
                True,
                id="dict-replacement",
            ),
            # Should properly handle None values in the path
            pytest.param(
                {"a": {"b": None}},
                ["a", "b"],
                "new",
                {"a": {"b": "new"}},
                True,
                id="none-replacement",
            ),
            # Test deep nested structure replacement
            pytest.param(
                {"a": {"b": {"c": "old"}}},
                ["a", "b", "c"],
                "new",
                {"a": {"b": {"c": "new"}}},
                True,
                id="deep-replacement",
            ),
            # Test shallow structure replacement
            pytest.param(
                {"a": {"b": "old"}},
                ["a", "b"],
                "new",
                {"a": {"b": "new"}},
                True,
                id="shallow-replacement",
            ),
            # Test with lists
            pytest.param(
                {"a": {"b": [1, 2, 3]}},
                ["a", "b"],
                "new_value",
                {"a": {"b": "new_value"}},
                True,
                id="list-value-replacement",
            ),
            # Test with None
            pytest.param(
                {"a": {"b": {"c": "value"}}},
                ["a", "b", "c"],
                None,
                {"a": {"b": {"c": None}}},
                True,
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
        expected_result: bool,
    ) -> None:
        """
        Test all field replacement scenarios.

        :param initial_data: Initial dictionary state
        :param keys: Path to the field to replace
        :param new_value: New value to set
        :param expected_data: Expected dictionary state after replacement
        """
        before_replaced = deepcopy(initial_data)
        result = utils_dict.replace_nested_field(
            data=initial_data,
            keys=keys,
            value=new_value,
        )

        # Verify the return value matches expected
        assert initial_data == expected_data

        # Verify the return value matches expected
        assert result == expected_result

        # If we expected a replacement, verify the data actually changed
        if result is True:
            assert initial_data != before_replaced
        else:
            assert initial_data == before_replaced


class TestRegexReplace:
    """Test suite for regex_replace function."""

    @pytest.mark.parametrize(
        ("data", "pattern", "replacement", "expected"),
        [
            (
                "Hello test@email.com !",
                re.compile(r"test@email\.com"),
                "anon@anon.com",
                "Hello anon@anon.com !",
            ),
            (
                {"email": "test@email.com", "toto": "tata"},
                re.compile(r"test@email\.com"),
                "anon@anon.com",
                {"email": "anon@anon.com", "toto": "tata"},
            ),
            (
                ["toto", {"nested": "test@email.com"}],
                re.compile(r"test@email\.com"),
                "anon@anon.com",
                ["toto", {"nested": "anon@anon.com"}],
            ),
            (
                [
                    "toto",
                    "test@email.com",
                    {"nested": ["test@email.com"], "tata": "tutu"},
                ],
                re.compile(r"test@email\.com"),
                "anon@anon.com",
                [
                    "toto",
                    "anon@anon.com",
                    {"nested": ["anon@anon.com"], "tata": "tutu"},
                ],
            ),
            (123, re.compile(r"test"), "anon", 123),
        ],
    )
    def test_regex_replace(
        self,
        data: Any,
        pattern: re.Pattern,
        replacement: str,
        expected: Any,
    ) -> None:
        """
        Test regex value replacement in different data structures.

        :param data: Input data structure to process
        :param pattern: Regex pattern to match
        :param replacement: Value to replace matches with
        :param expected: Expected output after replacement
        """
        result = utils_dict.regex_replace(data=data, pattern=pattern, value=replacement)
        assert result == expected
