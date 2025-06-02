from pydantic import BaseModel, Field, HttpUrl
from fastmcp import Tool
from typing import Optional, List
import aiohttp
from bs4 import BeautifulSoup
import asyncio
from mem0 import MemoryClient
import time

class CrawlPageInput(BaseModel):
    url: HttpUrl = Field(..., description="URL of the page to crawl")
    elements: List[str] = Field(
        default=["title", "p", "a"], 
        description="HTML elements to extract (e.g., title, p, a)"
    )

class CrawlSiteInput(BaseModel):
    url: HttpUrl = Field(..., description="Base URL to start crawling")
    max_depth: int = Field(default=2, ge=0, le=5, description="Maximum crawling depth")
    max_pages: int = Field(default=10, ge=1, le=100, description="Maximum pages to crawl")

class SearchPageInput(BaseModel):
    url: HttpUrl = Field(..., description="URL to search")
    query: str = Field(..., description="Keyword or phrase to search for")
    element: str = Field(default="p", description="HTML element to search within")

async def crawl_page(input_data: CrawlPageInput, context):
    async with aiohttp.ClientSession() as session:
        async with session.get(str(input_data.url)) as response:
            if response.status != 200:
                return {"error": f"Failed to fetch {input_data.url}: Status {response.status}"}
            html = await response.text()
    
    soup = BeautifulSoup(html, "html.parser")
    results = {}
    for element in input_data.elements:
        tags = soup.find_all(element)
        results[element] = [tag.get_text(strip=True) for tag in tags]
    
    # Store in Mem0
    memory_client = MemoryClient(api_key=context.get("MEM0_API_KEY"))
    memory_client.add(
        data={
            "url": str(input_data.url),
            "content": results,
            "timestamp": time.time()
        },
        user_id="crawler_user"
    )
    
    return {"url": str(input_data.url), "data": results}

async def crawl_site(input_data: CrawlSiteInput, context):
    visited = set()
    to_visit = [(str(input_data.url), 0)]  # (url, depth)
    results = []
    
    async with aiohttp.ClientSession() as session:
        while to_visit and len(visited) < input_data.max_pages:
            url, depth = to_visit.pop(0)
            if url in visited or depth > input_data.max_depth:
                continue
            
            visited.add(url)
            async with session.get(url) as response:
                if response.status != 200:
                    continue
                html = await response.text()
            
            soup = BeautifulSoup(html, "html.parser")
            page_data = {
                "url": url,
                "title": soup.title.get_text(strip=True) if soup.title else "",
                "text": [p.get_text(strip=True) for p in soup.find_all("p")]
            }
            results.append(page_data)
            
            # Store in Mem0
            memory_client = MemoryClient(api_key=context.get("MEM0_API_KEY"))
            memory_client.add(
                data=page_data,
                user_id="crawler_user"
            )
            
            # Find links to follow
            if depth < input_data.max_depth:
                for a in soup.find_all("a", href=True):
                    link = a["href"]
                    if link.startswith("/"):
                        link = str(input_data.url).rstrip("/") + link
                    if link.startswith(str(input_data.url)) and link not in visited:
                        to_visit.append((link, depth + 1))
            
            await asyncio.sleep(1)  # Respectful crawling delay
    
    return {"crawled_pages": len(results), "data": results}

async def search_page(input_data: SearchPageInput, context):
    async with aiohttp.ClientSession() as session:
        async with session.get(str(input_data.url)) as response:
            if response.status != 200:
                return {"error": f"Failed to fetch {input_data.url}: Status {response.status}"}
            html = await response.text()
    
    soup = BeautifulSoup(html, "html.parser")
    tags = soup.find_all(input_data.element)
    matches = [
        tag.get_text(strip=True) 
        for tag in tags 
        if input_data.query.lower() in tag.get_text(strip=True).lower()
    ]
    
    # Store in Mem0
    memory_client = MemoryClient(api_key=context.get("MEM0_API_KEY"))
    memory_client.add(
        data={
            "url": str(input_data.url),
            "query": input_data.query,
            "matches": matches,
            "timestamp": time.time()
        },
        user_id="crawler_user"
    )
    
    return {"url": str(input_data.url), "query": input_data.query, "matches": matches}

crawl_page_tool = Tool(
    name="crawl_page",
    description="Crawl a single webpage and extract specified HTML elements",
    input_schema=CrawlPageInput,
    handler=crawl_page
)

crawl_site_tool = Tool(
    name="crawl_site",
    description="Recursively crawl a website to a specified depth",
    input_schema=CrawlSiteInput,
    handler=crawl_site
)

search_page_tool = Tool(
    name="search_page",
    description="Search a webpage for text matching a query within specified elements",
    input_schema=SearchPageInput,
    handler=search_page
)