"""
Main agent script that uses intent classification and LangChain for responses.

This script defines an `MCPAgent` that can understand user queries, classify their intent,
and then either use a tool via MCP servers (for memory, tasks, calendar) or generate
a direct response using an LLM (e.g., Ollama via LangChain).

The agent leverages:
- `ClientManager` to connect to various MCP servers defined in `servers.yaml`.
- `intent_classifier` to determine if a query relates to memory, tasks, or calendar.
- `task_manager` (renamed from `process_query` for clarity) to execute tool calls based on intent.
- `ChatOllama` (LangChain) for LLM interactions when no specific tool is identified.

The `main` function demonstrates the agent processing a list of predefined queries.
"""
import asyncio
import os
import json
from typing import Dict, Any, Optional
from contextlib import asynccontextmanager
from langchain_ollama import ChatOllama # LLM integration using LangChain
from langchain_core.prompts import ChatPromptTemplate # For structuring LLM prompts
from langchain_core.runnables import Runnable # For type hinting the chain

# Custom modules for agent logic
from agents.intent_classifier import classify_intent
from agents.tool_executor import execute_mcp_tool # Renamed from process_query
from utils.client_manager import ClientManager # Manages connections to MCP servers

from dotenv import load_dotenv

# Load environment variables (e.g., LLM_CHOICE, API keys if any client needs them directly)
load_dotenv()

class MCPAgent:
    """An agent that uses intent classification and MCP tools or an LLM to respond to queries."""

    def __init__(self, llm: ChatOllama, client_manager: ClientManager):
        """
        Initializes the MCPAgent.

        Args:
            llm: An initialized LangChain LLM (e.g., ChatOllama).
            client_manager: An initialized ClientManager instance that has loaded server configs.
        """
        self.llm = llm
        self.client_manager = client_manager
        # System prompt to guide the LLM when it's used for direct responses
        self.prompt_template = ChatPromptTemplate.from_messages([
            ("system", "You are an AI assistant. Provide clear and concise answers. If you don't know the answer, say so."),
            ("human", "{input}")
        ])
        # Create a LangChain runnable sequence (chain)
        self.chain: Runnable = self.prompt_template | self.llm

    @asynccontextmanager
    async def active_connections(self):
        """
        An async context manager to ensure MCP server connections are active during an operation
        and cleaned up afterwards.
        """
        print("Agent: Establishing connections to MCP servers...")
        await self.client_manager.connect_to_server()
        try:
            yield # Connections are active within this block
        finally:
            print("Agent: Cleaning up MCP server connections...")
            await self.client_manager.cleanup()

    async def run(self, query: str) -> str:
        """
        Processes a user query.

        It first classifies the intent of the query. If the intent matches a known tool
        (memory, task, calendar), it uses `execute_mcp_tool`. Otherwise, it uses the LLM
        to generate a direct response.

        Args:
            query: The user's query string.

        Returns:
            A string response, either from a tool or the LLM.
        """
        print(f"Agent: Processing query - '{query}'")
        try:
            # The active_connections context manager ensures servers are connected for this run
            async with self.active_connections():
                # Step 1: Classify the intent of the query
                print(f"Agent: Classifying intent for query: '{query}'")
                intent = classify_intent(query) # This is expected to be a synchronous function
                print(f"Agent: Classified intent as: {intent}")

                # Step 2: Based on intent, either call a tool or use the LLM
                tool_intents = [
                    "save_memory", "search_memories", "get_all_memories", 
                    "readTasks", "newTask", "markTaskAsDone", 
                    "getEvents"
                ]

                if intent in tool_intents:
                    print(f"Agent: Intent '{intent}' matches a tool. Executing tool...")
                    # `execute_mcp_tool` will use the client_manager to call the appropriate MCP server tool
                    result = await execute_mcp_tool(query, intent, self.client_manager)
                    # Ensure results are JSON serializable if they are complex types
                    return json.dumps(result) if isinstance(result, (list, dict)) else str(result)
                else:
                    print("Agent: Intent does not match a specific tool. Using LLM for a direct response...")
                    # Use the LangChain chain to invoke the LLM
                    response = await self.chain.ainvoke({"input": query})
                    return response.content # Assuming response.content holds the string output
        except Exception as e:
            print(f"Agent: Error processing query '{query}': {str(e)}")
            return f"Error: Could not process your query. Details: {str(e)}"

async def main():
    """Main function to set up and run the MCPAgent with example queries."""
    print("--- MCPAgent Demo Start ---")
    
    # Initialize the LLM (e.g., Ollama Llama3)
    # LLM_CHOICE can be set in .env, e.g., LLM_CHOICE=llama3
    llm_model_name = os.getenv("LLM_CHOICE", "llama3") 
    print(f"Initializing LLM: {llm_model_name}")
    llm = ChatOllama(model=llm_model_name)

    # Initialize ClientManager and load server configurations
    # This manager will be used by the agent to interact with MCP servers.
    print("Initializing ClientManager and loading server configurations...")
    client_manager = ClientManager()
    client_manager.load_servers("servers.yaml") # Loads URLs and API keys

    if not client_manager.clients:
        print("No MCP servers configured in servers.yaml. Agent may not have tool access. Exiting.")
        return

    # Create the agent instance
    agent = MCPAgent(llm=llm, client_manager=client_manager)
    print("MCPAgent initialized.")

    # Example queries to test the agent
    queries = [
        "Hello, how are you today?",
        "Save a new memory: I had a productive meeting about the new UI design this morning at 10 AM.",
        "What memories do I have about UI design?",
        "Can you show me all my memories?",
        "What are my current tasks?",
        "Please add a new task: Prepare slides for Friday's presentation.",
        "I finished preparing the slides, please mark that task as done.",
        "Do I have any calendar events scheduled for tomorrow?" # Assuming getEvents can be adapted or intent maps to it
    ]

    for query in queries:
        print(f"\nUser Query: {query}")
        result = await agent.run(query)
        print(f"Agent Result: {result}")
    
    print("\n--- MCPAgent Demo End ---")

if __name__ == "__main__":
    asyncio.run(main())