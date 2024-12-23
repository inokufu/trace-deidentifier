from typing import ClassVar

from src.trace_deidentifier.common.models.trace import Trace
from src.trace_deidentifier.common.utils.utils_dict import DictUtils

from .base import BaseAnonymizationStrategy


class ReplaceSensitiveValuesStrategy(BaseAnonymizationStrategy):
    """Strategy to replace sensitive values with anonymous values."""

    FIELDS_TO_REPLACE: ClassVar[dict[str, str]] = {
        "actor.name": "Anonymous",
        "actor.mbox": "mailto:anonymous@anonymous.org",
        "actor.mbox_sha1sum": "84c014de9d5cb87777be0e00a1627798821db5e3",  # sha1 of mailto:anonymous@anonymous.org
        "actor.openid": "https://anonymous.org/anonymous",
        "actor.account.name": "Anonymous",
        "actor.account.homePage": "https://anonymous.org",
    }

    def anonymize(self, trace: Trace) -> None:
        """Inherited from BaseAnonymizationStrategy.anonymize."""
        self._replace_fields(trace.data, self.FIELDS_TO_REPLACE)

        # Handle group members if present
        actor = trace.data.get("actor", {})
        if isinstance(actor, dict):
            member_attribute = actor.get("member", [])
            if actor.get("objectType") == "Group" and isinstance(
                member_attribute,
                list,
            ):
                members = (m for m in member_attribute if isinstance(m, dict))
                actor_fields = {
                    field.split(".", 1)[1]: value
                    for field, value in self.FIELDS_TO_REPLACE.items()
                    if "actor." in field
                }
                for member in members:
                    self._replace_fields(member, actor_fields)

    def _replace_fields(self, target: dict, fields_to_replace: dict[str, str]) -> None:
        """
        Replace multiple fields in the target dictionary with their corresponding values.

        :param target: The dictionary in which to replace fields
        :param fields_to_replace: Dictionary mapping field paths to their replacement values
        """
        for field, value in fields_to_replace.items():
            replaced = DictUtils.replace_nested_field(
                data=target,
                keys=field.split("."),
                value=value,
            )
            if replaced:
                self.logger.debug(
                    "Replaced field in trace",
                    {"field": field, "value": value},
                )
