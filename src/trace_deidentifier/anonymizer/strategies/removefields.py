from typing import ClassVar

from src.trace_deidentifier.common.models.trace import Trace
from src.trace_deidentifier.common.utils.utils_dict import get_nested_field

from .base import BaseAnonymizationStrategy


class RemoveFieldsStrategy(BaseAnonymizationStrategy):
    """
    Strategy to remove non-required fields with sensitive values.
    """

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
        for path in self.EXTENSION_PATHS:
            if obj := get_nested_field(trace.data, path.split(".")):
                extensions = obj.get("extensions")
                if isinstance(extensions, dict) and extensions:
                    for ext in self.EXTENSIONS_TO_REMOVE:
                        extensions.pop(ext, None)

                    # Delete empty 'extensions' field
                    if not extensions:
                        obj.pop("extensions", None)
