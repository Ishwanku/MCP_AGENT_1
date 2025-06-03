"""
Agent implementations for MCP Agent PoC.

This package contains the implementations of various agents that provide
different functionalities in the MCP system:

- Memory Agent: Stores and retrieves information using vector storage
- Tasks Agent: Manages task-related operations with priority and status tracking
- Calendar Agent: Handles scheduling and time-based operations with Google Calendar integration
- Crawler Agent: Performs web crawling and data extraction with metadata storage

Each agent is implemented as a FastMCP server that exposes specific tools
for its functionality.

Example:
    >>> from agents.memory_agent import mcp as memory_mcp
    >>> from agents.tasks_agent import mcp as tasks_mcp
    >>> # Use the MCP instances to define tools and start servers
"""

from .memory_agent import mcp as memory_mcp
from .tasks_agent import mcp as tasks_mcp
from .calendar_agent import mcp as calendar_mcp
from .crawler_agent import mcp as crawler_mcp

__all__ = [
    'memory_mcp',
    'tasks_mcp',
    'calendar_mcp',
    'crawler_mcp',
]
