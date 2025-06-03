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
from typing import List
import aiohttp
from bs4 import BeautifulSoup
import asyncio
import json
import time
import os

class CrawlPageInput(BaseModel):
    url: HttpUrl = Field(..., description="URL of the page to crawl")
    elements: List[str] = Field(
        default=["title", "p", "a"],
        description="HTML elements to extract"
    )

class CrawlSiteInput(BaseModel):
    url: HttpUrl = Field(..., description="Base URL to start crawling")
    max_depth: int = Field(default=2, ge=0, le=5, description="Maximum crawling depth")
    max_pages: int = Field(default=10, ge=1, le=100, description="Maximum pages to crawl")

class SearchPageInput(BaseModel):
    url: HttpUrl = Field(..., description="URL to search")
    query: str = Field(..., description="Keyword or phrase to search for")
    element: str = Field(default="p", description="HTML element to search within")

def save_to_json(data):
    """Save crawler results to a local JSON file."""
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

async def crawl_page(input_data: CrawlPageInput, context):
    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(str(input_data.url)) as response:
                if response.status != 200:
                    return {"error": f"Failed to fetch {input_data.url}: Status {response.status}"}
                html = await response.text()
        except Exception as e:
            return {"error": f"Failed to fetch {input_data.url}: {e}"}
    
    soup = BeautifulSoup(html, "html.parser")
    results = {}
    for element in input_data.elements:
        tags = soup.find_all(element)
        results[element] = [tag.get_text(strip=True) for tag in tags]
    
    try:
        save_to_json({
            "url": str(input_data.url),
            "content": results,
            "timestamp": time.time(),
            "type": "crawl_page"
        })
    except Exception as e:
        print(f"Error saving crawl_page data: {e}")
    
    return {"url": str(input_data.url), "data": results}

async def crawl_site(input_data: CrawlSiteInput, context):
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
            
            soup = BeautifulSoup(html, "html.parser")
            page_data = {
                "url": url,
                "title": soup.title.get_text(strip=True) if soup.title else "",
                "text": [p.get_text(strip=True) for p in soup.find_all("p")]
            }
            results.append(page_data)
            
            try:
                save_to_json({
                    "url": url,
                    "content": page_data,
                    "timestamp": time.time(),
                    "type": "crawl_site"
                })
            except Exception as e:
                print(f"Error saving crawl_site data: {e}")
            
            if depth < input_data.max_depth:
                for a in soup.find_all("a", href=True):
                    link = a["href"]
                    if link.startswith("/"):
                        link = str(input_data.url).rstrip("/") + link
                    if link.startswith(str(input_data.url)) and link not in visited:
                        to_visit.append((link, depth + 1))
            
            await asyncio.sleep(1)  # Rate limit
    
    return {"crawled_pages": len(results), "data": results}

async def search_page(input_data: SearchPageInput, context):
    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(str(input_data.url)) as response:
                if response.status != 200:
                    return {"error": f"Failed to fetch {input_data.url}: Status {response.status}"}
                html = await response.text()
        except Exception as e:
            return {"error": f"Failed to fetch {input_data.url}: {e}"}
    
    soup = BeautifulSoup(html, "html.parser")
    tags = soup.find_all(input_data.element)
    matches = [
        tag.get_text(strip=True)
        for tag in tags
        if input_data.query.lower() in tag.get_text(strip=True).lower()
    ]
    
    try:
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