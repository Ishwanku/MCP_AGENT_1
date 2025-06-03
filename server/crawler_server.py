from mcp.server.fastmcp import FastMCP
from tools.crawler_tools import crawl_page_tool, crawl_site_tool, search_page_tool
import uvicorn
from utils.starlette import create_starlette_app

async def start_crawler_server():
    server = FastMCP(
        name="Crawler",
        host="localhost",
        port=3005,
        tools=[crawl_page_tool, crawl_site_tool, search_page_tool],
        context={}
    )
    starlette_app = create_starlette_app(server._mcp_server, api_key="secret-key4", debug=True)
    uvicorn.run(starlette_app, host="localhost", port=3005)

if __name__ == "__main__":
    import asyncio
    asyncio.run(start_crawler_server())