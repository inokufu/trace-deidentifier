from fastapi import APIRouter
from fastapi.params import Depends

from src.trace_deidentifier.anonymizer.anonymizer import Anonymizer
from src.trace_deidentifier.api.dependencies import get_anonymizer
from src.trace_deidentifier.api.schemas import (
    AnonymizeTraceRequestModel,
    AnonymizeTraceResponseModel,
)

router = APIRouter(prefix="/anonymize")


@router.post(
    "",
    tags=["Trace anonymization"],
    description="Anonymize an input trace.",
    status_code=200,
)
async def anonymize_trace(
    query: AnonymizeTraceRequestModel,
    anonymizer: Anonymizer = Depends(get_anonymizer),
) -> AnonymizeTraceResponseModel:
    """
    Anonymize a trace by applying configured anonymization strategies.

    :param query: The request containing the trace to anonymize
    :param anonymizer: The anonymizer instance to use (injected by FastAPI)
    :returns: The response containing the anonymized trace
    :raises AnonymizationError: If the anonymization process fails
    """
    input_trace = query.trace
    anonymizer.anonymize(trace=input_trace)
    return AnonymizeTraceResponseModel(trace=input_trace)
