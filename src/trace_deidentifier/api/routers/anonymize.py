from fastapi import APIRouter

from src.trace_deidentifier.api.schemas import (
    AnonymizeTraceRequestModel,
    AnonymizeTraceResponseModel,
)

router = APIRouter()


@router.post(
    "/anonymize",
    response_model=AnonymizeTraceResponseModel,
    tags=["Trace anonymization"],
    description="Anonymize an input trace.",
    status_code=200,
)
async def anonymize_trace(
    query: AnonymizeTraceRequestModel,
) -> AnonymizeTraceResponseModel:
    input_trace = query.trace
    # ici on va anonymiser...
    return AnonymizeTraceResponseModel(trace=input_trace)
