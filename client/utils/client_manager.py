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
from typing import List, Dict, Any, Optional
from openai.types.chat import ChatCompletionMessageToolCall, ChatCompletionToolParam
from utils.client import MCPClient # The individual client for each MCP server

class ClientManager:
    """Manages multiple MCPClient instances and orchestrates tool calls."""

    def __init__(self):
        """Initializes the ClientManager with empty lists for clients, tools, and a tool map."""
        self.clients: List[MCPClient] = [] # List of active MCPClient instances
        # Aggregated list of tools from all servers, in OpenAI-compatible format
        self.tools: List[ChatCompletionToolParam] = [] 
        # Maps tool names to the MCPClient instance that provides the tool
        self.tool_map: Dict[str, MCPClient] = {}

    def load_servers(self, servers_file: str):
        """
        Loads server configurations from a YAML file and adds them as MCPClient instances.

        The YAML file should have a top-level key `servers`, which is a list of server objects,
        each with `name`, `url`, and `api_key`.

        Args:
            servers_file: Path to the YAML file containing server configurations.
        """
        print(f"ClientManager: Loading server configurations from '{servers_file}'...")
        try:
            with open(servers_file, "r") as f:
                servers_config = yaml.safe_load(f)
            if "servers" not in servers_config or not isinstance(servers_config["servers"], list):
                print(f"ClientManager: Error - '{servers_file}' must contain a top-level 'servers' list.")
                return
            
            for server_info in servers_config["servers"]:
                if not all(k in server_info for k in ["name", "url", "api_key"]):
                    print(f"ClientManager: Warning - Skipping server with missing info: {server_info}")
                    continue
                self._add_server(server_info["name"], server_info["url"], server_info["api_key"])
            print(f"ClientManager: Successfully loaded {len(self.clients)} server configurations.")
        except FileNotFoundError:
            print(f"ClientManager: Error - Server configuration file '{servers_file}' not found.")
        except yaml.YAMLError as e:
            print(f"ClientManager: Error parsing server configuration file '{servers_file}': {e}")
        except Exception as e:
            print(f"ClientManager: An unexpected error occurred while loading servers: {e}")

    async def connect_to_server(self):
        """
        Connects to all configured MCP servers and aggregates their tools.
        
        It iterates through each added MCPClient, calls its `connect_to_sse_server` method,
        then populates `self.tools` and `self.tool_map` with the discovered tools.
        """
        print("ClientManager: Connecting to all configured servers...")
        self.tools = [] # Clear previous tools
        self.tool_map = {} # Clear previous tool map

        for client in self.clients:
            try:
                await client.connect_to_sse_server() # Connect and fetch tools for this client
                self.tools.extend(client.tools) # Add this client's tools to the global list
                for tool_param in client.tools:
                    # The tool name is nested within the ChatCompletionToolParam structure
                    if tool_param.get("type") == "function" and tool_param.get("function"):
                        tool_name = tool_param["function"].get("name")
                        if tool_name:
                            self.tool_map[tool_name] = client
                        else:
                            print(f"ClientManager: Warning - Tool from client '{client.name}' has no name: {tool_param}")
            except Exception as e:
                print(f"ClientManager: Error connecting to or listing tools for server '{client.name}' at {client.server_url}: {e}")
        print(f"ClientManager: Connection process complete. Total tools aggregated: {len(self.tools)}.")

    async def process_tool_call(self, tool_calls: Optional[List[ChatCompletionMessageToolCall]]) -> List[Any]:
        """
        Processes a list of tool calls (typically from an LLM response) and returns their results.

        Args:
            tool_calls: A list of `ChatCompletionMessageToolCall` objects from an OpenAI response.

        Returns:
            A list of results from the executed tool calls. Each result is typically the text content.
        """
        if not tool_calls:
            return []

        results = []
        for tool_call in tool_calls:
            tool_name = tool_call.function.name
            print(f"ClientManager: Processing tool call for function: '{tool_name}'")
            
            client_for_tool = self.tool_map.get(tool_name)
            if not client_for_tool:
                print(f"ClientManager: Error - No client found for tool '{tool_name}'. Skipping.")
                results.append(f"Error: Tool '{tool_name}' not found.") # Or raise an error
                continue
            
            try:
                # Arguments are expected to be a JSON string by the OpenAI API
                tool_arguments = json.loads(tool_call.function.arguments)
                print(f"ClientManager: Calling tool '{tool_name}' on server '{client_for_tool.name}' with args: {tool_arguments}")
                
                # Delegate the actual tool call to the responsible MCPClient instance
                response_from_tool = await client_for_tool.call_tool(tool_name, tool_arguments)
                
                # Assuming the response content has a structure like response.content[0].text
                if response_from_tool.content and isinstance(response_from_tool.content, list) and response_from_tool.content[0].type == "text":
                    results.append(response_from_tool.content[0].text)
                else:
                    print(f"ClientManager: Warning - Unexpected response format from tool '{tool_name}': {response_from_tool.content}")
                    results.append(str(response_from_tool.content)) # Fallback to string representation

            except json.JSONDecodeError as e:
                print(f"ClientManager: Error decoding JSON arguments for tool '{tool_name}': {e}. Arguments: '{tool_call.function.arguments}'")
                results.append(f"Error: Invalid arguments for tool '{tool_name}'.")
            except Exception as e:
                print(f"ClientManager: Error executing tool '{tool_name}' on server '{client_for_tool.name}': {e}")
                results.append(f"Error: Failed to execute tool '{tool_name}'.")
                
        return results

    async def cleanup(self):
        """Cleans up resources for all managed MCPClient instances."""
        print("ClientManager: Cleaning up all client connections...")
        for client in reversed(self.clients): # Cleanup in reverse order of initialization
            try:
                await client.cleanup()
            except Exception as e:
                print(f"ClientManager: Error during cleanup for client '{client.name}': {e}")
        print("ClientManager: All clients cleaned up.")

    def _add_server(self, name: str, server_url: str, api_key: str):
        """
        Internal helper method to create and add an MCPClient to the manager.

        Args:
            name: Name of the server.
            server_url: URL of the server's SSE endpoint.
            api_key: API key for the server.
        """
        client = MCPClient(name, server_url, api_key)
        self.clients.append(client)
        print(f"ClientManager: Added server configuration: {name} ({server_url})")