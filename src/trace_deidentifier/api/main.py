from fastapi import FastAPI

from .exception_handler import ExceptionHandler
from .routers.anonymize import router as anonymize_router

app = FastAPI(
    title="Deidentifier API",
    version="0.0.1",
)

exception_handler = ExceptionHandler()
exception_handler.configure(app)

app.include_router(router=anonymize_router)
