from typing import ClassVar

from src.trace_deidentifier.common.models.trace import Trace
from src.trace_deidentifier.common.utils.utils_dict import DictUtils

from .base import BaseAnonymizationStrategy


class RemoveFieldsStrategy(BaseAnonymizationStrategy):
    """Strategy to remove non-required fields with sensitive values."""

    EXTENSIONS_TO_REMOVE: ClassVar[set[str]] = {
        "http://id.tincanapi.com/extension/browser-info",
        "http://id.tincanapi.com/extension/ip-address",
        "http://id.tincanapi.com/extension/invitee",
        "http://id.tincanapi.com/extension/observer",
        "http://id.tincanapi.com/extension/referrer",
        "http://id.tincanapi.com/extension/tweet",
        "http://id.tincanapi.com/extension/geojson",
    }

    EXTENSION_PATHS: ClassVar[set[str]] = {
        "context",
        "object.definition",
        "result",
    }

    def anonymize(self, trace: Trace) -> None:
        """Inherited from BaseAnonymizationStrategy.anonymize."""
        for path in self.EXTENSION_PATHS:
            if obj := DictUtils.get_nested_field(data=trace.data, keys=path.split(".")):
                self.logger.debug("Path found in trace", {"path": path})
                extensions = obj.get("extensions")
                if isinstance(extensions, dict) and extensions:
                    self.logger.debug("Extensions found in path", {"path": path})
                    for ext in self.EXTENSIONS_TO_REMOVE:
                        if ext in extensions:
                            self.logger.debug("Remove extension", {"extension": ext})
                            extensions.pop(ext, None)

                    # Delete empty 'extensions' field
                    if not extensions:
                        self.logger.debug(
                            "Remove empty field extensions",
                            {"path": path},
                        )
                        obj.pop("extensions", None)
