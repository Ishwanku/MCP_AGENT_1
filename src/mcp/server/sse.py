"""Server-Sent Events (SSE) client implementation."""
import asyncio
from contextlib import asynccontextmanager
from typing import AsyncGenerator, Dict, Any, Tuple

@asynccontextmanager
async def sse_client(url: str, headers: Dict[str, str] = None) -> AsyncGenerator[Tuple[asyncio.StreamReader, asyncio.StreamWriter], None]:
    """
    Create an SSE client connection.
    
    Args:
        url: The SSE endpoint URL
        headers: Optional headers for the connection
        
    Yields:
        A tuple of (reader, writer) for the SSE connection
    """
    reader, writer = await asyncio.open_connection(
        host=url.split("://")[1].split(":")[0],
        port=int(url.split(":")[-1].split("/")[0])
    )
    
    # Send HTTP request
    request = f"GET {url.split('://')[1].split('/', 1)[1]} HTTP/1.1\r\n"
    request += f"Host: {url.split('://')[1].split(':')[0]}\r\n"
    request += "Accept: text/event-stream\r\n"
    request += "Cache-Control: no-cache\r\n"
    
    if headers:
        for key, value in headers.items():
            request += f"{key}: {value}\r\n"
    
    request += "\r\n"
    writer.write(request.encode())
    await writer.drain()
    
    try:
        yield reader, writer
    finally:
        writer.close()
        await writer.wait_closed() 