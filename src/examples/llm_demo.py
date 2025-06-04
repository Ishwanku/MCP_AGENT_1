"""
Example script demonstrating the LLM capabilities of the MCP Agent system.

This script shows how to use various LLM features including:
- Text generation
- Sentiment analysis
- Entity extraction
- Text summarization
- Text classification
- Keyword extraction
- Translation
"""

import asyncio
import json
from typing import List
from mcp.utils.llm_utils import (
    generate_text,
    analyze_sentiment,
    extract_entities,
    summarize_text,
    classify_text,
    extract_keywords,
    translate_text,
)

async def demonstrate_text_generation():
    """Demonstrate basic text generation."""
    print("\n=== Text Generation ===")
    prompt = "Explain quantum computing in simple terms."
    response = await generate_text(
        prompt=prompt,
        system_message="You are a helpful science educator.",
        temperature=0.7
    )
    print(f"Prompt: {prompt}")
    print(f"Response: {response['content']}")

async def demonstrate_sentiment_analysis():
    """Demonstrate sentiment analysis."""
    print("\n=== Sentiment Analysis ===")
    texts = [
        "I'm really happy with the results!",
        "This is the worst experience ever.",
        "The weather is okay today."
    ]
    for text in texts:
        sentiment = await analyze_sentiment(text)
        print(f"\nText: {text}")
        print(f"Sentiment: {json.dumps(sentiment, indent=2)}")

async def demonstrate_entity_extraction():
    """Demonstrate entity extraction."""
    print("\n=== Entity Extraction ===")
    text = "Apple CEO Tim Cook announced new products at their headquarters in Cupertino, California."
    entities = await extract_entities(text)
    print(f"Text: {text}")
    print(f"Entities: {json.dumps(entities, indent=2)}")

async def demonstrate_summarization():
    """Demonstrate text summarization."""
    print("\n=== Text Summarization ===")
    text = """
    Artificial Intelligence (AI) is transforming industries across the globe. 
    From healthcare to finance, AI applications are becoming increasingly sophisticated. 
    Machine learning algorithms can now predict diseases, optimize financial portfolios, 
    and even create art. However, this rapid advancement also raises important ethical 
    questions about privacy, bias, and job displacement. Companies and governments must 
    work together to ensure AI development benefits society while minimizing potential risks.
    """
    summary = await summarize_text(text, max_length=100)
    print(f"Original text: {text}")
    print(f"Summary: {summary}")

async def demonstrate_classification():
    """Demonstrate text classification."""
    print("\n=== Text Classification ===")
    text = "The new smartphone features a 6.5-inch display and 5G connectivity."
    categories = ["Technology", "Sports", "Politics", "Entertainment", "Science"]
    classification = await classify_text(text, categories)
    print(f"Text: {text}")
    print(f"Classification: {json.dumps(classification, indent=2)}")

async def demonstrate_keyword_extraction():
    """Demonstrate keyword extraction."""
    print("\n=== Keyword Extraction ===")
    text = """
    The global climate crisis requires immediate action. Rising temperatures, 
    extreme weather events, and melting ice caps are clear indicators of climate change. 
    Renewable energy sources like solar and wind power offer sustainable solutions.
    """
    keywords = await extract_keywords(text, max_keywords=5)
    print(f"Text: {text}")
    print(f"Keywords: {json.dumps(keywords, indent=2)}")

async def demonstrate_translation():
    """Demonstrate text translation."""
    print("\n=== Translation ===")
    text = "Hello, how are you today?"
    translations = {
        "Spanish": await translate_text(text, "es"),
        "French": await translate_text(text, "fr"),
        "German": await translate_text(text, "de")
    }
    print(f"Original: {text}")
    for language, translation in translations.items():
        print(f"{language}: {translation}")

async def main():
    """Run all demonstrations."""
    print("Starting LLM Capabilities Demonstration...")
    
    # Run all demonstrations
    await demonstrate_text_generation()
    await demonstrate_sentiment_analysis()
    await demonstrate_entity_extraction()
    await demonstrate_summarization()
    await demonstrate_classification()
    await demonstrate_keyword_extraction()
    await demonstrate_translation()
    
    print("\nDemonstration complete!")

if __name__ == "__main__":
    asyncio.run(main()) 