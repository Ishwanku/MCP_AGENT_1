"""
MCP Server for web crawling operations.

This server provides tools to crawl web pages, entire sites, and search for specific content
within web pages. It uses tools defined in the tools directory and exposes these
capabilities through the FastMCP protocol.
"""
import os
import sys
import asyncio

# Add the parent directory to the path so we can import from config
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from ..server.fastmcp import FastMCP
from ..core.config import CRAWLER_SERVER_PORT, CRAWLER_SERVER_API_KEY

# Define crawler-related tools
def crawl_page(data: dict) -> dict:
    """Crawl a single webpage.
    
    Args:
        data (dict): Dictionary containing 'url' and optional 'depth'.
    
    Returns:
        dict: Response with status and page content data.
    """
    url = data.get('url', '')
    depth = data.get('depth', 1)
    if not url:
        return {'status': 'error', 'message': 'No URL provided'}
    # Placeholder for actual crawling logic
    print(f"Crawling page: {url}, depth: {depth}")
    return {'status': 'success', 'data': {'url': url, 'title': 'Sample Page', 'content': f'Content of {url}'}}

def crawl_site(data: dict) -> dict:
    """Recursively crawl a website.
    
    Args:
        data (dict): Dictionary containing 'url', 'max_depth', and optional 'rate_limit'.
    
    Returns:
        dict: Response with status and list of crawled page contents.
    """
    url = data.get('url', '')
    max_depth = data.get('max_depth', 2)
    rate_limit = data.get('rate_limit', 1.0)
    if not url:
        return {'status': 'error', 'message': 'No URL provided'}
    # Placeholder for actual site crawling logic
    print(f"Crawling site: {url}, max depth: {max_depth}, rate limit: {rate_limit}")
    return {'status': 'success', 'data': [{'url': f"{url}/page{i}", 'title': f'Page {i}', 'content': f'Content of page {i}'} for i in range(3)]}

def search_page(data: dict) -> dict:
    """Search for text within a webpage.
    
    Args:
        data (dict): Dictionary containing 'url' and 'query'.
    
    Returns:
        dict: Response with status and matching snippets.
    """
    url = data.get('url', '')
    query = data.get('query', '')
    if not url or not query:
        return {'status': 'error', 'message': 'URL and query are required'}
    # Placeholder for actual search logic
    print(f"Searching page {url} for: {query}")
    return {'status': 'success', 'results': [f'Snippet 1 containing {query}', f'Snippet 2 containing {query}']}

# Initialize FastMCP server for Crawler Agent
crawler_server = FastMCP(name="Crawler Agent", port=CRAWLER_SERVER_PORT, api_key=CRAWLER_SERVER_API_KEY)

# Register crawler tools
crawler_server.register_tool('crawl_page', crawl_page)
crawler_server.register_tool('crawl_site', crawl_site)
crawler_server.register_tool('search_page', search_page)

if __name__ == "__main__":
    crawler_server.run()