from contextlib import asynccontextmanager
from typing import Any

from fastapi import FastAPI

from src.trace_deidentifier.infrastructure.config.settings import Settings
from src.trace_deidentifier.infrastructure.logging.loglevel import LogLevel
from src.trace_deidentifier.infrastructure.logging.loguru import LoguruLogger

from .exception_handler import ExceptionHandler
from .routers.anonymize import router as anonymize_router

config = Settings()


@asynccontextmanager
async def lifespan(_app: FastAPI) -> dict[str, Any]:
    """
    Lifespan context manager for the FastAPI application.

    :param _app: The FastAPI application instance
    :yield: A dictionary containing logger and config objects
    """
    logger = LoguruLogger(level=config.get_log_level())
    logger.info(
        "Application starting",
        {
            "app_log_level": config.get_log_level().name,
            "app_env": config.get_environment().name,
        },
    )

    yield {"config": config, "logger": logger}

    logger.info("Application shutting down")


app = FastAPI(
    title="Deidentifier API",
    version="0.0.1",
    debug=config.get_log_level() == LogLevel.DEBUG and not config.is_env_production(),
    lifespan=lifespan,
)

exception_handler = ExceptionHandler()
exception_handler.configure(app=app)

app.include_router(router=anonymize_router)
