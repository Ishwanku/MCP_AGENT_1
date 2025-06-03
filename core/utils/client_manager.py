"""
Manages connections and tool interactions with multiple MCP (Model Context Protocol) servers.

This module provides the `ClientManager` class, which is responsible for:
- Loading server configurations from a YAML file.
- Establishing connections to multiple MCP servers using `MCPClient` instances.
- Aggregating tool definitions from all connected servers.
- Dispatching tool calls from an LLM to the appropriate MCP server and tool.
- Handling cleanup of all server connections.
"""
import json
import yaml
# Updated import to use 'Client' instead of 'MCPClient' due to library update or naming change
from fastmcp.client import Client as MCPClient
# Removed incorrect import for transport as it does not exist in fastmcp
# from fastmcp.transport.http import HTTPTransport  # Adjust based on actual library structure if different
from typing import List, Any

class ClientManager:
    def __init__(self):
        self.clients: List[MCPClient] = []
        self.tools = []

    def load_servers(self, config_file: str):
        """Load server configurations from a YAML file."""
        try:
            with open(config_file, 'r') as f:
                config = yaml.safe_load(f)
                print(f"ClientManager: Loaded config from {config_file}: {config}")
            servers_config = config.get('servers', {})
            print(f"ClientManager: Number of servers in config: {len(servers_config)}")
            for server_name, server_info in servers_config.items():
                server_url = f"http://{server_info['host']}:{server_info['port']}/sse"
                api_key = server_info.get('api_key', '')
                print(f"ClientManager: Processing server {server_name} with URL {server_url}")
                try:
                    # Removed transport initialization as it does not exist in fastmcp
                    # transport = HTTPTransport()  # Create transport instance, adjust if different in library
                    client = MCPClient(name=server_name, server_url=server_url, api_key=api_key)
                    self.clients.append(client)
                    # Store tool names for lookup during process_tool_call
                    client.tools = server_info.get('tools', [])
                    print(f"ClientManager: Successfully added server configuration: {server_name} ({server_url})")
                except Exception as e:
                    print(f"ClientManager: Error creating client for server {server_name}: {e}")
        except Exception as e:
            print(f"ClientManager: Error loading server configurations from {config_file}: {e}")

    async def connect_to_server(self):
        """Connect to all configured servers and collect their tools."""
        for client in self.clients:
            try:
                await client.connect()
                print(f"ClientManager: Connected to server '{client.name}'")
                tools = await client.list_tools()
                for tool in tools:
                    tool_def = {
                        "type": "function",
                        "function": {
                            "name": tool.name,
                            "description": tool.description,
                            "parameters": {
                                "type": tool.input_schema.get("type", "object"),
                                "properties": tool.input_schema.get("properties", {}),
                                "required": tool.input_schema.get("required", [])
                            }
                        }
                    }
                    self.tools.append(tool_def)
                    print(f"ClientManager: Registered tool '{tool.name}' from server '{client.name}'")
            except Exception as e:
                print(f"ClientManager: Error connecting to server '{client.name}': {e}")

    async def process_tool_call(self, tool_calls: List[Any]) -> List[Any]:
        """Process a list of tool calls by dispatching them to the appropriate server."""
        results = []
        for tool_call in tool_calls:
            tool_name = tool_call.function.name
            try:
                tool_arguments = json.loads(tool_call.function.arguments)
            except json.JSONDecodeError as e:
                print(f"ClientManager: Error decoding JSON arguments for tool '{tool_name}': {e}")
                results.append(f"Error: Invalid arguments for tool '{tool_name}'.")
                continue

            client_for_tool = None
            for client in self.clients:
                if tool_name in client.tools:
                    client_for_tool = client
                    break

            if not client_for_tool:
                print(f"ClientManager: No server found for tool '{tool_name}'")
                results.append(f"Error: Tool '{tool_name}' not found.")
                continue

            try:
                response_from_tool = await client_for_tool.call_tool(tool_name, tool_arguments)
                # Handle varied response formats
                if hasattr(response_from_tool, 'content') and isinstance(response_from_tool.content, list) and response_from_tool.content:
                    if hasattr(response_from_tool.content[0], 'text'):
                        results.append(response_from_tool.content[0].text)
                    else:
                        results.append(response_from_tool.content)
                else:
                    results.append(response_from_tool)  # Handle dict or other formats (e.g., crawler tools)
            except Exception as e:
                print(f"ClientManager: Error executing tool '{tool_name}' on server '{client_for_tool.name}': {e}")
                results.append(f"Error: Failed to execute tool '{tool_name}'.")

        return results

    async def cleanup(self):
        """Cleans up resources for all managed MCPClient instances."""
        print("ClientManager: Cleaning up all client connections...")
        for client in reversed(self.clients):
            try:
                await client.cleanup()
            except Exception as e:
                print(f"ClientManager: Error during cleanup for client '{client.name}': {e}")
        print("ClientManager: All clients cleaned up.")