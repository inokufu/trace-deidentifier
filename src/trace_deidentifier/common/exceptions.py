class TraceError(Exception):
    """Base class for Trace exceptions."""


class InvalidTraceError(TraceError):
    """Exception raised when trace validation fails against its Pydantic model."""
