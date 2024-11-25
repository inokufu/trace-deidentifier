from typing import Any


class DictUtils:
    """Utility class for handling nested dictionary and list operations."""

    @staticmethod
    def get_nested_field(
        data: dict[str, Any], keys: list[str]
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
