from pydantic import Field, field_validator
from pydantic_core.core_schema import ValidationInfo
from pydantic_settings import BaseSettings, SettingsConfigDict

from src.trace_deidentifier.infrastructure.logging.loglevel import LogLevel

from .contract import ConfigContract
from .environment import Environment


class Settings(BaseSettings, ConfigContract):
    """
    Application settings loaded from environment variables, via Pydantic model
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
    )

    environment: Environment = Field(default=Environment.PRODUCTION.value)
    log_level: LogLevel = Field(default=LogLevel.INFO.name)

    @field_validator("log_level", mode="before")
    @classmethod
    def validate_log_level(
        cls,
        log_level: str | LogLevel,
        values: ValidationInfo,
    ) -> LogLevel:
        """
        Convert log level strings to their corresponding LogLevel enum.
        """
        if isinstance(log_level, str):
            return LogLevel.from_str(log_level)
        return log_level

    def get_environment(self) -> Environment:
        """Inherited from ConfigContract.get_environment."""
        return self.environment

    def get_log_level(self) -> LogLevel:
        """Inherited from ConfigContract.get_log_level."""
        return self.log_level

    def is_env_production(self):
        """Inherited from ConfigContract.is_env_production."""
        return self.environment == Environment.PRODUCTION
