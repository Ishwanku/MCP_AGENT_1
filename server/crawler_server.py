from fastmcp.server import MCPServer
from tools.crawler_tools import crawl_page_tool, crawl_site_tool, search_page_tool
from dotenv import load_dotenv
import os

load_dotenv()

async def start_crawler_server():
    server = MCPServer(
        host="localhost",
        port=3005,
        tools=[crawl_page_tool, crawl_site_tool, search_page_tool],
        context={
            "MEM0_API_KEY": os.getenv("MEM0_API_KEY")
        }
    )
    await server.start()

if __name__ == "__main__":
    import asyncio
    asyncio.run(start_crawler_server())