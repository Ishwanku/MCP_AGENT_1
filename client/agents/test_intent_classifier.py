import os
from agents.intent_classifier import classify_intent
from dotenv import load_dotenv

load_dotenv()

def test_intent_classifier():
    queries = [
        "What are my tasks?",
        "Save a new memory: Project meeting.",
        "Hello, how are you?"
    ]
    
    for query in queries:
        print(f"\nTesting query: {query}")
        intent = classify_intent(query)
        print(f"Classified intent: {intent}")

if __name__ == "__main__":
    test_intent_classifier()