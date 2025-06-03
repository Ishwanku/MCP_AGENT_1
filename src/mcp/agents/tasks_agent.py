"""
MCP Server for managing tasks.

This server provides tools to read, add, and mark tasks as done.
It uses utility functions to interact with a task storage system (e.g., JSON file)
and exposes these capabilities through the FastMCP protocol.
"""
import os
import sys
import asyncio

# Add the parent directory to the path so we can import from config
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from ..server.fastmcp import FastMCP
from ..core.config import TASKS_SERVER_PORT, TASKS_SERVER_API_KEY
from ..utils.tasks import add_task, mark_task_as_done, read_tasks
from dotenv import load_dotenv

# Load environment variables from .env file
# This allows configuration of API keys, host, port, etc. through environment variables
load_dotenv()

# Define tasks-related tools
def get_tasks(data: dict) -> dict:
    """List all tasks with optional filtering.
    
    Args:
        data (dict): Dictionary potentially containing 'status' and 'priority' filters.
    
    Returns:
        dict: Response with status and list of tasks.
    """
    status = data.get('status')
    priority = data.get('priority')
    tasks = read_tasks(status=status, priority=priority)
    return {'status': 'success', 'tasks': tasks}

def add_new_task(data: dict) -> dict:
    """Create a new task.
    
    Args:
        data (dict): Dictionary containing task details like 'title', 'description', 'priority', 'due_date'.
    
    Returns:
        dict: Response with status and task ID.
    """
    title = data.get('title', '')
    if not title:
        return {'status': 'error', 'message': 'No title provided'}
    
    task = add_task(
        title=title,
        description=data.get('description', ''),
        priority=data.get('priority', 'medium'),
        due_date=data.get('due_date')
    )
    return {'status': 'success', 'task': task}

def complete_task(data: dict) -> dict:
    """Mark a task as completed.
    
    Args:
        data (dict): Dictionary containing 'task_id'.
    
    Returns:
        dict: Response with status and message.
    """
    task_id = data.get('task_id')
    if not task_id:
        return {'status': 'error', 'message': 'No task ID provided'}
    
    task = mark_task_as_done(task_id)
    if task is None:
        return {'status': 'error', 'message': f'Task {task_id} not found'}
    
    return {'status': 'success', 'task': task}

# Initialize FastMCP server for Task Management operations
tasks_server = FastMCP(name="Tasks Agent", port=TASKS_SERVER_PORT, api_key=TASKS_SERVER_API_KEY)

# Register tasks tools
tasks_server.register_tool('get_tasks', get_tasks)
tasks_server.register_tool('add_new_task', add_new_task)
tasks_server.register_tool('complete_task', complete_task)

if __name__ == "__main__":
    # The FastMCP instance has its own run method that starts Uvicorn.
    tasks_server.run()