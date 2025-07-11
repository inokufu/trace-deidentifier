from collections.abc import Mapping, MutableSequence
from typing import Any, ClassVar

from src.trace_deidentifier.common.models.trace import Trace
from src.trace_deidentifier.common.utils import utils_dict

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

    AGENT_REPLACEMENTS: ClassVar[dict[str, str]] = {
        field.split(".", 1)[1]: value
        for field, value in FIELDS_TO_REPLACE.items()
        if "actor." in field
    }

    def anonymize(self, trace: Trace) -> None:
        """Inherited from BaseAnonymizationStrategy.anonymize."""
        self._anonymize_part(trace.data)

    def _anonymize_part(self, data: Mapping[str, Any]) -> None:
        """
        Recursively anonymize a part of the trace.

        :param data: Data part to anonymize
        """
        # Handle fixed list of fields directly on the trace
        self._replace_fields(data, self.FIELDS_TO_REPLACE)
        actor = data.get("actor")
        if isinstance(actor, Mapping):
            self._handle_group_members(actor)

        obj = data.get("object")
        if isinstance(obj, Mapping):
            obj_type = obj.get("objectType")
            # Handle object if it's an agent or a group
            # See: https://github.com/adlnet/xAPI-Spec/blob/master/xAPI-Data.md#object-is-agent
            if obj_type in ("Agent", "Group"):
                self._replace_fields(obj, self.AGENT_REPLACEMENTS)
                self._handle_group_members(obj)
            # Recursively handle sub statements
            elif obj_type == "SubStatement":
                self._anonymize_part(obj)

        # Handle authority
        # See: https://github.com/adlnet/xAPI-Spec/blob/master/xAPI-Data.md#249-authority
        authority = data.get("authority")
        if isinstance(authority, Mapping):
            if authority.get("objectType") == "Group":
                self._handle_group_members(authority)
            else:
                self._replace_fields(authority, self.AGENT_REPLACEMENTS)

        # Handle context agents
        # See: https://github.com/adlnet/xAPI-Spec/blob/master/xAPI-Data.md#246-context
        context = data.get("context")
        if isinstance(context, Mapping):
            for field in ("instructor", "team"):
                context_field = context.get(field)
                if isinstance(context_field, Mapping):
                    self._replace_fields(context_field, self.AGENT_REPLACEMENTS)
                    self._handle_group_members(context_field)

    def _handle_group_members(self, data: Mapping[str, Any]) -> None:
        """
        Handle anonymization of group members.

        :param data: Data containing potential group members
        """
        member_attribute = data.get("member")
        if data.get("objectType") == "Group" and isinstance(
            member_attribute,
            MutableSequence,
        ):
            members = (m for m in member_attribute if isinstance(m, Mapping))
            for member in members:
                self._replace_fields(member, self.AGENT_REPLACEMENTS)

    def _replace_fields(
        self,
        target: Mapping[str, Any],
        fields_to_replace: Mapping[str, str],
    ) -> None:
        """
        Replace multiple fields in the target dictionary with their corresponding values.

        :param target: The dictionary in which to replace fields
        :param fields_to_replace: Dictionary mapping field paths to their replacement values
        """
        for field, value in fields_to_replace.items():
            replaced = utils_dict.replace_nested_field(
                data=target,
                keys=field.split("."),
                value=value,
            )
            if replaced:
                self.logger.debug(
                    "Replaced field in trace",
                    {"field": field, "value": value},
                )
