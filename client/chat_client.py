import asyncio
from fastmcp.client import MCPClient
from llm_client import LLMClient
import json
from dotenv import load_dotenv
import os

load_dotenv()

class ChatClient:
    def __init__(self, server_url, client_name="crawler-client"):
        self.mcp_client = MCPClient(name=client_name, version="1.0.0")
        self.server_url = server_url
        self.llm_client = LLMClient()
        self.chat_history = []
        self.tools = []

    async def initialize(self):
        await self.mcp_client.connect(self.server_url)
        self.tools = await self.list_tools()
        print(f"Connected to MCP server {self.server_url} with {len(self.tools)} tools")

    async def list_tools(self):
        tools = await self.mcp_client.list_tools()
        return [
            {
                "name": tool.name,
                "description": tool.description,
                "parameters": {
                    "type": tool.input_schema.get("type"),
                    "properties": tool.input_schema.get("properties"),
                    "required": tool.input_schema.get("required", [])
                }
            }
            for tool in tools
        ]

    async def chat_loop(self):
        while True:
            user_input = input("You: ")
            if user_input.lower() == "exit":
                break

            self.chat_history.append({"role": "user", "content": user_input})

            response = await self.llm_client.chat(
                messages=self.chat_history,
                tools=self.tools
            )

            if response.get("error"):
                print(f"Error: {response['error']}")
                continue

            if response.get("tool_calls"):
                for tool_call in response["tool_calls"]:
                    tool_name = tool_call["function"]["name"]
                    tool_args = tool_call["function"]["arguments"]
                    print(f"Calling tool: {tool_name} with args: {tool_args}")
                    
                    tool_result = await self.mcp_client.call_tool(
                        name=tool_name, arguments=tool_args
                    )
                    self.chat_history.append(
                        {"role": "tool", "content": json.dumps(tool_result)}
                    )
                    await self.chat_loop()  # Recurse to process tool result
                    return

            response_text = response["message"]["content"]
            self.chat_history.append({"role": "assistant", "content": response_text})
            print(f"AI: {response_text}")

if __name__ == "__main__":
    client = ChatClient(server_url="http://localhost:3005")
    asyncio.run(client.initialize())
    asyncio.run(client.chat_loop())