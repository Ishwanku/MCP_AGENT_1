"""
Database connection and migration management for MCP Agent PoC.

This module provides database connection management and migration utilities
using SQLAlchemy and Alembic. It handles database initialization, session
management, and migration execution.

Example:
    >>> from core.database import init_db, get_session
    >>> init_db()
    >>> with get_session() as session:
    ...     # Use session for database operations
    ...     pass
"""

import logging
import os
from contextlib import contextmanager
from typing import Generator

import alembic.config
from alembic import op
from .config import settings
from .models import Base
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Session, sessionmaker

# Configure logging
logger = logging.getLogger(__name__)

# Create SQLAlchemy engine
engine = create_engine(settings.db.DATABASE_URL, echo=settings.LOG_LEVEL == "DEBUG")

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@contextmanager
def get_session() -> Generator[Session, None, None]:
    """Get a database session.
    
    This is a context manager that provides a database session and ensures
    proper cleanup after use.
    
    Yields:
        Session: A SQLAlchemy database session.
        
    Example:
        >>> with get_session() as session:
        ...     result = session.query(User).all()
    """
    session = SessionLocal()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


def init_db() -> None:
    """Initialize the database.
    
    This function creates all tables in the database if they don't exist.
    It should be called when the application starts.
    
    Example:
        >>> init_db()  # Creates all tables
    """
    try:
        # Create tables
        Base.metadata.create_all(bind=engine)

        # Run migrations if enabled
        if settings.db.ENABLE_MIGRATIONS:
            run_migrations()

        logger.info("Database initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize database: {str(e)}")
        raise


def run_migrations() -> None:
    """Run database migrations.
    
    This function executes any pending database migrations using Alembic.
    It should be called after init_db() if migrations are enabled.
    
    Example:
        >>> if settings.db.ENABLE_MIGRATIONS:
        ...     run_migrations()
    """
    try:
        # Get the directory containing this file
        current_dir = os.path.dirname(os.path.abspath(__file__))

        # Create Alembic configuration
        alembic_cfg = alembic.config.Config()
        alembic_cfg.set_main_option(
            "script_location", os.path.join(current_dir, "alembic")
        )
        alembic_cfg.set_main_option("sqlalchemy.url", settings.db.DATABASE_URL)

        # Run migrations
        alembic.command.upgrade(alembic_cfg, "head")
        logger.info("Database migrations completed successfully")
    except Exception as e:
        logger.error(f"Failed to run database migrations: {str(e)}")
        raise


# Export commonly used items
__all__ = ["get_session", "init_db", "run_migrations", "Base", "engine"]
