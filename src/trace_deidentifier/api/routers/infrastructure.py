from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse

router = APIRouter()


@router.get("/health", status_code=200, tags=["Health"])
async def health_liveness() -> JSONResponse:
    """Return a simple liveness check."""
    return JSONResponse(content={"status": "ok", "service": "tdi-api"})


@router.get("/health/ready", status_code=200, tags=["Health"])
async def health_readiness(request: Request) -> JSONResponse:
    """Detailed health check endpoint."""
    return JSONResponse(
        {
            "status": "ok",
            "service": "tdi-api",
            "checks": {
                "env": {
                    "log_level": request.state.config.get_log_level().name,
                    "env": request.state.config.get_environment().name,
                },
            },
        },
    )
