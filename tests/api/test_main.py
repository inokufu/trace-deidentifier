import pytest
from fastapi import FastAPI
from logger import LoggerContract

from src.trace_deidentifier.api.main import lifespan
from src.trace_deidentifier.infrastructure.config.contract import ConfigContract


class TestMain:
    """Test suite for main API file."""

    @pytest.mark.asyncio
    async def test_lifespan_initializes_correctly(self) -> None:
        """Test that lifespan correctly initializes configuration and logger."""
        app = FastAPI()

        async with lifespan(app) as state:
            assert "config" in state
            assert "logger" in state

            assert isinstance(state["config"], ConfigContract)
            assert isinstance(state["logger"], LoggerContract)
