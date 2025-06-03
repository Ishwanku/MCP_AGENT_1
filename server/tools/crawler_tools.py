"""
Web Crawler Tools for MCP Server.

This module defines tools for web crawling operations including crawling single pages,
recursively crawling entire sites, and searching for specific content within pages.
These tools are used by the crawler server to provide web content extraction capabilities.
"""
from pydantic import BaseModel, Field, HttpUrl
try:
    from fastmcp.tools import Tool
except ImportError:
    try:
        from mcp import Tool
    except ImportError:
        class Tool(BaseModel):
            name: str
            description: str
            inputSchema: type[BaseModel]
            fn: callable
            parameters: dict

            class Config:
                arbitrary_types_allowed = True

            @classmethod
            def from_handler(cls, name: str, description: str, input_schema: type[BaseModel], handler: callable):
                return cls(
                    name=name,
                    description=description,
                    inputSchema=input_schema,
                    fn=handler,
                    parameters=input_schema.schema()
                )
            
            async def run(self, input_data: BaseModel, **kwargs):
                """
                Run the tool with the given input data and optional context.
                
                Args:
                    input_data: The input data for the tool
                    **kwargs: Additional arguments including context
                
                Returns:
                    The result of running the tool
                """
                context = kwargs.get('context', {})
                return await self.fn(input_data, context)

from typing import List, Optional, Dict, Any
import aiohttp
from bs4 import BeautifulSoup
import asyncio
import json
import time
import os

# Define input models for the crawler tools using Pydantic for validation
class CrawlPageInput(BaseModel):
    url: HttpUrl = Field(..., description="URL of the page to crawl")
    elements: List[str] = Field(
        default=["title", "p", "a"],
        description="HTML elements to extract from the page"
    )

class CrawlSiteInput(BaseModel):
    url: HttpUrl = Field(..., description="Base URL to start crawling")
    max_depth: int = Field(default=2, ge=0, le=5, description="Maximum crawling depth for recursive site crawling")
    max_pages: int = Field(default=10, ge=1, le=100, description="Maximum number of pages to crawl")

class SearchPageInput(BaseModel):
    url: HttpUrl = Field(..., description="URL to search")
    query: str = Field(..., description="Keyword or phrase to search for within the page")
    element: str = Field(default="p", description="HTML element to search within")

def save_to_json(data):
    """
    Save crawler results to a local JSON file for persistence.
    
    Args:
        data: The data to save to the JSON file.
    """
    file_path = "crawler_data.json"
    try:
        if os.path.exists(file_path):
            with open(file_path, "r", encoding="utf-8") as f:
                existing_data = json.load(f)
        else:
            existing_data = []
        existing_data.append(data)
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(existing_data, f, indent=2, ensure_ascii=False)
    except Exception as e:
        print(f"Error saving to JSON: {e}")

