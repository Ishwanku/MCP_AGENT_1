"""
Configuration management for MCP Agent PoC.

This module provides a centralized configuration system using Pydantic settings.
It handles environment variables, database settings, and API configurations.
All configuration is type-safe and validated at runtime.

Example:
    >>> from core.config import settings
    >>> print(settings.db.DATABASE_URL)
    'sqlite:///./mcp_agent.db'
"""

import os
from typing import Optional
from dotenv import load_dotenv
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

# Load environment variables from .env file
load_dotenv()


class DatabaseSettings(BaseSettings):
    """Database configuration settings.
    
    Attributes:
        DATABASE_URL: The database connection URL.
        ENABLE_MIGRATIONS: Whether to run database migrations on startup.
    """
    model_config = SettingsConfigDict(env_prefix="DB_")

    DATABASE_URL: str = Field(
        default="sqlite:///./mcp_agent.db",
        description="Database connection URL"
    )
    ENABLE_MIGRATIONS: bool = Field(
        default=True,
        description="Whether to run database migrations on startup"
    )


class APISettings(BaseSettings):
    """API configuration settings.
    
    Attributes:
        GOOGLE_CALENDAR_CREDENTIALS: Path to Google Calendar API credentials.
        GOOGLE_CALENDAR_TOKEN: Path to Google Calendar API token.
    """
    model_config = SettingsConfigDict(env_prefix="API_")

    GOOGLE_CALENDAR_CREDENTIALS: Optional[str] = Field(
        default=None,
        description="Path to Google Calendar API credentials"
    )
    GOOGLE_CALENDAR_TOKEN: Optional[str] = Field(
        default=None,
        description="Path to Google Calendar API token"
    )


class SecuritySettings(BaseSettings):
    """Security configuration settings.
    
    Attributes:
        SECRET_KEY: Secret key for JWT token generation.
        TOKEN_EXPIRE_MINUTES: JWT token expiration time in minutes.
    """
    model_config = SettingsConfigDict(env_prefix="SECURITY_")

    SECRET_KEY: str = Field(
        default=os.getenv("SECRET_KEY", "your-secret-key-here"),
        description="Secret key for JWT token generation"
    )
    TOKEN_EXPIRE_MINUTES: int = Field(
        default=30,
        description="JWT token expiration time in minutes"
    )


class Settings(BaseSettings):
    """Main settings class combining all configuration categories.
    
    This class combines all configuration categories into a single settings object.
    It provides access to database, API, and security settings, as well as
    server and logging configurations.
    
    Attributes:
        MEMORY_SERVER_PORT: Port for the memory server.
        TASKS_SERVER_PORT: Port for the tasks server.
        CALENDAR_SERVER_PORT: Port for the calendar server.
        CRAWLER_SERVER_PORT: Port for the crawler server.
        MEMORY_SERVER_API_KEY: API key for the memory server.
        TASKS_SERVER_API_KEY: API key for the tasks server.
        CALENDAR_SERVER_API_KEY: API key for the calendar server.
        CRAWLER_SERVER_API_KEY: API key for the crawler server.
        db: Database settings.
        api: API settings.
        security: Security settings.
        LOG_LEVEL: Logging level.
        LOG_FORMAT: Logging format string.
    """
    model_config = SettingsConfigDict(env_prefix="")

    # Server settings
    MEMORY_SERVER_PORT: int = Field(default=8030)
    TASKS_SERVER_PORT: int = Field(default=8010)
    CALENDAR_SERVER_PORT: int = Field(default=8020)
    CRAWLER_SERVER_PORT: int = Field(default=3006)

    # Server API keys
    MEMORY_SERVER_API_KEY: str = Field(default="secret-key3")
    TASKS_SERVER_API_KEY: str = Field(default="secret-key1")
    CALENDAR_SERVER_API_KEY: str = Field(default="secret-key2")
    CRAWLER_SERVER_API_KEY: str = Field(default="secret-key4")

    # Database settings
    db: DatabaseSettings = DatabaseSettings()

    # API settings
    api: APISettings = APISettings()

    # Security settings
    security: SecuritySettings = SecuritySettings()

    # Logging settings
    LOG_LEVEL: str = Field(default="INFO")
    LOG_FORMAT: str = Field(
        default="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )


# Create global settings instance
settings = Settings()

# Export settings and server configurations for use in other modules
MEMORY_SERVER_PORT = settings.MEMORY_SERVER_PORT
TASKS_SERVER_PORT = settings.TASKS_SERVER_PORT
CALENDAR_SERVER_PORT = settings.CALENDAR_SERVER_PORT
CRAWLER_SERVER_PORT = settings.CRAWLER_SERVER_PORT

MEMORY_SERVER_API_KEY = settings.MEMORY_SERVER_API_KEY
TASKS_SERVER_API_KEY = settings.TASKS_SERVER_API_KEY
CALENDAR_SERVER_API_KEY = settings.CALENDAR_SERVER_API_KEY
CRAWLER_SERVER_API_KEY = settings.CRAWLER_SERVER_API_KEY

__all__ = [
    "settings",
    "MEMORY_SERVER_PORT",
    "TASKS_SERVER_PORT",
    "CALENDAR_SERVER_PORT",
    "CRAWLER_SERVER_PORT",
    "MEMORY_SERVER_API_KEY",
    "TASKS_SERVER_API_KEY",
    "CALENDAR_SERVER_API_KEY",
    "CRAWLER_SERVER_API_KEY"
]
