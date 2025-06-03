"""
Tool definitions for MCP Agent PoC.

This package contains the tool definitions used by various agents in the system.
Each tool is a function that can be called by clients to perform specific actions.

The tools are organized by agent type:
- Memory Tools: Tools for storing and retrieving information
- Tasks Tools: Tools for managing tasks and their states
- Calendar Tools: Tools for handling calendar events and scheduling
- Crawler Tools: Tools for web crawling and data extraction

Example:
    >>> from tools.memory_tools import store_information, retrieve_information
    >>> # Use the tools in agent implementations
"""

from .memory_tools import (
    store_information,
    retrieve_information,
    search_information,
)

from .tasks_tools import (
    create_task,
    update_task,
    list_tasks,
    delete_task,
)

from .calendar_tools import (
    create_event,
    update_event,
    list_events,
    delete_event,
)

from .crawler_tools import (
    crawl_url,
    extract_content,
    save_data,
)

__all__ = [
    # Memory tools
    'store_information',
    'retrieve_information',
    'search_information',
    
    # Tasks tools
    'create_task',
    'update_task',
    'list_tasks',
    'delete_task',
    
    # Calendar tools
    'create_event',
    'update_event',
    'list_events',
    'delete_event',
    
    # Crawler tools
    'crawl_url',
    'extract_content',
    'save_data',
]
