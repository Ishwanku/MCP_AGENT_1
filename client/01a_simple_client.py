"""
A simple example MCP client demonstrating direct tool calls to an MCP server.

This script defines an `MCPClient` class that can connect to a single MCP server,
list its available tools, and call a specific tool. It's designed to interact
with an MCP server that exposes tools (e.g., a task manager server).

The main part of the script demonstrates connecting to the task manager server 
(localhost:8010) and calling the `get_tasks` tool.
"""
import os
import asyncio
from contextlib import AsyncExitStack
from typing import Any, Optional, Dict, List
import yaml
from dotenv import load_dotenv
from mcp import ClientSession
from mcp.client.sse import sse_client

load_dotenv()

class MCPClient:
    """A client for interacting with a Model Context Protocol (MCP) server."""

    def __init__(self, server_url: str, api_key: str):
        """
        Initializes the MCPClient.

        Args:
            server_url: The URL of the MCP server (SSE endpoint).
            api_key: The API key for authenticating with the server.
        """
        self.server_url = server_url
        self.api_key = api_key
        self.session: Optional[ClientSession] = None
        self.tools: List[Dict[str, Any]] = []
        self._streams_context = None
        self._session_context = None

    async def connect_to_sse_server(self):
        """
        Connects to the MCP server using SSE, initializes the session, and lists available tools.
        """
        print(f"Connecting to MCP server at {self.server_url}...")
        self._streams_context = sse_client(url=self.server_url, headers={"Authorization": f"Bearer {self.api_key}"})
        streams = await self._streams_context.__aenter__()

        self._session_context = ClientSession(*streams)
        self.session = await self._session_context.__aenter__()
        
        await self.session.initialize()
        print("MCP session initialized.")

        print("Available tools on the server:")
        response = await self.session.list_tools()
        server_tools = response.tools
        self.tools = []
        for tool in server_tools:
            print(f"  Name: {tool.name}")
            print(f"  Description: {tool.description}")
            print("  Input Schema:")
            print(f"    {yaml.dump(tool.inputSchema).replace(os.linesep, os.linesep + '    ')}")
            print("---")
            self.tools.append(
                {
                    "type": "function",
                    "function": {
                        "name": tool.name,
                        "description": tool.description,
                        "parameters": tool.inputSchema,
                    },
                }
            )
        print("Successfully connected and listed tools.")

    async def call_tool(self, tool_name: str, tool_input: Optional[Dict[str, Any]] = None) -> Any:
        """
        Calls a specific tool on the connected MCP server.

        Args:
            tool_name: The name of the tool to call.
            tool_input: A dictionary of arguments for the tool. Can be None if the tool takes no input.

        Returns:
            The response from the tool call.

        Raises:
            ValueError: If the session is not initialized (i.e., not connected).
        """
        if self.session is None:
            raise ValueError("Session not initialized. Call connect_to_sse_server() first.")
        
        print(f"Calling tool '{tool_name}' with input: {tool_input}")
        response = await self.session.call_tool(tool_name, tool_input)
        print(f"Received response from '{tool_name}': {response}")
        return response

    async def cleanup(self):
        """Cleans up the MCP session and SSE connection resources."""
        print("Cleaning up MCP client resources...")
        if self._session_context and self.session:
            try:
                await self._session_context.__aexit__(None, None, None)
                print("MCP session closed.")
            except Exception as e:
                print(f"Error during session cleanup: {e}")
            self.session = None
            self._session_context = None

        if self._streams_context:
            try:
                await self._streams_context.__aexit__(None, None, None)
                print("SSE streams closed.")
            except Exception as e:
                print(f"Error during streams cleanup: {e}")
            self._streams_context = None
        print(f"Client '{self.name}': Cleanup complete.")

async def main():
    """Main function to demonstrate MCPClient usage."""
    # Get server URL and API key from environment variables or use defaults
    # These defaults point to the Task Manager server as an example.
    # You can change these in your .env file to target a different server.
    target_server_url = os.getenv("SIMPLE_CLIENT_TARGET_URL", "http://localhost:8010/sse") 
    target_api_key = os.getenv("SIMPLE_CLIENT_TARGET_API_KEY", "secret-key1")

    print(f"SimpleClient: Targeting server at {target_server_url}, API_Key_Ending_With={target_api_key[-4:] if len(target_api_key) > 4 else '****'}")

    client = MCPClient(server_url=target_server_url, api_key=target_api_key)
    
    try:
        await client.connect_to_sse_server()
        
        print("\nAttempting to call tool 'get_tasks'...")
        response = await client.call_tool(tool_name="get_tasks", tool_input=None)
        
        if response.content and response.content[0].type == "text":
            print(f"Content from 'get_tasks':\n{response.content[0].text}")
        else:
            print(f"Received unexpected response format from 'get_tasks': {response.content}")
            
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        await client.cleanup()

if __name__ == "__main__":
    asyncio.run(main())