from pydantic import BaseModel, model_validator
from ralph.models.xapi.base.statements import BaseXapiStatement

from src.trace_deidentifier.common.exceptions import InvalidTraceError
from src.trace_deidentifier.common.types import JsonType


class Trace(BaseModel):
    data: JsonType

    @model_validator(mode="before")
    @classmethod
    def validate_data(cls, values: dict) -> dict:
        input_data = values.get("data")

        if not input_data:
            raise InvalidTraceError("Trace data is required")

        try:
            BaseXapiStatement(**input_data)
        except (ValueError, TypeError) as e:
            raise InvalidTraceError("Invalid xAPI trace") from e

        return values
