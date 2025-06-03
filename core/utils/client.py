"""
Defines the MCPClient class, a generic client for interacting with a single
Model Context Protocol (MCP) server using Server-Sent Events (SSE).

This client handles connection, session initialization, tool listing, tool calling,
and cleanup for an MCP server. It is designed to be used by ClientManager
to manage connections to multiple such servers.
"""
from contextlib import AsyncExitStack
from typing import Any, Optional, List, Dict

from mcp import ClientSession
from mcp.client.sse import sse_client
from openai.types.chat import ChatCompletionToolParam

class MCPClient:
    """A generic client for a single MCP server."""

    def __init__(self, name: str, server_url: str, api_key: str):
        """
        Initializes the MCPClient.

        Args:
            name: A descriptive name for this client/server connection (e.g., "memory_server").
            server_url: The URL of the MCP server's SSE endpoint.
            api_key: The API key for authenticating with the server.
        """
        self.name = name
        self.server_url = server_url
        self.api_key = api_key
        self.session: Optional[ClientSession] = None
        self._streams_context = None
        self._session_context = None
        self.tools: List[ChatCompletionToolParam] = []

    async def connect_to_sse_server(self):
        """
        Connects to the MCP server via SSE, initializes the session, and retrieves available tools.
        Formats the tools into OpenAI's ChatCompletionToolParam structure.
        """
        print(f"Client '{self.name}': Connecting to {self.server_url}...")
        self._streams_context = sse_client(
            url=self.server_url, headers={"Authorization": f"Bearer {self.api_key}"}
        )
        streams = await self._streams_context.__aenter__()

        self._session_context = ClientSession(*streams)
        self.session = await self._session_context.__aenter__()
        
        await self.session.initialize()
        print(f"Client '{self.name}': Session initialized.")

        response = await self.session.list_tools()
        server_tools = response.tools
        self.tools = []
        for tool in server_tools:
            self.tools.append(
                ChatCompletionToolParam(
                    type="function",
                    function={
                        "name": tool.name,
                        "description": tool.description or "No description provided",
                        "parameters": tool.inputSchema,
                    },
                )
            )
        print(f"Client '{self.name}': Discovered {len(self.tools)} tools.")

    async def call_tool(self, tool_name: str, tool_input: Optional[Dict[str, Any]] = None) -> Any:
        """
        Calls a specific tool on the connected MCP server.

        Args:
            tool_name: The name of the tool to call.
            tool_input: A dictionary of arguments for the tool. Can be None.

        Returns:
            The response from the tool call.

        Raises:
            ValueError: If the session is not initialized.
        """
        if self.session is None:
            raise ValueError(f"Client '{self.name}': Session not initialized. Cannot call tool '{tool_name}'.")
        
        print(f"Client '{self.name}': Calling tool '{tool_name}' with input: {tool_input}")
        response = await self.session.call_tool(tool_name, tool_input)
        print(f"Client '{self.name}': Received response from '{tool_name}'.")
        return response

    async def cleanup(self):
        """Cleans up the MCP session and SSE connection resources."""
        print(f"Client '{self.name}': Cleaning up resources...")
        if self._session_context and self.session:
            try:
                await self._session_context.__aexit__(None, None, None)
                print(f"Client '{self.name}': Session closed.")
            except Exception as e:
                print(f"Client '{self.name}': Error during session cleanup: {e}")
            self.session = None
            self._session_context = None

        if self._streams_context:
            try:
                await self._streams_context.__aexit__(None, None, None)
                print(f"Client '{self.name}': SSE streams closed.")
            except Exception as e:
                print(f"Client '{self.name}': Error during streams cleanup: {e}")
            self._streams_context = None
        print(f"Client '{self.name}': Cleanup complete.")