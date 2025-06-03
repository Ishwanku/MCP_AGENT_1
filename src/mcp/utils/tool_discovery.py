from mcp.server.fastmcp import MCPClient
import json
import asyncio

async def list_tools(server_url, client_name="crawler-client", version="1.0.0"):
    client = MCPClient(name=client_name, version=version)
    await client.connect(server_url)
    tools = await client.list_tools()
    formatted_tools = [
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
    with open("client/tools.json", "w") as f:
        json.dump(formatted_tools, f, indent=2)
    return formatted_tools

if __name__ == "__main__":
    tools = asyncio.run(list_tools("http://localhost:3005"))
    print("Available crawling tools:", tools)