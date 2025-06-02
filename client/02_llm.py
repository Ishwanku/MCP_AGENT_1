"""
Example client demonstrating LLM-driven tool usage with ClientManager.

This script initializes an OpenAI client and a ClientManager. It loads server
configurations, connects to MCP servers to get their available tools, and then
prompts the user for a query.

The query is sent to an LLM (e.g., GPT via OpenAI API or a local Ollama model
if configured for OpenAI compatibility) along with the list of tools gathered
from all MCP servers. The LLM decides if a tool call is appropriate.

If the LLM returns a tool call, the ClientManager processes it by dispatching
the call to the correct MCP server and tool. The result is then printed.
"""
import asyncio
import os
from dotenv import load_dotenv
from openai import OpenAI
import yaml # OpenAI client for interacting with LLMs
from utils.client_manager import ClientManager # Manages connections to multiple MCP servers

# Load environment variables from .env (e.g., OPENAI_API_KEY, OLLAMA_BASE_URL, MODEL)
load_dotenv()

# --- BEGIN DEBUG PRINTS ---
print(f"DEBUG: OPENAI_API_KEY: {os.getenv('OPENAI_API_KEY')}")
print(f"DEBUG: OPENAI_BASE_URL: {os.getenv('OPENAI_BASE_URL')}")
print(f"DEBUG: OLLAMA_BASE_URL (for reference): {os.getenv('OLLAMA_BASE_URL')}")
print(f"DEBUG: MODEL: {os.getenv('MODEL')}")
# --- END DEBUG PRINTS ---

# Initialize the OpenAI client.
# This will use OPENAI_API_KEY by default.
# If using a local Ollama model with an OpenAI-compatible API, ensure OLLAMA_BASE_URL is set
# in your .env and that your local Ollama server is running.
# Example .env for Ollama: OPENAI_API_KEY="ollama" OLLAMA_BASE_URL="http://localhost:11434/v1"

ollama_base_url = os.getenv("OLLAMA_BASE_URL")
if ollama_base_url:
    print(f"DEBUG: Using Ollama base URL: {ollama_base_url}")
    # Explicitly pass a non-empty api_key, as some Ollama OpenAI-compatible endpoints might expect it
    # even if not strictly validated, for all parameters (like model) to be processed correctly.
    client = OpenAI(base_url=ollama_base_url, api_key=os.getenv("OPENAI_API_KEY", "ollama"))
else:
    client = OpenAI()

# Get the LLM model choice from environment variable, defaulting to gpt-4o-mini
# This can be changed to a local model like "llama3" if using Ollama
model = os.getenv("MODEL", "gpt-4o-mini") 

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

    # Get query from user
    query = input("\nEnter your query for the LLM (e.g., 'What are my tasks?', 'Save a memory: I had a great meeting today.'): ")
    if not query:
        print("No query entered. Exiting.")
        await client_manager.cleanup()
        return

    print(f"\nSending query to LLM ('{model}') with available tools...")
    try:
        # LLM Interaction Block
        # -----------------------
        # Tool usage is currently commented out to allow this script to work with LLMs 
        # (like llama3 via Ollama) that might not fully support OpenAI-compatible tool calling 
        # or when a specific tool-supporting model (e.g., qwen2:7b-instruct) is not available.
        #
        # To re-enable LLM-driven tool usage:
        # 1. Ensure your .env file specifies a MODEL that supports OpenAI-compatible tool calls 
        #    (e.g., MODEL="qwen2:7b-instruct" when using Ollama, or a suitable OpenAI model).
        # 2. Ensure the chosen model is running and accessible (e.g., `ollama pull qwen2:7b-instruct`).
        # 3. Uncomment the 'tools' and 'tool_choice' parameters in the call below.
        # -----------------------

        # Send the query and available tools to the LLM
        response = client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": f"User's query: {query}"}],
            # tools=client_manager.tools, # Provide the aggregated list of tools to the LLM
            # tool_choice="auto",         # Let the LLM decide whether to use a tool
            temperature=0.0,            # Low temperature for more deterministic tool calls
        )

        # Check if the LLM decided to call a tool
        llm_message = response.choices[0].message
        if llm_message.tool_calls:
            print("LLM decided to call a tool.")
            # Process the tool call(s) using ClientManager
            # This will find the right MCP client and execute the tool call
            results = await client_manager.process_tool_call(llm_message.tool_calls)
            print("\n--- Tool Call Results ---")
            if results:
                for result in results:
                    print(yaml.dump(result) if isinstance(result, (dict, list)) else result)
            else:
                print("Tool call processed, but no explicit result returned or an error occurred.")
        else:
            # If no tool call, print the LLM's direct response
            print("\n--- LLM Response (no tool call) ---")
            print(llm_message.content)
    
    except Exception as e:
        print(f"An error occurred during LLM interaction or tool processing: {e}")

    finally:
        # Clean up all client connections
        print("\nCleaning up client connections...")
        await client_manager.cleanup()
        print("ClientManager cleanup complete.")

if __name__ == "__main__":
    asyncio.run(main())