"""
Intent classification module for the MCPAgent.

This module uses an LLM (e.g., OpenAI's GPT models or a compatible local model)
to classify a user's query into one of several predefined intents related to
memory, task, or calendar operations. If no specific intent is matched, it defaults
to 'other'.

The `classify_intent` function constructs a prompt for the LLM, sends the query,
and extracts the classified action from the LLM's structured response.
"""
import os
from typing import Dict, Any, Optional
from openai import OpenAI
from utils.structured_responses import extract_json
from dotenv import load_dotenv

load_dotenv() # Load .env variables

# Default model if not specified in environment variables
DEFAULT_MODEL = "gpt-4o-mini"

# Predefined intents that the LLM can classify into
ALLOWED_INTENTS = [
    "save_memory",
    "search_memories",
    "get_all_memories",
    "readTasks",
    "newTask",
    "markTaskAsDone",
    "getEvents",
    "other" # Default for queries not matching other intents
]

def classify_intent(query: str) -> str:
    """
    Classifies the intent of a user's query using an LLM.

    Args:
        query: The user's query string.

    Returns:
        A string representing the classified intent (e.g., "save_memory", "other").
        Returns "other" if classification fails or the LLM response is not as expected.
    """
    # Initialize OpenAI client, explicitly handling Ollama configuration if present

    # Get base URL and API key from environment variables
    # Prioritize OLLAMA_BASE_URL for explicit Ollama setup
    base_url_from_env = os.getenv("OLLAMA_BASE_URL")

    # If OLLAMA_BASE_URL is not set, check OPENAI_BASE_URL (might be used for custom OpenAI-compatible APIs)
    if not base_url_from_env:
        base_url_from_env = os.getenv("OPENAI_BASE_URL")

    openai_api_key = os.getenv("OPENAI_API_KEY")
    model_choice = os.getenv("MODEL", DEFAULT_MODEL)

    print(f"IntentClassifier: Sending query to LLM ('{model_choice}') for intent classification.")

    client: OpenAI

    # Determine if we're connecting to Ollama or standard OpenAI
    if base_url_from_env and "ollama" in base_url_from_env.lower():
        print(f"IntentClassifier: Connecting to Ollama via base URL: {base_url_from_env}")
        # For Ollama, the API key is typically "ollama" or not strictly needed
        client = OpenAI(base_url=base_url_from_env, api_key=openai_api_key or "ollama")
    else:
        print(f"IntentClassifier: Connecting to standard OpenAI API.")
        # For standard OpenAI, the base_url defaults correctly to https://api.openai.com/v1.
        # Only provide base_url if it's explicitly set and NOT an Ollama URL.
        if base_url_from_env: # If OPENAI_BASE_URL was set to something other than Ollama's default
             client = OpenAI(base_url=base_url_from_env, api_key=openai_api_key)
        else: # Standard OpenAI API, no custom base_url needed
             client = OpenAI(api_key=openai_api_key)


    # System prompt to guide the LLM's classification task
    system_prompt = (
        f"You are an expert intent classifier. Classify the user's query into one of the following predefined actions: "
        f"{', '.join(ALLOWED_INTENTS)}. "
        "If the query doesn't fit any specific action, classify it as 'other'."
    )

    # User prompt providing the query and instructions for the LLM's output format
    user_prompt = f"""
Identify the action the user wants to perform in the following query: "{query}"

Allowed actions: {', '.join(ALLOWED_INTENTS)}

Specific instructions:
- If the user mentions completing, finishing, or marking a task as done, select 'markTaskAsDone'.
- For general greetings, questions not related to memory, tasks, or calendar, or if unsure, select 'other'.

Provide your response strictly in the following JSON format inside a ## Response section:

## Justification
<Your step-by-step reasoning for choosing the action. This helps in debugging but will not be parsed by the system.>

## Response
{{"action": "[chosen_action]"}}
"""

    try:
        response = client.chat.completions.create(
            model=model_choice,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            temperature=0.0, # Low temperature for more deterministic classification
        )

        llm_response_content = response.choices[0].message.content
        print(f"IntentClassifier: Raw LLM response: {llm_response_content}")

        # Extract the JSON part from the LLM's response
        extracted_data: Optional[Dict[Any, Any]] = extract_json(llm_response_content)

        if extracted_data and isinstance(extracted_data.get("action"), str) and extracted_data["action"] in ALLOWED_INTENTS:
            classified_action = extracted_data["action"]
            print(f"IntentClassifier: Successfully classified intent as: {classified_action}")
            return classified_action
        else:
            print(f"IntentClassifier: Failed to extract a valid action from LLM response or action not allowed. Defaulting to 'other'. Response: {extracted_data}")
            return "other"

    except Exception as e:
        print(f"IntentClassifier: Error during intent classification with LLM: {e}")
        return "other" # Fallback to 'other' in case of any exception