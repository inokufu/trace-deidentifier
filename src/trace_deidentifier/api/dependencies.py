from fastapi import Request

from src.trace_deidentifier.anonymizer.anonymizer import Anonymizer
from src.trace_deidentifier.anonymizer.strategies.removefields import (
    RemoveFieldsStrategy,
)
from src.trace_deidentifier.anonymizer.strategies.replacevalues import (
    ReplaceSensitiveValuesStrategy,
)


async def get_anonymizer(request: Request) -> Anonymizer:
    """
    FastAPI dependency to get a configured Anonymizer instance.

    :param request: The FastAPI request object
    :returns: A configured Anonymizer instance with all required strategies
    """
    return Anonymizer(
        strategies=[
            ReplaceSensitiveValuesStrategy(),
            RemoveFieldsStrategy(),
        ],
    )
