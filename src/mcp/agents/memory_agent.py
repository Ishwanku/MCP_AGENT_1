"""
MCP Server for managing long-term memory using Mem0.

This server provides tools to save, search, and retrieve memories.
It utilizes a Mem0 client for memory operations and exposes these
capabilities through the FastMCP protocol.
"""
import json
from ..server.fastmcp import FastMCP
import warnings
import os
from dotenv import load_dotenv
import sys
import asyncio

# Load environment variables from .env file
# This allows configuration of API keys, host, port, etc. through environment variables
load_dotenv()

# Suppress specific DeprecationWarnings from websockets.legacy
# These warnings are filtered to avoid cluttering the console output with deprecation notices
warnings.filterwarnings("ignore", category=DeprecationWarning, module="websockets.legacy")
# Suppress the specific DeprecationWarning for websockets.server.WebSocketServerProtocol
warnings.filterwarnings("ignore", category=DeprecationWarning, message="websockets.server.WebSocketServerProtocol is deprecated")
warnings.filterwarnings("ignore", category=DeprecationWarning, message="The websockets.server.WebSocketServerProtocol class is deprecated. WebSocketServerProtocol is an alias for ServerProtocol.")

# Add the parent directory to the path so we can import from config
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from ..core.config import MEMORY_SERVER_PORT, MEMORY_SERVER_API_KEY

# Define memory-related tools
def save_memory_tool(data: dict) -> str:
    """
    Saves a new memory entry to the long-term memory storage.

    Args:
        data (dict): Dictionary containing 'content' for the memory.

    Returns:
        A confirmation message indicating success.
    """
    content = data.get("content")
    if content is None:
        return "Error: 'content' not provided in data."
    # Placeholder for actual memory saving logic (e.g., to Qdrant)
    print(f"Saving memory: {content}")
    return f"Successfully saved memory: {content}"

def search_memories_tool(data: dict) -> str:
    """
    Searches existing memories based on a query string using vector search.

    Args:
        data (dict): Dictionary containing 'query' for the search.

    Returns:
        A JSON string list of memory contents that match the query.
    """
    query = data.get("query")
    if query is None:
        return "Error: 'query' not provided in data."
    # Placeholder for actual search logic
    print(f"Searching memories for: {query}")
    return json.dumps([f"Sample memory for {query}"])

def get_all_memories_tool(data: dict) -> str: # Added data param even if not used by placeholder
    """
    Retrieves all stored memories for the user from the memory database.

    Args:
        data (dict): Optional data dictionary (not used by placeholder).

    Returns:
        A JSON string list of all memory contents.
    """
    # Placeholder for actual retrieval logic
    print("Retrieving all memories")
    return json.dumps(["Memory 1", "Memory 2", "Memory 3", "Memory 4", "Memory 5"])

# Initialize FastMCP server for Memory operations
# FastMCP is the protocol used for communication between clients and servers
memory_server = FastMCP(name="Memory Agent", port=MEMORY_SERVER_PORT, api_key=MEMORY_SERVER_API_KEY)

# Register memory tools
memory_server.register_tool('save_memory', save_memory_tool)
memory_server.register_tool('search_memories', search_memories_tool)
memory_server.register_tool('get_all_memories', get_all_memories_tool)

if __name__ == "__main__":
    # The FastMCP instance has its own run method that starts Uvicorn.
    memory_server.run()