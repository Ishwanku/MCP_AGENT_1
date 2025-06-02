import asyncio
import os
import json
from typing import Dict, Any, Optional
from contextlib import asynccontextmanager
from langchain_ollama import ChatOllama
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import Runnable

from agents.intent_classifier import classify_intent
from agents.tool_executor import execute_mcp_tool
from utils.client_manager import ClientManager

from dotenv import load_dotenv

load_dotenv()

class MCPAgent:
    """An agent that uses intent classification and MCP tools or an LLM to respond to queries."""

    def __init__(self, llm: ChatOllama, client_manager: ClientManager):
        self.llm = llm
        self.client_manager = client_manager
        self.prompt_template = ChatPromptTemplate.from_messages([
            ("system", "You are an AI assistant. Provide clear and concise answers. If you don't know the answer, say so."),
            ("human", "{input}")
        ])
        self.chain: Runnable = self.prompt_template | self.llm

    @asynccontextmanager
    async def active_connections(self):
        print("Agent: Establishing connections to MCP servers...")
        await self.client_manager.connect_to_server()
        try:
            yield
        finally:
            print("Agent: Cleaning up MCP server connections...")
            await self.client_manager.cleanup()

    async def run(self, query: str) -> str:
        print(f"Agent: Processing query - '{query}'")
        async with self.active_connections():
            try:
                print(f"Agent: Classifying intent for query: '{query}'")
                intent = classify_intent(query)
                print(f"Agent: Classified intent as: {intent}")

                tool_intents = [
                    "save_memory", "search_memories", "get_all_memories",
                    "readTasks", "newTask", "markTaskAsDone",
                    "getEvents"
                ]

                if intent in tool_intents:
                    print(f"Agent: Intent '{intent}' matches a tool. Executing tool...")
                    result = await execute_mcp_tool(query, intent, self.client_manager)
                    return json.dumps(result) if isinstance(result, (list, dict)) else str(result)
                else:
                    print("Agent: Intent does not match a specific tool. Using LLM for a direct response...")
                    response = await self.chain.ainvoke({"input": query})
                    print(f"Agent: LLM response: {response.content}")
                    return response.content
            except Exception as e:
                print(f"Agent: Error processing query '{query}': {str(e)}")
                return f"Error: Could not process your query. Details: {str(e)}"

async def main():
    print("--- MCPAgent Demo Start ---")
    
    llm_model_name = os.getenv("LLM_CHOICE", "qwen2:7b-instruct")
    print(f"Initializing LLM: {llm_model_name}")
    llm = ChatOllama(model=llm_model_name, base_url="http://localhost:11434")
    
    print("Initializing ClientManager and loading server configurations...")
    client_manager = ClientManager()
    client_manager.load_servers("servers.yaml")
    
    if not client_manager.clients:
        print("No MCP servers configured in servers.yaml. Agent may not have tool access. Exiting.")
        return

    agent = MCPAgent(llm=llm, client_manager=client_manager)
    print("MCPAgent initialized.")

    queries = [
        "Hello, how are you today?",
        "Save a new memory: I had a productive meeting about the new UI design this morning at 10 AM.",
        "What memories do I have about UI design?",
        "Can you show me all my memories?",
        "What are my current tasks?",
        "Please add a new task: Prepare slides for Friday's presentation.",
        "I finished preparing the slides, please mark that task as done.",
        "Do I have any calendar events scheduled for tomorrow?"
    ]

    for query in queries:
        print(f"\nUser Query: {query}")
        result = await agent.run(query)
        print(f"Agent Result: {result}")
        if result is None:
            print(f"Debug: 'run' method returned None for query '{query}'")
            
    print("\n--- MCPAgent Demo End ---")

if __name__ == "__main__":
    asyncio.run(main())