"""
Core functionality for the MCP Agent PoC.

This package contains the core components of the MCP Agent system:
- Configuration management
- Database connection and models
- MCP client implementation
- Utility functions

The core package provides the foundation for all agents and tools in the system.
"""

from .config import settings
from .database import init_db, run_migrations
from .models import Base, Task, Memory, CalendarEvent, CrawlerData
from .mcp_client import MCPClient

__all__ = [
    'settings',
    'init_db',
    'run_migrations',
    'Base',
    'Task',
    'Memory',
    'CalendarEvent',
    'CrawlerData',
    'MCPClient',
]
