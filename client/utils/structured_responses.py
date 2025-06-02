"""
Utility for extracting JSON content from a string.

This module provides a simple function to find and parse a JSON object
embedded within a larger string. It assumes the JSON object is the first
and outermost curly-brace delimited structure.
"""
import json
from typing import Dict, Any, Optional

def extract_json(content: str) -> Optional[Dict[Any, Any]]:
    """
    Extracts a JSON object from a string.

    Searches for the first opening curly brace '{' and the last closing
    curly brace '}' to identify the JSON content. This is a naive
    implementation and might not work for all cases, especially with
    nested or multiple JSON objects not properly delimited.

    Args:
        content: The string potentially containing an embedded JSON object.

    Returns:
        A dictionary parsed from the JSON string, or None if no valid
        JSON object is found or if parsing fails.
    """
    try:
        start_index = content.find("{")
        # Find the corresponding closing brace for the outermost JSON object.
        # This is a simplified approach; a more robust parser would be needed for complex cases.
        # For now, we look for the last closing brace.
        end_index = content.rfind("}")

        if start_index != -1 and end_index != -1 and end_index > start_index:
            json_text = content[start_index : end_index + 1]
            return json.loads(json_text)
        else:
            # No clear JSON structure found based on simple brace matching
            return None
    except json.JSONDecodeError:
        # The identified substring was not valid JSON
        return None
    except Exception:
        # Catch any other unexpected errors during extraction
        return None