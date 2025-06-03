"""
MCP Server for managing long-term memory using Mem0.

This server provides tools to save, search, and retrieve memories.
It utilizes a Mem0 client for memory operations and exposes these
capabilities through the FastMCP protocol.
"""
import json
from mcp.server.fastmcp import FastMCP
from core.utils.starlette import create_starlette_app
from core.utils.memory import get_mem0_client
import warnings
import os
from dotenv import load_dotenv

# Load environment variables from .env file
# This allows configuration of API keys, host, port, etc. through environment variables
load_dotenv()

# Suppress specific DeprecationWarnings from websockets.legacy
# These warnings are filtered to avoid cluttering the console output with deprecation notices
warnings.filterwarnings("ignore", category=DeprecationWarning, module="websockets.legacy")
# Suppress the specific DeprecationWarning for websockets.server.WebSocketServerProtocol
warnings.filterwarnings("ignore", category=DeprecationWarning, message="websockets.server.WebSocketServerProtocol is deprecated")
warnings.filterwarnings("ignore", category=DeprecationWarning, message="The websockets.server.WebSocketServerProtocol class is deprecated. WebSocketServerProtocol is an alias for ServerProtocol.")

# Initialize FastMCP server for Memory operations
# FastMCP is the protocol used for communication between clients and servers
mcp = FastMCP("Memory")

@mcp.tool()
def save_memory(content: str) -> str:
    """
    Saves a new memory entry to the long-term memory storage.

    Args:
        content: The string content of the memory to save.

    Returns:
        A confirmation message indicating success.
    """
    # Get the Mem0 client instance for memory operations
    mem0_client = get_mem0_client()
    # In a production system, user_id would be dynamically obtained (e.g., from authenticated session)
    # Here, a static 'user' ID is used for simplicity
    mem0_client.add([{"role": "user", "content": content}], user_id="user")
    return f"Successfully saved memory: {content}"

@mcp.tool()
def search_memories(query: str) -> str:
    """
    Searches existing memories based on a query string using vector search.

    Args:
        query: The search query string to find relevant memories.

    Returns:
        A JSON string list of memory contents that match the query.
    """
    mem0_client = get_mem0_client()
    # In a production system, user_id would be dynamically obtained
    results = mem0_client.search(query, user_id="user")
    # Return only the content of the memories, formatted as JSON
    return json.dumps([result["content"] for result in results])

@mcp.tool()
def get_all_memories() -> str:
    """
    Retrieves all stored memories for the user from the memory database.

    Returns:
        A JSON string list of all memory contents.
    """
    mem0_client = get_mem0_client()
    # In a production system, user_id would be dynamically obtained
    results = mem0_client.get_all(user_id="user")
    # Return only the content of the memories, formatted as JSON
    return json.dumps([result["content"] for result in results])

if __name__ == "__main__":
    import uvicorn

    # Get server configurations from environment variables or use defaults
    # This allows the server to be configured without changing code
    server_api_key = os.getenv("MEMORY_SERVER_API_KEY", "secret-key3")
    server_host = os.getenv("MEMORY_SERVER_HOST", "localhost")
    server_port = int(os.getenv("MEMORY_SERVER_PORT", "8030"))

    print(f"Starting Memory Server: Host={server_host}, Port={server_port}, API_Key_Ending_With={server_api_key[-4:] if len(server_api_key) > 4 else '****'}")

    # Create a Starlette app for the MCP server with specified API key
    # Starlette is a lightweight ASGI framework for building async web applications
    starlette_app = create_starlette_app(mcp._mcp_server, api_key=server_api_key, debug=True)
    # Run the Uvicorn server, which is an ASGI server implementation for Python
    uvicorn.run(starlette_app, host=server_host, port=server_port)