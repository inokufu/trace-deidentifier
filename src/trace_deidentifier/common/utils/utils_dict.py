import re
from typing import Any


class DictUtils:
    """Utility class for handling nested dictionary and list operations."""

    @staticmethod
    def get_nested_field(
        data: dict[str, Any],
        keys: list[str],
    ) -> dict[str, Any] | None:
        """
        Get a nested dictionary field based on a path of keys.

        :param data: The dictionary to traverse
        :param keys: A list of keys to navigate the nested structure
        :return: The nested dictionary or None if not found
        """
        for key in keys:
            if isinstance(data, dict) and key in data:
                data = data[key]
            else:
                return None
        return data

    @staticmethod
    def replace_nested_field(data: dict[str, Any], keys: list[str], value: Any) -> None:
        """
        Recursively navigate through nested dictionaries to replace a field.

        :param data: The dictionary to modify
        :param keys: List of keys representing the path to the field
        :param value: The value to set at the specified field
        """
        if not keys:  # In case keys list is empty
            return
        key = keys[0]
        if len(keys) == 1:
            if key in data:
                data[key] = value
        elif key in data and isinstance(data[key], dict):
            DictUtils.replace_nested_field(data[key], keys[1:], value)

    @staticmethod
    def regex_replace(data: Any, pattern: re.Pattern, value: Any):
        """
        Recursively replace a value, which can be a string, dict, or list.

        :param data: Input data (str, dict, or list) to process
        :param pattern: Compiled regex pattern to search for
        :param value: Replacement string
        :return: The modified data with replacements applied
        """
        if isinstance(data, str):
            # Apply regex replacement directly
            return pattern.sub(repl=value, string=data)

        if isinstance(data, dict):
            # Replace each value in the dictionary
            for key in data:
                data[key] = DictUtils.regex_replace(
                    data=data[key],
                    pattern=pattern,
                    value=value,
                )

        elif isinstance(data, list):
            # Replace each element in the list
            for i in range(len(data)):
                data[i] = DictUtils.regex_replace(
                    data=data[i],
                    pattern=pattern,
                    value=value,
                )

        return data