async def crawl_page(input_data: CrawlPageInput, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    Crawls a single webpage and extracts content from specified HTML elements.
    
    Args:
        input_data: A CrawlPageInput object containing the URL and elements to extract.
        context: Additional context for the tool (optional).
        
    Returns:
        A dictionary containing the URL and extracted data, or an error message if the operation fails.
    """
    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(str(input_data.url)) as response:
                if response.status != 200:
                    return {"error": f"Failed to fetch {input_data.url}: Status {response.status}"}
                html = await response.text()
        except Exception as e:
            return {"error": f"Failed to fetch {input_data.url}: {e}"}
    
    # Parse the HTML content using BeautifulSoup for easy DOM traversal
    soup = BeautifulSoup(html, "html.parser")
    results = {}
    for element in input_data.elements:
        tags = soup.find_all(element)
        results[element] = [tag.get_text(strip=True) for tag in tags]
    
    try:
        # Save the crawled data to a JSON file for persistence
        save_to_json({
            "url": str(input_data.url),
            "content": results,
            "timestamp": time.time(),
            "type": "crawl_page"
        })
    except Exception as e:
        print(f"Error saving crawl_page data: {e}")
    
    return {"url": str(input_data.url), "data": results}

async def crawl_site(input_data: CrawlSiteInput, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    Recursively crawls a website starting from a base URL up to a specified depth and page limit.
    
    Args:
        input_data: A CrawlSiteInput object containing the base URL, max depth, and max pages.
        context: Additional context for the tool (optional).
        
    Returns:
        A dictionary containing the number of crawled pages and the extracted data for each page.
    """
    visited = set()
    to_visit = [(str(input_data.url), 0)]  # (url, depth)
    results = []
    
    async with aiohttp.ClientSession() as session:
        while to_visit and len(results) < input_data.max_pages:
            url, depth = to_visit.pop(0)
            if url in visited or depth > input_data.max_depth:
                continue
            
            visited.add(url)
            try:
                async with session.get(url) as response:
                    if response.status != 200:
                        continue
                    html = await response.text()
            except Exception as e:
                print(f"Error fetching {url}: {e}")
                continue
            
            # Parse the HTML content using BeautifulSoup
            soup = BeautifulSoup(html, "html.parser")
            page_data = {
                "url": url,
                "title": soup.title.get_text(strip=True) if soup.title else "",
                "text": [p.get_text(strip=True) for p in soup.find_all("p")]
            }
            results.append(page_data)
            
            try:
                # Save the crawled data to a JSON file for persistence
                save_to_json({
                    "url": url,
                    "content": page_data,
                    "timestamp": time.time(),
                    "type": "crawl_site"
                })
            except Exception as e:
                print(f"Error saving crawl_site data: {e}")
            
            if depth < input_data.max_depth:
                # Find all links on the page for recursive crawling
                for a in soup.find_all("a", href=True):
                    link = a["href"]
                    if link.startswith("/"):
                        link = str(input_data.url).rstrip("/") + link
                    if link.startswith(str(input_data.url)) and link not in visited:
                        to_visit.append((link, depth + 1))
            
            # Rate limit to avoid overwhelming the target server
            await asyncio.sleep(1)
    
    return {"crawled_pages": len(results), "data": results}

async def search_page(input_data: SearchPageInput, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    Searches a webpage for text matching a query within specified HTML elements.
    
    Args:
        input_data: A SearchPageInput object containing the URL, search query, and element to search within.
        context: Additional context for the tool (optional).
        
    Returns:
        A dictionary containing the URL, search query, and matching text snippets, or an error if the operation fails.
    """
    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(str(input_data.url)) as response:
                if response.status != 200:
                    return {"error": f"Failed to fetch {input_data.url}: Status {response.status}"}
                html = await response.text()
        except Exception as e:
            return {"error": f"Failed to fetch {input_data.url}: {e}"}
    
    # Parse the HTML content using BeautifulSoup
    soup = BeautifulSoup(html, "html.parser")
    tags = soup.find_all(input_data.element)
    # Search for the query text within the specified elements (case-insensitive)
    matches = [
        tag.get_text(strip=True)
        for tag in tags
        if input_data.query.lower() in tag.get_text(strip=True).lower()
    ]
    
    try:
        # Save the search results to a JSON file for persistence
        save_to_json({
            "url": str(input_data.url),
            "query": input_data.query,
            "matches": matches,
            "timestamp": time.time(),
            "type": "search_page"
        })
    except Exception as e:
        print(f"Error saving search_page data: {e}")
    
    return {"url": str(input_data.url), "query": input_data.query, "matches": matches}

# Define the crawler tools for use in the MCP server
crawl_page_tool = Tool(
    name="crawl_page",
    description="Crawl a single webpage and extract specified HTML elements",
    inputSchema=CrawlPageInput,
    fn=crawl_page,
    parameters=CrawlPageInput.schema()
)

crawl_site_tool = Tool(
    name="crawl_site",
    description="Recursively crawl a website to a specified depth",
    inputSchema=CrawlSiteInput,
    fn=crawl_site,
    parameters=CrawlSiteInput.schema()
)

search_page_tool = Tool(
    name="search_page",
    description="Search a webpage for text matching a query within specified elements",
    inputSchema=SearchPageInput,
    fn=search_page,
    parameters=SearchPageInput.schema()
)