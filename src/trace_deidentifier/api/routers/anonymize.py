import json
from collections.abc import AsyncGenerator

import ijson
from fastapi import APIRouter, Request, UploadFile
from fastapi.params import Depends
from fastapi.responses import StreamingResponse

from src.trace_deidentifier.anonymizer.anonymizer import Anonymizer
from src.trace_deidentifier.api.dependencies import get_anonymizer
from src.trace_deidentifier.api.schemas import (
    AnonymizeTraceRequestModel,
    AnonymizeTraceResponseModel,
)
from src.trace_deidentifier.common.jsonencoder import CustomJSONEncoder
from src.trace_deidentifier.common.models.trace import Trace

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


@router.post(
    "/file",
    tags=["Trace anonymization"],
    description="Anonymize traces from a JSON file.",
    status_code=200,
)
async def anonymize_traces_file(
    request: Request,
    file: UploadFile,
    anonymizer: Anonymizer = Depends(get_anonymizer),
) -> StreamingResponse:
    """
    Anonymize multiple traces from a JSON file by applying configured anonymization strategies.

    :param request: The current HTTP request
    :param file: Uploaded JSON file containing an array of traces
    :param anonymizer: The anonymizer instance to use (injected by FastAPI)
    :returns: The response containing the anonymized traces
    """

    async def generate_anonymized_traces() -> AsyncGenerator[str, None]:
        try:
            parser = ijson.items(file.file, "item")
        except ijson.JSONError as e:
            request.state.logger.exception("Invalid JSON format", e)
            yield json.dumps({"error": f"Invalid JSON format: {e!s}"}) + "\n"
            return

        for index, statement in enumerate(parser):
            try:
                trace = Trace(data=statement)
                anonymizer.anonymize(trace=trace)
                yield json.dumps(trace.data, cls=CustomJSONEncoder) + "\n"
            except Exception as e:
                request.state.logger.exception(
                    "Failed to anonymize trace",
                    e,
                    {"index": index},
                )
                yield (json.dumps({"error": f"Trace at index {index}: {e!s}"}) + "\n")

    return StreamingResponse(
        content=generate_anonymized_traces(),
        media_type="application/x-ndjson",
    )
