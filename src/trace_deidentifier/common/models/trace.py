from pydantic import BaseModel, model_validator
from ralph.models.xapi.base.statements import BaseXapiStatement

from src.trace_deidentifier.common.exceptions import InvalidTraceError
from src.trace_deidentifier.common.types import JsonType


class Trace(BaseModel):
    """
    Represents a trace containing xAPI data.

    :param data: The xAPI statement data
    :type data: BaseXapiStatement
    """

    data: JsonType

    @model_validator(mode="before")
    @classmethod
    def validate_data(cls, values: dict) -> dict:
        """
        Validate that data is present and follows xAPI format.

        :param values: Dictionary of field values
        :returns: Validated values
        :raises InvalidTraceError: If data is missing or invalid xAPI format
        """
        input_data = values.get("data")

        if not input_data:
            raise InvalidTraceError("Trace data is required")

        try:
            BaseXapiStatement.model_validate(input_data)
        except (ValueError, TypeError) as e:
            raise InvalidTraceError("Invalid xAPI trace") from e

        return values
