from collections.abc import MutableMapping
from typing import ClassVar

from src.trace_deidentifier.common.models.trace import Trace
from src.trace_deidentifier.common.utils import utils_dict

from .base import BaseAnonymizationStrategy


class RemoveFieldsStrategy(BaseAnonymizationStrategy):
    """Strategy to remove non-required fields with sensitive values."""

    EXTENSIONS_TO_REMOVE: ClassVar[frozenset[str]] = {
        "browser-info",
        "ip-address",
        "invitee",
        "observer",
        "referrer",
        "tweet",
        "geojson",
        "latitude",
        "longitude",
        "location",
        "username",
        "biography",
    }

    EXTENSION_PATHS: ClassVar[frozenset[str]] = {
        "context",
        "object.definition",
        "result",
    }

    def anonymize(self, trace: Trace) -> None:
        """Inherited from BaseAnonymizationStrategy.anonymize."""
        for path in self.EXTENSION_PATHS:
            if obj := utils_dict.get_nested_field(
                data=trace.data,
                keys=path.split("."),
            ):
                self.logger.debug("Path found in trace", {"path": path})
                extensions = obj.get("extensions")
                if isinstance(extensions, MutableMapping) and extensions:
                    self.logger.debug("Extensions found in path", {"path": path})
                    extensions_to_remove = [
                        ext_url
                        for ext_url in extensions
                        if self._should_remove_extension(ext_url)
                    ]
                    for ext in extensions_to_remove:
                        self.logger.debug("Remove extension", {"extension": ext})
                        extensions.pop(ext, None)

                    # Delete empty 'extensions' field
                    if not extensions:
                        self.logger.debug(
                            "Remove empty field extensions",
                            {"path": path},
                        )
                        obj.pop("extensions", None)

    def _should_remove_extension(self, extension_url: str) -> bool:
        """
        Check if an extension URL ends with any of the sensitive extension names.

        :param extension_url: The full extension URL to check
        :return: True if the extension should be removed, False otherwise
        """
        return any(extension_url.endswith(ext) for ext in self.EXTENSIONS_TO_REMOVE)
