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
import ollama
from typing import Dict, Any, Optional
from utils.structured_responses import extract_json
from dotenv import load_dotenv

load_dotenv()

DEFAULT_MODEL = "qwen2:7b-instruct"

ALLOWED_INTENTS = [
    "save_memory",
    "search_memories",
    "get_all_memories",
    "readTasks",
    "newTask",
    "markTaskAsDone",
    "getEvents",
    "other"
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
    model_choice = os.getenv("MODEL", DEFAULT_MODEL)
    print(f"IntentClassifier: Sending query to LLM ('{model_choice}') for intent classification.")
    print(f"IntentClassifier: Using Ollama native API.")

    system_prompt = (
        f"You are an expert intent classifier. Classify the user's query into one of the following predefined actions: "
        f"{', '.join(ALLOWED_INTENTS)}. "
        "If the query doesn't fit any specific action, classify it as 'other'."
    )

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
        response = ollama.chat(
            model=model_choice,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            options={"temperature": 0.0},
        )

        llm_response_content = response["message"]["content"]
        print(f"IntentClassifier: Raw LLM response: {llm_response_content}")

        extracted_data = extract_json(llm_response_content)

        if extracted_data and isinstance(extracted_data.get("action"), str) and extracted_data["action"] in ALLOWED_INTENTS:
            classified_action = extracted_data["action"]
            print(f"IntentClassifier: Successfully classified intent as: {classified_action}")
            return classified_action
        else:
            print(f"IntentClassifier: Failed to extract a valid action from LLM response or action not allowed. Response: {extracted_data}")
            return "other"

    except Exception as e:
        print(f"IntentClassifier: Error during intent classification with LLM: {str(e)}")
        return "other"