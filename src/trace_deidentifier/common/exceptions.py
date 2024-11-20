class TraceError(Exception):
    """Base class for Trace exceptions."""


class InvalidTraceError(TraceError):
    """Exception when a trace to his Pydantic model fails."""
