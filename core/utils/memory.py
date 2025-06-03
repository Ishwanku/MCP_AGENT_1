"""
Memory utilities for MCP Agent PoC.

This module provides utilities for working with the Mem0 memory system,
including client initialization and management.
"""

import os
from typing import Optional
from mem0 import Mem0Client


# Global Mem0 client instance
_mem0_client: Optional[Mem0Client] = None


def get_mem0_client() -> Mem0Client:
    """Get or create a Mem0 client instance.
    
    This function implements a singleton pattern for the Mem0 client.
    It creates a new client if one doesn't exist, or returns the existing one.
    
    Returns:
        A configured Mem0 client instance.
    """
    global _mem0_client
    
    if _mem0_client is None:
        # Get configuration from environment variables
        api_key = os.getenv("MEM0_API_KEY")
        if not api_key:
            raise ValueError("MEM0_API_KEY environment variable is required")
            
        # Initialize the client
        _mem0_client = Mem0Client(api_key=api_key)
        
    return _mem0_client