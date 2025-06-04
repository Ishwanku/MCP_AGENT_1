"""
LLM utility functions for the MCP Agent system.

This module provides utilities for interacting with language models,
including text generation, embeddings, and function calling.
Supports multiple LLM providers through a unified interface.
"""

import json
from typing import Any, Dict, List, Optional, Union
from .llm_providers import get_provider
from ..core.config import settings

# Initialize LLM provider
llm_provider = get_provider()

async def generate_text(
    prompt: str,
    system_message: Optional[str] = None,
    temperature: Optional[float] = None,
    max_tokens: Optional[int] = None,
    functions: Optional[List[Dict[str, Any]]] = None,
) -> Dict[str, Any]:
    """Wrapper for LLM provider's generate_text method."""
    return await llm_provider.generate_text(
        prompt=prompt,
        system_message=system_message,
        temperature=temperature,
        max_tokens=max_tokens,
        functions=functions,
    )

async def get_embeddings(text: Union[str, List[str]]) -> List[List[float]]:
    """Wrapper for LLM provider's get_embeddings method."""
    return await llm_provider.get_embeddings(text)

async def analyze_sentiment(text: str) -> Dict[str, float]:
    """
    Analyze the sentiment of the given text using the LLM.

    Args:
        text: The text to analyze.

    Returns:
        Dictionary containing sentiment scores.
    """
    prompt = f"""Analyze the sentiment of the following text and return a JSON object with scores for:
    - positive (0-1)
    - negative (0-1)
    - neutral (0-1)
    - overall (-1 to 1)

    Text: {text}"""

    response = await generate_text(
        prompt=prompt,
        system_message="You are a sentiment analysis expert. Respond only with valid JSON.",
        temperature=0.3,
    )

    try:
        return json.loads(response["content"])
    except json.JSONDecodeError:
        return {
            "error": "Failed to parse sentiment analysis",
            "raw_response": response["content"],
        }

async def extract_entities(text: str) -> List[Dict[str, str]]:
    """
    Extract named entities from the given text using the LLM.

    Args:
        text: The text to analyze.

    Returns:
        List of dictionaries containing entity information.
    """
    prompt = f"""Extract named entities from the following text and return a JSON array of objects with:
    - text: the entity text
    - type: the entity type (PERSON, ORGANIZATION, LOCATION, etc.)
    - start: the start position in the text
    - end: the end position in the text

    Text: {text}"""

    response = await generate_text(
        prompt=prompt,
        system_message="You are an entity extraction expert. Respond only with valid JSON.",
        temperature=0.3,
    )

    try:
        return json.loads(response["content"])
    except json.JSONDecodeError:
        return [
            {
                "error": "Failed to parse entity extraction",
                "raw_response": response["content"],
            }
        ]

async def summarize_text(text: str, max_length: int = 200) -> str:
    """
    Generate a concise summary of the given text using the LLM.

    Args:
        text: The text to summarize.
        max_length: Maximum length of the summary in characters.

    Returns:
        The generated summary.
    """
    prompt = f"""Summarize the following text in {max_length} characters or less:

    {text}"""

    response = await generate_text(
        prompt=prompt,
        system_message="You are a summarization expert. Provide concise, informative summaries.",
        temperature=0.5,
    )

    return response["content"]

async def classify_text(text: str, categories: List[str]) -> Dict[str, float]:
    """
    Classify text into predefined categories using the LLM.

    Args:
        text: The text to classify.
        categories: List of possible categories.

    Returns:
        Dictionary mapping categories to confidence scores.
    """
    prompt = f"""Classify the following text into these categories and return a JSON object with confidence scores (0-1):
    Categories: {', '.join(categories)}

    Text: {text}"""

    response = await generate_text(
        prompt=prompt,
        system_message="You are a text classification expert. Respond only with valid JSON.",
        temperature=0.3,
    )

    try:
        return json.loads(response["content"])
    except json.JSONDecodeError:
        return {
            "error": "Failed to parse classification",
            "raw_response": response["content"],
        }

async def extract_keywords(text: str, max_keywords: int = 5) -> List[str]:
    """
    Extract key phrases from the text using the LLM.

    Args:
        text: The text to analyze.
        max_keywords: Maximum number of keywords to extract.

    Returns:
        List of extracted keywords.
    """
    prompt = f"""Extract the top {max_keywords} most important keywords or key phrases from the following text.
    Return them as a JSON array of strings:

    Text: {text}"""

    response = await generate_text(
        prompt=prompt,
        system_message="You are a keyword extraction expert. Respond only with valid JSON.",
        temperature=0.3,
    )

    try:
        return json.loads(response["content"])
    except json.JSONDecodeError:
        return []

async def translate_text(text: str, target_language: str) -> str:
    """
    Translate text to the target language using the LLM.

    Args:
        text: The text to translate.
        target_language: The target language code (e.g., 'es', 'fr', 'de').

    Returns:
        The translated text.
    """
    prompt = f"""Translate the following text to {target_language}:

    Text: {text}"""

    response = await generate_text(
        prompt=prompt,
        system_message="You are a professional translator. Provide accurate translations.",
        temperature=0.3,
    )

    return response["content"] 