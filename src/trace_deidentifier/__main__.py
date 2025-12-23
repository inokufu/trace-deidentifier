"""Entry point for running the application."""

import uvicorn


def main() -> None:
    """Run the FastAPI application."""
    uvicorn.run(
        "trace_deidentifier.api.main:app",
        host="0.0.0.0",
        port=8001,
        reload=True,
    )


if __name__ == "__main__":
    main()
