"""
Utility modules for MCP Agent PoC.

This package contains utility modules used throughout the application:
- starlette: Utilities for creating FastMCP server applications
- memory: Utilities for working with the Mem0 memory system
"""

from .starlette import create_starlette_app
from .memory import get_mem0_client

__all__ = [
    'create_starlette_app',
    'get_mem0_client',
] 