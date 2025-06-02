"""
MCP Server for managing tasks.

This server provides tools to read, add, and mark tasks as done.
It uses utility functions to interact with a task storage system (e.g., JSON file)
and exposes these capabilities through the FastMCP protocol.
"""
from mcp.server.fastmcp import FastMCP
from utils.starlette import create_starlette_app
# Renaming imported functions to avoid conflict with tool names
from utils.tasks import add_task as util_add_task, mark_task_as_done as util_mark_task_as_done, read_tasks as util_read_tasks
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Initialize FastMCP server for Task Management operations
mcp = FastMCP("Task Manager")

@mcp.tool()
def get_tasks() -> str:
    """
    Retrieves all tasks for the user.

    Returns:
        A string representation of the tasks (e.g., JSON).
    """
    # In a production system, user_id would be dynamically obtained
    return util_read_tasks("user")

@mcp.tool()
def add_new_task(task: str) -> str:  # Renamed to avoid conflict with imported add_task
    """
    Adds a new task for the user.

    Args:
        task: The description of the task to add.

    Returns:
        A confirmation message.
    """
    # In a production system, user_id would be dynamically obtained
    return util_add_task("user", task)

@mcp.tool()
def complete_task(task: str) -> str:  # Renamed to avoid conflict with imported mark_task_as_done
    """
    Marks a specified task as done for the user.

    Args:
        task: The description of the task to mark as done.

    Returns:
        A confirmation message.
    """
    # In a production system, user_id would be dynamically obtained
    return util_mark_task_as_done("user", task)

if __name__ == "__main__":
    import uvicorn

    # Get server configurations from environment variables or use defaults
    server_api_key = os.getenv("TASKS_SERVER_API_KEY", "secret-key1")
    server_host = os.getenv("TASKS_SERVER_HOST", "localhost")
    server_port = int(os.getenv("TASKS_SERVER_PORT", "8010"))

    print(f"Starting Tasks Server: Host={server_host}, Port={server_port}, API_Key_Ending_With={server_api_key[-4:] if len(server_api_key) > 4 else '****'}")

    # Create a Starlette app for the MCP server with specified API key
    starlette_app = create_starlette_app(mcp._mcp_server, api_key=server_api_key, debug=True)
    # Run the Uvicorn server
    uvicorn.run(starlette_app, host=server_host, port=server_port)