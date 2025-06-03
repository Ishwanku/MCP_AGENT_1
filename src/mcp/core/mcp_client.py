"""
MCP Client implementation for MCP Agent PoC.

This module provides a client for interacting with MCP servers.
It handles SSE (Server-Sent Events) connections and tool execution.

Example:
    >>> from core.mcp_client import MCPClient
    >>> client = MCPClient("http://localhost:8030/sse")
    >>> await client.connect()
    >>> result = await client.call_tool("store_information", {"key": "test", "value": "data"})
"""

import asyncio
from typing import Any, Dict, Optional

import aiohttp
import httpx
from sseclient import SSEClient


class MCPClient:
    """Client for interacting with MCP servers.
    
    This class provides methods to connect to MCP servers and execute tools.
    It uses Server-Sent Events (SSE) for real-time communication.
    
    Attributes:
        server_url: The URL of the MCP server to connect to.
        api_key: Optional API key for authentication.
        client: HTTP client for making requests.
        sse_client: SSE client for receiving server events.
    """
    
    def __init__(self, server_url: str, api_key: Optional[str] = None):
        """Initialize the MCP client.
        
        Args:
            server_url: The URL of the MCP server to connect to.
            api_key: Optional API key for authentication.
        """
        self.server_url = server_url
        self.api_key = api_key
        self.client = httpx.AsyncClient()
        self.sse_client: Optional[SSEClient] = None

    async def connect(self) -> None:
        """Connect to the MCP server.
        
        This method establishes an SSE connection to the server.
        It should be called before executing any tools.
        
        Raises:
            ConnectionError: If the connection fails.
        """
        headers = {}
        if self.api_key:
            headers["X-API-Key"] = self.api_key
            
        response = await self.client.get(
            self.server_url,
            headers=headers,
            timeout=None
        )
        
        if response.status_code != 200:
            raise ConnectionError(f"Failed to connect to server: {response.status_code}")
            
        self.sse_client = SSEClient(response)

    async def call_tool(self, tool_name: str, params: Dict[str, Any]) -> Any:
        """Execute a tool on the MCP server.
        
        Args:
            tool_name: The name of the tool to execute.
            params: The parameters to pass to the tool.
            
        Returns:
            The result of the tool execution.
            
        Raises:
            ConnectionError: If not connected to the server.
            ValueError: If the tool execution fails.
        """
        if not self.sse_client:
            raise ConnectionError("Not connected to server")
            
        # Send tool execution request
        response = await self.client.post(
            f"{self.server_url}/tools/{tool_name}",
            json=params,
            headers={"X-API-Key": self.api_key} if self.api_key else {}
        )
        
        if response.status_code != 200:
            raise ValueError(f"Tool execution failed: {response.status_code}")
            
        return response.json()

    async def close(self) -> None:
        """Close the connection to the MCP server.
        
        This method should be called when the client is no longer needed.
        """
        if self.sse_client:
            self.sse_client.close()
        await self.client.aclose()


# Export the client class
__all__ = ["MCPClient"]

async def connect_sse(url, client_name="crawler-client", version="1.0.0"):
    client = MCPClient(name=client_name, version=version)
    await client.connect(url)
    async with aiohttp.ClientSession() as session:
        async with session.get(f"{url}/sse") as response:
            print("Connected to MCP crawler server via SSE")
            async for line in response.content:
                if line.startswith(b"data:"):
                    event = line.decode("utf-8")[5:].strip()
                    print(f"SSE event: {event}")
                    # Process event (e.g., crawling progress)
    return client

if __name__ == "__main__":
    asyncio.run(connect_sse("http://localhost:3005"))