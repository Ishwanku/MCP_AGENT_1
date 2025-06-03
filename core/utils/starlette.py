"""
Starlette utilities for FastMCP server implementation.

This module provides utilities for creating Starlette applications
that wrap FastMCP servers with authentication and other middleware.
"""

from typing import Optional
from starlette.applications import Starlette
from starlette.middleware import Middleware
from starlette.middleware.authentication import AuthenticationMiddleware
from starlette.middleware.cors import CORSMiddleware
from starlette.routing import Route
from starlette.responses import JSONResponse
from starlette.authentication import SimpleUser, AuthCredentials, AuthenticationBackend
from starlette.requests import Request


class APIKeyAuthBackend(AuthenticationBackend):
    """Authentication backend that validates API keys.
    
    This backend checks for an X-API-Key header and validates it against
    a configured API key.
    """
    
    def __init__(self, api_key: str):
        """Initialize the authentication backend.
        
        Args:
            api_key: The API key to validate against.
        """
        self.api_key = api_key

    async def authenticate(self, request: Request):
        """Authenticate a request using the API key.
        
        Args:
            request: The request to authenticate.
            
        Returns:
            A tuple of (AuthCredentials, SimpleUser) if authentication succeeds,
            or None if it fails.
        """
        if "X-API-Key" not in request.headers:
            return None
            
        api_key = request.headers["X-API-Key"]
        if api_key != self.api_key:
            return None
            
        return AuthCredentials(["authenticated"]), SimpleUser("api_user")


def create_starlette_app(mcp_server, api_key: Optional[str] = None, debug: bool = False) -> Starlette:
    """Create a Starlette application for a FastMCP server.
    
    Args:
        mcp_server: The FastMCP server to wrap.
        api_key: Optional API key for authentication.
        debug: Whether to enable debug mode.
        
    Returns:
        A configured Starlette application.
    """
    # Create middleware stack
    middleware = [
        Middleware(
            CORSMiddleware,
            allow_origins=["*"],
            allow_methods=["*"],
            allow_headers=["*"],
        )
    ]
    
    # Add authentication if API key is provided
    if api_key:
        middleware.append(
            Middleware(
                AuthenticationMiddleware,
                backend=APIKeyAuthBackend(api_key)
            )
        )
    
    # Create routes
    routes = [
        Route("/sse", mcp_server.sse_endpoint),
        Route("/tools/{tool_name}", mcp_server.tool_endpoint, methods=["POST"]),
    ]
    
    # Create and return the application
    return Starlette(
        debug=debug,
        routes=routes,
        middleware=middleware
    )