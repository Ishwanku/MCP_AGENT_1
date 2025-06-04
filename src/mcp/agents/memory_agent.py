"""
LLM-enhanced Memory Agent for the MCP system.

This agent provides memory storage and retrieval capabilities with semantic search
using LLM embeddings and vector storage.
"""

import json
from typing import Any, Dict, List, Optional
from datetime import datetime
from qdrant_client import QdrantClient
from qdrant_client.http import models
from ..core.config import settings
from ..utils.llm_utils import get_embeddings, summarize_text

class MemoryAgent:
    """Memory Agent with LLM-enhanced capabilities."""

    def __init__(self):
        """Initialize the Memory Agent with Qdrant client and collection."""
        self.client = QdrantClient(
            url=settings.QDRANT_URL,
            api_key=settings.QDRANT_API_KEY
        )
        self.collection_name = "memories"
        self._ensure_collection()

    def _ensure_collection(self):
        """Ensure the Qdrant collection exists with proper configuration."""
        collections = self.client.get_collections().collections
        collection_names = [collection.name for collection in collections]

        if self.collection_name not in collection_names:
            self.client.create_collection(
                collection_name=self.collection_name,
                vectors_config=models.VectorParams(
                    size=1536,  # OpenAI embedding dimension
                    distance=models.Distance.COSINE
                )
            )

    async def store_memory(
        self,
        content: str,
        metadata: Optional[Dict[str, Any]] = None,
        generate_summary: bool = True
    ) -> Dict[str, Any]:
        """
        Store a memory with optional metadata and summary.

        Args:
            content: The memory content to store.
            metadata: Optional metadata to store with the memory.
            generate_summary: Whether to generate a summary using LLM.

        Returns:
            Dictionary containing the stored memory information.
        """
        # Generate embeddings for the content
        embeddings = await get_embeddings(content)
        
        # Generate summary if requested
        summary = None
        if generate_summary:
            summary = await summarize_text(content)

        # Prepare metadata
        memory_metadata = {
            "timestamp": datetime.utcnow().isoformat(),
            "content": content,
            "summary": summary,
            **(metadata or {})
        }

        # Store in Qdrant
        point_id = self.client.upsert(
            collection_name=self.collection_name,
            points=[
                models.PointStruct(
                    id=hash(content),  # Simple hash as ID
                    vector=embeddings[0],
                    payload=memory_metadata
                )
            ]
        )

        return {
            "id": point_id,
            "metadata": memory_metadata
        }

    async def search_memories(
        self,
        query: str,
        limit: int = 5,
        score_threshold: float = 0.7
    ) -> List[Dict[str, Any]]:
        """
        Search memories using semantic similarity.

        Args:
            query: The search query.
            limit: Maximum number of results to return.
            score_threshold: Minimum similarity score threshold.

        Returns:
            List of matching memories with their metadata.
        """
        # Generate embeddings for the query
        query_embedding = await get_embeddings(query)

        # Search in Qdrant
        search_result = self.client.search(
            collection_name=self.collection_name,
            query_vector=query_embedding[0],
            limit=limit,
            score_threshold=score_threshold
        )

        return [
            {
                "id": hit.id,
                "score": hit.score,
                "metadata": hit.payload
            }
            for hit in search_result
        ]

    async def get_memory_context(
        self,
        query: str,
        max_tokens: int = 1000
    ) -> str:
        """
        Get relevant memory context for a query.

        Args:
            query: The query to get context for.
            max_tokens: Maximum number of tokens in the context.

        Returns:
            Concatenated relevant memory content.
        """
        # Search for relevant memories
        memories = await self.search_memories(query, limit=3)
        
        # Combine memory content
        context = "\n\n".join(
            f"Memory {i+1}:\n{mem['metadata']['content']}"
            for i, mem in enumerate(memories)
        )

        # If context is too long, summarize it
        if len(context) > max_tokens * 4:  # Rough estimate of tokens
            context = await summarize_text(context, max_length=max_tokens * 4)

        return context

    async def delete_memory(self, memory_id: int) -> bool:
        """
        Delete a memory by its ID.

        Args:
            memory_id: The ID of the memory to delete.

        Returns:
            True if deletion was successful, False otherwise.
        """
        try:
            self.client.delete(
                collection_name=self.collection_name,
                points_selector=models.PointIdsList(
                    points=[memory_id]
                )
            )
            return True
        except Exception:
            return False

    async def update_memory(
        self,
        memory_id: int,
        content: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Update a memory's content and/or metadata.

        Args:
            memory_id: The ID of the memory to update.
            content: New content for the memory.
            metadata: New metadata for the memory.

        Returns:
            Updated memory information if successful, None otherwise.
        """
        try:
            # Get existing memory
            memory = self.client.retrieve(
                collection_name=self.collection_name,
                ids=[memory_id]
            )[0]

            # Update content and generate new embeddings if needed
            if content:
                embeddings = await get_embeddings(content)
                memory.vector = embeddings[0]
                memory.payload["content"] = content
                memory.payload["summary"] = await summarize_text(content)

            # Update metadata
            if metadata:
                memory.payload.update(metadata)

            # Update in Qdrant
            self.client.upsert(
                collection_name=self.collection_name,
                points=[memory]
            )

            return {
                "id": memory_id,
                "metadata": memory.payload
            }
        except Exception:
            return None