import asyncio
import aiohttp
from fastmcp.client import MCPClient

async def connect_sse(url, client_name="crawler-client", version="1.0.0"):
    client = MCPClient(name=client_name, version=version)
    await client.connect(url)
    async with aiohttp.ClientSession() as session:
        async with session.get(f"{url}/sse") as response:
            print("Connected to MCP crawler server via SSE")
            async for line in response.content:
                if line.startswith(b"data:"):
                    event = line.decode("utf-8")[5:].strip()
                    print(f"SSE event: {event}")
                    # Process event (e.g., crawling progress)
    return client

if __name__ == "__main__":
    asyncio.run(connect_sse("http://localhost:3005"))