"""
Example client demonstrating the use of ClientManager to interact with multiple MCP servers.

This script initializes a ClientManager, loads server configurations from `servers.yaml`,
connects to all configured servers, lists all available tools from all servers,
and then cleans up the connections.

It showcases how ClientManager can simplify managing connections and tools
from various MCP servers simultaneously.
"""
import asyncio
import yaml
from utils.client_manager import ClientManager

async def main():
    """Main function to demonstrate ClientManager for multi-server interaction."""
    print("Initializing ClientManager...")
    client_manager = ClientManager()
    
    # Load server configurations from the YAML file
    # This file should define the URLs and API keys for each MCP server.
    print("Loading server configurations from servers.yaml...")
    client_manager.load_servers("servers.yaml")
    
    if not client_manager.clients:
        print("No servers configured in servers.yaml or failed to load. Exiting.")
        return

    print(f"Found {len(client_manager.clients)} server(s) configured.")

    # Connect to all configured MCP servers and list their tools
    # The connect_to_server method in ClientManager handles connecting to each client
    # and aggregating their tools.
    print("Connecting to all configured servers and fetching tools...")
    await client_manager.connect_to_server() 
    
    # Print all tools discovered from all connected servers
    print("\n--- All Discovered Tools ---")
    if client_manager.tools:
        print(yaml.dump(client_manager.tools))
    else:
        print("No tools found on any server or connection failed.")
    
    # Clean up all client sessions and connections
    print("\nCleaning up all client connections...")
    await client_manager.cleanup()
    print("ClientManager cleanup complete.")

if __name__ == "__main__":
    # Run the asynchronous main function
    asyncio.run(main())