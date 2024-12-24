from fastapi import Request

from src.trace_deidentifier.anonymizer.anonymizer import Anonymizer
from src.trace_deidentifier.anonymizer.strategies.detect_emails import (
    EmailDetectionStrategy,
)
from src.trace_deidentifier.anonymizer.strategies.detect_geolocations import (
    GeoLocationDetectionStrategy,
)
from src.trace_deidentifier.anonymizer.strategies.detect_ipsv4 import (
    Ipv4DetectionStrategy,
)
from src.trace_deidentifier.anonymizer.strategies.detect_ipsv6 import (
    Ipv6DetectionStrategy,
)
from src.trace_deidentifier.anonymizer.strategies.remove_fields import (
    RemoveFieldsStrategy,
)
from src.trace_deidentifier.anonymizer.strategies.replace_values import (
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
            EmailDetectionStrategy(),
            Ipv4DetectionStrategy(),
            Ipv6DetectionStrategy(),
            GeoLocationDetectionStrategy(),
        ],
        logger=request.state.logger,
    )
