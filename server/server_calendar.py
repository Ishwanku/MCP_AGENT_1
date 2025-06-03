"""
MCP Server for managing calendar events.

This server provides a tool to retrieve a list of predefined calendar events.
In a real application, this would connect to a calendar service (e.g., Google Calendar API).
It uses YAML for formatting the event data and exposes the functionality via FastMCP.
"""
import yaml
from dotenv import load_dotenv
from mcp.server.fastmcp import FastMCP
from utils.starlette import create_starlette_app
import os

# Load environment variables from .env file (if any)
# This allows configuration of API keys, host, port, etc. through environment variables
load_dotenv()

# Initialize FastMCP server for Calendar operations
# FastMCP is the protocol used for communication between clients and servers
mcp = FastMCP("Calendar")

@mcp.tool()
def get_events() -> str:
    """
    Retrieves a predefined list of calendar events.

    Currently, this returns a hardcoded list of events. In a production
    system, this would fetch events from a calendar API or database.

    Returns:
        A YAML string representing a list of calendar events.
        Each event is a dictionary with 'title', 'start', and 'end' times.
    """
    # Placeholder: In a real app, fetch from Google Calendar, Outlook, etc.
    # Define a list of calendar events with title, start, and end times
    events_data = [
        {
            "title": "MCP Stream",
            "start": "2025-05-30T10:00:00",
            "end": "2025-05-30T11:00:00",
        },
        {
            "title": "Team Meeting",
            "start": "2025-05-30T14:00:00",
            "end": "2025-05-30T15:00:00",
        },
    ]
    # Use yaml.dump to convert the events data into a YAML string for easy parsing by clients
    return yaml.dump(events_data)

if __name__ == "__main__":
    import uvicorn

    # Get server configurations from environment variables or use defaults
    # This allows the server to be configured without changing code
    server_api_key = os.getenv("CALENDAR_SERVER_API_KEY", "secret-key2")
    server_host = os.getenv("CALENDAR_SERVER_HOST", "localhost")
    server_port = int(os.getenv("CALENDAR_SERVER_PORT", "8020"))

    print(f"Starting Calendar Server: Host={server_host}, Port={server_port}, API_Key_Ending_With={server_api_key[-4:] if len(server_api_key) > 4 else '****'}")

    # Create a Starlette app for the MCP server with specified API key
    # Starlette is a lightweight ASGI framework for building async web applications
    starlette_app = create_starlette_app(mcp._mcp_server, api_key=server_api_key, debug=True)
    # Run the Uvicorn server, which is an ASGI server implementation for Python
    uvicorn.run(starlette_app, host=server_host, port=server_port)