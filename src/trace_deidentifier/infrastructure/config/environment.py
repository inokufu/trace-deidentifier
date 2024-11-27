from enum import StrEnum


class Environment(StrEnum):
    """
    Represents the different environments in which the application can run.
    """

    DEVELOPMENT = "development"
    PRODUCTION = "production"
