"""
LLM-powered MCP client for tool-using interactions with multiple servers.

This script demonstrates how to use an LLM (Large Language Model) to intelligently
interact with multiple MCP servers by selecting appropriate tools based on user queries.
It integrates with OpenAI-compatible APIs or local LLM setups like Ollama.
"""
import asyncio
import os
import json
from dotenv import load_dotenv
import yaml
from llm_client import LLMClient
from utils.client_manager import ClientManager

# Load environment variables from .env
# This allows configuration of LLM settings and server credentials through environment variables
load_dotenv()

# Debug prints for environment variables
# These help in troubleshooting configuration issues by displaying the loaded settings
print(f"DEBUG: LLM_PROVIDER: {os.getenv('LLM_PROVIDER')}")
print(f"DEBUG: GEMINI_API_KEY: {os.getenv('GEMINI_API_KEY')}")
print(f"DEBUG: OPENAI_API_KEY: {os.getenv('OPENAI_API_KEY')}")
print(f"DEBUG: GROK_API_KEY: {os.getenv('GROK_API_KEY')}")
print(f"DEBUG: OLLAMA_HOST: {os.getenv('OLLAMA_HOST')}")
print(f"DEBUG: OLLAMA_BASE_URL: {os.getenv('OLLAMA_BASE_URL')}")
print(f"DEBUG: LLM_MODEL: {os.getenv('LLM_MODEL')}")

async def main():
    """Main function to run the LLM-powered tool-using client for interacting with MCP servers."""
    print("Initializing ClientManager for LLM-driven tool use...")
    # Create a ClientManager instance to handle connections to multiple MCP servers
    client_manager = ClientManager()
    
    # Load MCP server configurations from a YAML file
    print("Loading server configurations from servers.yaml...")
    client_manager.load_servers("servers.yaml")

    if not client_manager.clients:
        print("No servers configured in servers.yaml or failed to load. Exiting.")
        return
    
    # Connect to all configured MCP servers and fetch their tool definitions
    print("Connecting to MCP servers and fetching tools...")
    await client_manager.connect_to_server()

    if not client_manager.tools:
        print("No tools found on any server or connection failed. Cannot proceed with LLM tool use.")
        await client_manager.cleanup()
        return
    
    print(f"Successfully loaded {len(client_manager.tools)} tools for the LLM.")

    # Initialize LLM client for intelligent tool selection and response generation
    try:
        llm_client = LLMClient()
    except Exception as e:
        print(f"Failed to initialize LLM client: {e}")
        await client_manager.cleanup()
        return

    # Get query from user to be processed by the LLM
    query = input("\nEnter your query for the LLM (e.g., 'Crawl example.com for titles', 'Search example.com for privacy policy'): ")
    if not query:
        print("No query entered. Exiting.")
        await client_manager.cleanup()
        return

    print(f"\nSending query to LLM ('{llm_client.model}') with available tools...")
    try:
        # Send the query and available tools to the LLM for processing
        response = await llm_client.chat(
            messages=[{"role": "user", "content": f"User's query: {query}"}],
            tools=client_manager.tools
        )

        if response.get("error"):
            print(f"LLM error: {response['error']}")
            await client_manager.cleanup()
            return

        # Check if the LLM decided to call a tool based on the user's query
        if response.get("tool_calls"):
            print("LLM decided to call a tool.")
            # Convert LLMClient tool calls to OpenAI-compatible format for ClientManager
            tool_calls = [
                type("ToolCall", (), {
                    "id": f"call_{i}",
                    "type": "function",
                    "function": type("Function", (), {
                        "name": tc["function"]["name"],
                        "arguments": json.dumps(tc["function"]["arguments"])
                    })()
                })()
                for i, tc in enumerate(response["tool_calls"])
            ]
            # Process the tool call(s) using ClientManager to interact with the appropriate server
            results = await client_manager.process_tool_call(tool_calls)
            print("\n--- Tool Call Results ---")
            if results:
                for result in results:
                    print(yaml.dump(result) if isinstance(result, (dict, list)) else result)
            else:
                print("Tool call processed, but no explicit result returned or an error occurred.")
        else:
            # If no tool call, print the LLM's direct response to the user
            print("\n--- LLM Response (no tool call) ---")
            print(response["message"]["content"])
    
    except Exception as e:
        print(f"An error occurred during LLM interaction or tool processing: {e}")

    finally:
        # Clean up all client connections to ensure proper shutdown of resources
        print("\nCleaning up client connections...")
        await client_manager.cleanup()
        print("ClientManager cleanup complete.")

if __name__ == "__main__":
    # Run the main async function to start the LLM-powered client
    asyncio.run(main())