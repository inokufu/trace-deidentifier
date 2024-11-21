from src.trace_deidentifier.anonymizer.exceptions import AnonymizationError
from src.trace_deidentifier.common.models.trace import Trace
from src.trace_deidentifier.common.utils.utils_dict import replace_nested_field
from .base import BaseAnonymizationStrategy


class ReplaceSensitiveValuesStrategy(BaseAnonymizationStrategy):
    """
    Strategy to replace sensitive values with anonymous values.
    """

    FIELDS_TO_REPLACE = {
        "actor.name": "Anonymous",
        "actor.mbox": "mailto:anonymous@anonymous.org",
        "actor.mbox_sha1sum": "84c014de9d5cb87777be0e00a1627798821db5e3",  # sha1 of mailto:anonymous@anonymous.org
        "actor.account.name": "Anonymous",
        "actor.account.homePage": "https://anonymous.org",
    }

    def anonymize(self, trace: Trace) -> None:
        for field, value in self.FIELDS_TO_REPLACE.items():
            try:
                replace_nested_field(trace.data, field.split("."), value)
            except KeyError as e:
                raise AnonymizationError(f"Failed to replace value: {e!s}") from e
