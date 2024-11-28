from typing import Annotated

from pydantic import Field, BeforeValidator
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

    environment: Annotated[
        Environment,
        BeforeValidator(lambda v: Environment[v.upper()] if isinstance(v, str) else v),
    ] = Field(default=Environment.PRODUCTION.value)

    log_level: Annotated[
        LogLevel,
        BeforeValidator(lambda v: LogLevel.from_str(v) if isinstance(v, str) else v),
    ] = Field(default=LogLevel.INFO.name)

    def get_environment(self) -> Environment:
        """Inherited from ConfigContract.get_environment."""
        return self.environment

    def get_log_level(self) -> LogLevel:
        """Inherited from ConfigContract.get_log_level."""
        return self.log_level

    def is_env_production(self):
        """Inherited from ConfigContract.is_env_production."""
        return self.environment == Environment.PRODUCTION
