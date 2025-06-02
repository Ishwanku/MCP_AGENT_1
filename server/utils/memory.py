"""
Utility module for initializing and configuring the Mem0 client.

This module provides a function to get a configured Mem0 client instance.
It reads LLM provider, model choices, and other settings from environment
variables to set up the Mem0 client with a Qdrant vector store.
"""
from mem0 import Memory
import os
from qdrant_client import QdrantClient

def get_mem0_client() -> Memory:
    """
    Initializes and returns a Mem0 client instance.

    The client is configured based on environment variables for LLM provider,
    LLM model, embedding model, and Ollama host. It uses a local Qdrant
    database for vector storage.

    Environment Variables Used:
        LLM_PROVIDER: The provider for the language model (default: "ollama").
        LLM_CHOICE: The specific language model to use (default: "llama3").
        EMBEDDING_MODEL_CHOICE: The embedding model (default: "nomic-embed-text").
        OLLAMA_HOST: The base URL for the Ollama API (default: "http://localhost:11434").

    Returns:
        An initialized Mem0 Memory instance.
    """
    # Retrieve LLM and embedding model configurations from environment variables
    llm_provider = os.getenv("LLM_PROVIDER", "ollama")
    llm_model = os.getenv("LLM_CHOICE", "llama3")
    embedding_model = os.getenv("EMBEDDING_MODEL_CHOICE", "nomic-embed-text")
    ollama_host = os.getenv("OLLAMA_HOST", "http://localhost:11434")

    # Initialize Qdrant client for vector storage
    # Assumes Qdrant is running and accessible.
    qdrant_db_path = os.getenv("QDRANT_DB_PATH", "./qdrant_db")
    print(f"Mem0/Qdrant: Using database path: {qdrant_db_path}")
    qdrant_client = QdrantClient(path=qdrant_db_path)

    # Configuration dictionary for Mem0
    config = {
        "llm": {
            "provider": llm_provider,
            "config": {
                "model": llm_model,
                "temperature": 0.2,       # Controls randomness of LLM responses
                "max_tokens": 2000,       # Maximum number of tokens in LLM response
                "api_base": ollama_host   # Base URL for Ollama API if used
            }
        },
        "embedder": {
            "provider": llm_provider, # Assumes embedder uses same provider as LLM
            "config": {
                "model": embedding_model,
                "embedding_dims": 768   # Dimensionality of the embedding vectors (e.g., nomic-embed-text is 768). Adjust if using a different model.
            }
        },
        "vector_store": {
            "provider": "qdrant",
            "config": {
                "collection_name": "mem0_memories", # Name of the collection in Qdrant
                "client": qdrant_client           # The initialized Qdrant client
            }
        }
    }

    # Create and return Memory instance from the configuration
    return Memory.from_config(config)