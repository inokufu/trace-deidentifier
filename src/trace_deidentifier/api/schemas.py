from pydantic import BaseModel, Field

from src.trace_deidentifier.common.models.trace import Trace


class AnonymizeTraceRequestModel(BaseModel):
    """
    Model for trace anonymization request.

    Attributes:
        trace (dict[str, Any]): The input trace data in xAPI format
    """

    trace: Trace = Field(
        description="Input trace data",
    )


class AnonymizeTraceResponseModel(BaseModel):
    """
    Model for trace anonymization response.

    Attributes:
        trace (dict[str, Any]): The output trace data in xAPI format
    """

    trace: Trace = Field(
        description="Anonymized output trace",
    )
