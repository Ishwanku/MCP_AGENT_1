"""
A simple example MCP client demonstrating direct tool calls to an MCP server.

This script defines an `MCPClient` class that can connect to a single MCP server,
list its available tools, and call a specific tool. It's designed to interact
with an MCP server that exposes tools (e.g., a calendar server).

The main part of the script demonstrates connecting to the calendar server 
(localhost:8020) and calling available tools.
"""
import os
import asyncio
from typing import Any, Optional, Dict, List
import yaml
from dotenv import load_dotenv
from mcp.server.fastmcp import ClientSession
from mcp.server.sse import sse_client

# Load environment variables from .env file
# This allows configuration of server URLs and API keys through environment variables
load_dotenv()

class MCPClient:
    """A client for interacting with a Model Context Protocol (MCP) server."""

    def __init__(self, server_url: str, api_key: str):
        """
        Initializes the MCPClient with server connection details.

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
        Connects to the MCP server using Server-Sent Events (SSE), initializes the session,
        and lists available tools on the server.
        """
        print(f"Connecting to MCP server at {self.server_url}...")
        # Establish an SSE connection with the server using the provided API key for authentication
        self._streams_context = sse_client(url=self.server_url, headers={"Authorization": f"Bearer {self.api_key}"})
        streams = await self._streams_context.__aenter__()

        # Initialize the MCP client session using the SSE streams
        self._session_context = ClientSession(*streams)
        self.session = await self._session_context.__aenter__()
        
        # Complete the initialization of the MCP session
        await self.session.initialize()
        print("MCP session initialized.")

        print("Available tools on the server:")
        # Retrieve the list of tools available on the server
        response = await self.session.list_tools()
        server_tools = response.tools
        self.tools = []
        for tool in server_tools:
            print(f"  Name: {tool.name}")
            print(f"  Description: {tool.description}")
            print("  Input Schema:")
            print(f"    {yaml.dump(tool.inputSchema).replace(os.linesep, os.linesep + '    ')}")
            print("---")
            # Store the tool information in a format compatible with OpenAI tool calling
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
        # Send the tool call request to the server and await the response
        response = await self.session.call_tool(tool_name, tool_input)
        print(f"Received response from '{tool_name}': {response}")
        return response

    async def cleanup(self):
        """Cleans up the MCP session and SSE connection resources to ensure proper shutdown."""
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
        print("Client: Cleanup complete.")

async def main():
    """Main function to demonstrate MCPClient usage with the Calendar Server."""
    # Hardcoded values for Calendar Server
    target_server_url = "http://localhost:8020/sse"
    target_api_key = "secret-key2"
    print(f"SimpleClient: Targeting Calendar Server at {target_server_url}, API_Key_Ending_With={target_api_key[-4:]}")
    client = MCPClient(server_url=target_server_url, api_key=target_api_key)
    try:
        # Connect to the server and list available tools
        await client.connect_to_sse_server()
        # Dynamically call tools based on what's available
        for tool in client.tools:
            tool_name = tool['function']['name']
            print(f"\nAttempting to call tool '{tool_name}'...")
            try:
                if tool_name == 'get_events':
                    response = await client.call_tool(tool_name=tool_name, tool_input=None)
                elif tool_name == 'add_event':
                    response = await client.call_tool(tool_name=tool_name, tool_input={"title": "Test Event", "start": "2025-06-01T10:00:00", "end": "2025-06-01T11:00:00"})
                else:
                    response = await client.call_tool(tool_name=tool_name, tool_input=None)
                if response.content and response.content[0].type == "text":
                    print(f"Content from '{tool_name}':\n{response.content[0].text}")
                elif response.content:
                    print(f"Content from '{tool_name}':\n{response.content}")
                else:
                    print(f"No content returned from '{tool_name}'")
            except Exception as e:
                print(f"Error executing tool {tool_name}: {e}")
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        # Ensure resources are properly cleaned up
        await client.cleanup()

if __name__ == "__main__":
    # Run the main async function to start the client
    asyncio.run(main()) 