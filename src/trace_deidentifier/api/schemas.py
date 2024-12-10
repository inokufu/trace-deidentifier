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
        examples=[
            {
                "trace": {
                    "data": {
                        "actor": {
                            "name": "John Doe",
                            "account": {
                                "name": "johndoe",
                                "homePage": "https://example.com",
                            },
                        },
                        "object": {
                            "id": "http://example.com/activities/course-001",
                            "definition": {
                                "extensions": {
                                    "http://id.tincanapi.com/extension/browser-info": "Chrome/91.0",
                                    "http://id.tincanapi.com/extension/ip-address": "192.168.1.1",
                                    "http://id.tincanapi.com/extension/geojson": "45.123°N 2.345°E",
                                },
                            },
                        },
                        "verb": {"id": "http://example.com/verbs/completed"},
                    },
                },
            },
        ],
    )


class AnonymizeTraceResponseModel(BaseModel):
    """
    Model for trace anonymization response.

    Attributes:
        trace (dict[str, Any]): The output trace data in xAPI format
    """

    trace: Trace = Field(
        description="Anonymized output trace",
        examples=[
            {
                "trace": {
                    "data": {
                        "actor": {
                            "name": "Anonymous",
                            "account": {
                                "name": "Anonymous",
                                "homePage": "https://anonymous.org",
                            },
                        },
                        "object": {
                            "id": "http://example.com/activities/course-001",
                            "definition": {},
                        },
                        "verb": {"id": "http://example.com/verbs/completed"},
                    },
                },
            },
        ],
    )
