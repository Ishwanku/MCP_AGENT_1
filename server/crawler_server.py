"""
MCP Server for web crawling operations.

This server provides tools to crawl web pages, entire sites, and search for specific content
within web pages. It uses tools defined in the tools directory and exposes these
capabilities through the FastMCP protocol.
"""
from mcp.server.fastmcp import FastMCP
from tools.crawler_tools import crawl_page_tool, crawl_site_tool, search_page_tool
import uvicorn
from utils.starlette import create_starlette_app

def start_crawler_server():
    """
    Starts the crawler server with the specified tools.
    
    This function initializes the FastMCP server with web crawling tools
    and starts the server on the specified host and port.
    """
    server = FastMCP(
        name="Crawler",
        host="localhost",
        port=3006,
        tools=[crawl_page_tool, crawl_site_tool, search_page_tool],
        context={}
    )
    # Create a Starlette app for the MCP server with specified API key
    starlette_app = create_starlette_app(server._mcp_server, api_key="secret-key4", debug=True)
    # Run the Uvicorn server
    uvicorn.run(starlette_app, host="localhost", port=3006)

if __name__ == "__main__":
    start_crawler_server()

# MCP Server for managing calendar events.
# This server provides a tool to retrieve a list of predefined calendar events.
# In a real application, this would connect to a calendar service (e.g., Google Calendar API).
# It uses YAML for formatting the event data and exposes the functionality via FastMCP.

"""
Import necessary libraries:
- yaml for formatting event data
- dotenv for loading environment variables from .env file
- FastMCP for creating the MCP server
- create_starlette_app for creating the Starlette app
- os for accessing environment variables
"""
import yaml
from dotenv import load_dotenv
from mcp.server.fastmcp import FastMCP
from utils.starlette import create_starlette_app
import os

# Load environment variables from .env file (if any)
load_dotenv()

# Initialize FastMCP server for Calendar operations
mcp = FastMCP("Calendar")

# Define a tool within the MCP server to retrieve calendar events
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
    # Use yaml.dump to convert the events data into a YAML string
    return yaml.dump(events_data)

# Check if the script is being run directly (not being imported)
if __name__ == "__main__":
    # Import uvicorn for running the server
    import uvicorn

    # Get server configurations from environment variables or use defaults
    # server_api_key is used for authentication, server_host is the host IP
    server_api_key = os.getenv("CALENDAR_SERVER_API_KEY", "secret-key2")
    server_host = os.getenv("CALENDAR_SERVER_HOST", "localhost")