import asyncio

from typing import Dict, Any, Callable, Optional

from fastapi import FastAPI, HTTPException, Request, Response
from fastapi.responses import StreamingResponse
from starlette.background import BackgroundTask
import uvicorn

from pydantic import BaseModel


class ToolRequest(BaseModel):
    """Model for tool execution requests."""
    data: Dict[str, Any]


class FastMCP:
    """A server implementation for MCP Agent providing SSE and tool execution endpoints."""

    def __init__(self, name: str, port: int, api_key: str, tools: Dict[str, Callable] = None):
        """Initialize the FastMCP server.

        Args:
            name (str): Name of the server/agent.
            port (int): Port to run the server on.
            api_key (str): API key for authentication.
            tools (Dict[str, Callable], optional): Dictionary of tool names to their callable functions.
        """
        self.name = name
        self.port = port
        self.api_key = api_key
        self.tools = tools or {}
        self.app = FastAPI(title=f"MCP Agent - {name}")
        self._setup_routes()

    def _setup_routes(self) -> None:
        """Set up the FastAPI routes for SSE and tool execution."""
        @self.app.get("/sse")
        async def sse_endpoint(request: Request):
            """Server-Sent Events endpoint for real-time updates."""
            if request.headers.get("X-API-Key") != self.api_key:
                raise HTTPException(status_code=401, detail="Invalid API key")
            return StreamingResponse(
                self._sse_stream(request),
                media_type="text/event-stream",
                background=BackgroundTask(self._cleanup_sse, request)
            )

        @self.app.post("/tools/{tool_name}")
        async def execute_tool(tool_name: str, request: Request, tool_request: ToolRequest):
            """Execute a specific tool with the provided data."""
            if request.headers.get("X-API-Key") != self.api_key:
                raise HTTPException(status_code=401, detail="Invalid API key")
            if tool_name not in self.tools:
                raise HTTPException(status_code=404, detail=f"Tool {tool_name} not found")
            try:
                result = await asyncio.to_thread(self.tools[tool_name], tool_request.data)
                return {"status": "success", "data": result}
            except Exception as e:
                raise HTTPException(status_code=500, detail=f"Error executing tool {tool_name}: {str(e)}")

    async def _sse_stream(self, request: Request):
        """Stream SSE events to the client."""
        while True:
            if await request.is_disconnected():
                break
            # Placeholder for sending updates; can be customized based on agent logic
            yield f"event: update\ndata: {{\"message\": \"Update from {self.name}\"}}\n\n"
            await asyncio.sleep(5)  # Send update every 5 seconds

    async def _cleanup_sse(self, request: Request):
        """Cleanup when SSE connection is closed."""
        if await request.is_disconnected():
            print(f"SSE connection closed for {self.name}")

    def run(self) -> None:
        """Run the FastMCP server using Uvicorn."""
        print(f"Starting {self.name} server on port {self.port}")
        uvicorn.run(self.app, host="0.0.0.0", port=self.port, log_level="info")

    def register_tool(self, name: str, func: Callable) -> None:
        """Register a new tool with the server.

        Args:
            name (str): Name of the tool.
            func (Callable): Function to execute for the tool.
        """
        self.tools[name] = func
        print(f"Registered tool '{name}' for {self.name}")
