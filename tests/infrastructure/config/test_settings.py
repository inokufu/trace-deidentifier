import os
from typing import Generator

import pytest
from pydantic import ValidationError
from pydantic_settings import SettingsConfigDict

from src.trace_deidentifier.infrastructure.config.environment import Environment
from src.trace_deidentifier.infrastructure.config.settings import Settings
from src.trace_deidentifier.infrastructure.logging.loglevel import LogLevel


class TestSettings:
    """Test suite for Settings class."""

    @pytest.fixture
    def clean_env(self) -> Generator[None, None, None]:
        """Temporarily clear environment variables and prevent .env loading."""
        original_env = dict(os.environ)
        os.environ.clear()

        # Save the original configuration
        original_config = Settings.model_config

        # Disable .env loading during tests
        Settings.model_config = SettingsConfigDict(env_file=None)

        yield

        # Restore config and environment variables
        Settings.model_config = original_config
        os.environ.update(original_env)

    def test_default_values(self, clean_env):
        """Test that settings loads with correct default values."""
        settings = Settings()
        assert settings.environment == Environment.PRODUCTION
        assert settings.log_level == LogLevel.INFO

    def test_environment_override(self, clean_env):
        """Test that environment variables override defaults."""
        os.environ["ENVIRONMENT"] = "development"
        os.environ["LOG_LEVEL"] = "debug"

        settings = Settings()
        assert settings.environment == Environment.DEVELOPMENT
        assert settings.log_level == LogLevel.DEBUG

    def test_invalid_environment(self, clean_env):
        """Test that invalid environment raises error."""
        os.environ["ENVIRONMENT"] = "invalid"

        with pytest.raises(KeyError):
            Settings()

    def test_invalid_log_level(self, clean_env):
        """Test that invalid log level raises error."""
        os.environ["LOG_LEVEL"] = "invalid"

        with pytest.raises(ValidationError) as exc_info:
            Settings()
        assert "log_level" in str(exc_info.value)
        assert len(exc_info.value.errors()) == 1

    def test_is_env_production(self, clean_env):
        """Test is_env_production helper method."""
        settings = Settings(environment=Environment.PRODUCTION)
        assert settings.is_env_production() is True

        settings = Settings(environment=Environment.DEVELOPMENT)
        assert settings.is_env_production() is False

    def test_case_insensitive_values(self, clean_env):
        """Test case insensitivity for environment and log level."""
        os.environ["ENVIRONMENT"] = "DeVelOpMeNt"
        os.environ["LOG_LEVEL"] = "DeBuG"

        settings = Settings()
        assert settings.environment == Environment.DEVELOPMENT
        assert settings.log_level == LogLevel.DEBUG
