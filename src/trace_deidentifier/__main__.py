"""Entry point for running the application."""

import os

import uvicorn


def main() -> None:
    """Run the FastAPI application."""
    uvicorn.run(
        "trace_deidentifier.api.main:app",
        host=os.getenv("APP_INTERNAL_HOST", "0.0.0.0"),
        port=int(os.getenv("APP_INTERNAL_PORT", "8001")),
        reload=True,
    )


if __name__ == "__main__":
    main()
