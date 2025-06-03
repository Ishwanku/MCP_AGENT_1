"""
MCP Server for managing calendar events.

This server provides a tool to retrieve a list of predefined calendar events.
In a real application, this would connect to a calendar service (e.g., Google Calendar API).
It uses YAML for formatting the event data and exposes the functionality via FastMCP.
"""
import yaml
from dotenv import load_dotenv
from ..server.fastmcp import FastMCP
import os
import sys
import asyncio

# Add the parent directory to the path so we can import from config
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from ..core.config import CALENDAR_SERVER_PORT, CALENDAR_SERVER_API_KEY

# Load environment variables from .env file (if any)
# This allows configuration of API keys, host, port, etc. through environment variables
load_dotenv()

def get_events_tool(data: dict) -> dict:
    """List calendar events for a specified time range.
    
    Args:
        data (dict): Dictionary potentially containing 'start_date' and 'end_date'.
    
    Returns:
        dict: Response with status and list of events.
    """
    start_date = data.get('start_date', '')
    end_date = data.get('end_date', '')
    # Placeholder for actual event retrieval logic
    print(f"Retrieving events from {start_date} to {end_date}")
    return {'status': 'success', 'events': [{'id': 1, 'title': 'Sample Event', 'start_time': '2025-05-10T14:00:00', 'end_time': '2025-05-10T15:00:00', 'location': 'Virtual'}]}

# Initialize FastMCP server for Calendar operations
calendar_server = FastMCP(name="Calendar Agent", port=CALENDAR_SERVER_PORT, api_key=CALENDAR_SERVER_API_KEY)

# Register calendar tools
calendar_server.register_tool('get_events', get_events_tool)

if __name__ == "__main__":
    # The FastMCP instance has its own run method that starts Uvicorn.
    calendar_server.run()