import asyncio
import os
import json
from dotenv import load_dotenv
import yaml
from llm_client import LLMClient
from utils.client_manager import ClientManager

# Load environment variables from .env
load_dotenv()

# Debug prints for environment variables
print(f"DEBUG: LLM_PROVIDER: {os.getenv('LLM_PROVIDER')}")
print(f"DEBUG: GEMINI_API_KEY: {os.getenv('GEMINI_API_KEY')}")
print(f"DEBUG: OPENAI_API_KEY: {os.getenv('OPENAI_API_KEY')}")
print(f"DEBUG: GROK_API_KEY: {os.getenv('GROK_API_KEY')}")
print(f"DEBUG: OLLAMA_HOST: {os.getenv('OLLAMA_HOST')}")
print(f"DEBUG: OLLAMA_BASE_URL: {os.getenv('OLLAMA_BASE_URL')}")
print(f"DEBUG: LLM_MODEL: {os.getenv('LLM_MODEL')}")

async def main():
    """Main function to run the LLM-powered tool-using client."""
    print("Initializing ClientManager for LLM-driven tool use...")
    client_manager = ClientManager()
    
    # Load MCP server configurations
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

    # Initialize LLM client
    try:
        llm_client = LLMClient()
    except Exception as e:
        print(f"Failed to initialize LLM client: {e}")
        await client_manager.cleanup()
        return

    # Get query from user
    query = input("\nEnter your query for the LLM (e.g., 'Crawl example.com for titles', 'Search example.com for privacy policy'): ")
    if not query:
        print("No query entered. Exiting.")
        await client_manager.cleanup()
        return

    print(f"\nSending query to LLM ('{llm_client.model}') with available tools...")
    try:
        # Send the query and available tools to the LLM
        response = await llm_client.chat(
            messages=[{"role": "user", "content": f"User's query: {query}"}],
            tools=client_manager.tools
        )

        if response.get("error"):
            print(f"LLM error: {response['error']}")
            await client_manager.cleanup()
            return

        # Check if the LLM decided to call a tool
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
            # Process the tool call(s) using ClientManager
            results = await client_manager.process_tool_call(tool_calls)
            print("\n--- Tool Call Results ---")
            if results:
                for result in results:
                    print(yaml.dump(result) if isinstance(result, (dict, list)) else result)
            else:
                print("Tool call processed, but no explicit result returned or an error occurred.")
        else:
            # If no tool call, print the LLM's direct response
            print("\n--- LLM Response (no tool call) ---")
            print(response["message"]["content"])
    
    except Exception as e:
        print(f"An error occurred during LLM interaction or tool processing: {e}")

    finally:
        # Clean up all client connections
        print("\nCleaning up client connections...")
        await client_manager.cleanup()
        print("ClientManager cleanup complete.")

if __name__ == "__main__":
    asyncio.run(main())