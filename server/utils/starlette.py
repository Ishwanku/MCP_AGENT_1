"""
Utility module for creating a Starlette application to host an MCP server.

This module provides a function `create_starlette_app` that sets up
a Starlette application with routes for Server-Sent Events (SSE) communication
and message handling, suitable for a FastMCP server.
It includes API key authentication for the SSE endpoint.
"""
from mcp.server import Server
from mcp.server.sse import SseServerTransport
from starlette.applications import Starlette
from starlette.responses import PlainTextResponse
from starlette.routing import Route
from starlette.types import ASGIApp, Receive, Scope, Send


class AuthMiddleware:
    def __init__(self, app: ASGIApp, api_key: str):
        self.app = app
        self.api_key = f"Bearer {api_key}"

    async def __call__(self, scope: Scope, receive: Receive, send: Send):
        """ASGI middleware to check for API key in Authorization header."""
        if scope["type"] not in ("http", "websocket"):
            await self.app(scope, receive, send)
            return

        auth_header = None
        for name, value in scope.get("headers", []):
            if name.decode('latin-1').lower() == 'authorization':
                auth_header = value.decode('latin-1')
                break

        if auth_header != self.api_key:
            # If auth fails, send a 401 response and do not proceed to the wrapped app.
            response = PlainTextResponse("Unauthorized", status_code=401)
            await response(scope, receive, send)
            return

        await self.app(scope, receive, send)


def create_starlette_app(mcp_server: Server, *, api_key: str, debug: bool = False) -> Starlette:
    """
    Creates and configures a Starlette application for an MCP server.

    The application includes:
    - An SSE endpoint (`/sse`) for real-time communication.
    - A POST endpoint (`/messages/`) for message submission.
    Both are protected by an API key via AuthMiddleware.

    Args:
        mcp_server: The MCP Server instance to be run by this Starlette app.
        api_key: The API key required for authorizing access.
        debug: A boolean flag to enable Starlette's debug mode (default: False).

    Returns:
        A configured Starlette application instance.
    """
    # SseServerTransport expects the prefix for POST messages.
    # The client will POST to /messages/?session_id=...
    # Starlette's Route will match /messages/ for this.
    sse_transport = SseServerTransport("/messages/")

    async def actual_handle_sse(scope: Scope, receive: Receive, send: Send):
        """Handles the GET /sse request to establish SSE connection and run MCP server."""
        async with sse_transport.connect_sse(scope, receive, send) as (read_stream, write_stream):
            await mcp_server.run(read_stream, write_stream, mcp_server.create_initialization_options())

    async def actual_handle_messages(scope: Scope, receive: Receive, send: Send):
        """Handles the POST /messages/ request to process incoming MCP messages."""
        await sse_transport.handle_post_message(scope, receive, send)

    # Wrap the actual handlers with authentication
    authed_handle_sse = AuthMiddleware(actual_handle_sse, api_key=api_key)
    authed_handle_messages = AuthMiddleware(actual_handle_messages, api_key=api_key)

    return Starlette(
        debug=debug,
        routes=[
            Route("/sse", endpoint=authed_handle_sse, methods=["GET"]),
            # The client POSTs to /messages/?session_id=...
            # Starlette's Route should match the base path /messages/
            # The SseServerTransport was initialized with "/messages/" and expects
            # its handle_post_message to be called for scopes matching this path.
            Route("/messages/", endpoint=authed_handle_messages, methods=["POST"]),
        ],
    )