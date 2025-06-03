"""
MCP Client for tool discovery and interaction.
"""
import aiohttp
from typing import List, Dict, Any
from dataclasses import dataclass

@dataclass
class Tool:
    name: str
    description: str
    input_schema: Dict[str, Any]

class MCPClient:
    def __init__(self, name: str, version: str):
        self.name = name
        self.version = version
        self.session = None
        self.base_url = None

    async def connect(self, server_url: str):
        self.base_url = server_url.rstrip('/')
        self.session = aiohttp.ClientSession()

    async def list_tools(self) -> List[Tool]:
        async with self.session.get(f"{self.base_url}/tools") as response:
            tools_data = await response.json()
            return [Tool(**tool) for tool in tools_data]

    async def close(self):
        if self.session:
            await self.session.close() 